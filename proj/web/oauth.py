import datetime
import secrets
from functools import wraps

import rethinkdb
from flask import request
from werkzeug.exceptions import NotFound, Unauthorized

TIME_ZONE_UTC = rethinkdb.make_timezone("+00:00")
ACCESS_TOKEN_LENGTH = 32
ACCESS_TOKEN_EXPIRATION = datetime.timedelta(hours=1)
REFRESH_TOKEN_LENGTH = 64


class OAuthAccessToken:
    def __init__(self, user_id: str):
        """
        Generates an access token
        """
        self.user_id = user_id
        self.token = secrets.token_urlsafe(ACCESS_TOKEN_LENGTH)
        self.token_expiration = datetime.datetime.now(TIME_ZONE_UTC) + ACCESS_TOKEN_EXPIRATION


class OAuthRefreshToken:
    def __init__(self, user_id: str):
        """
        Generates a refresh token
        """
        self.user_id = user_id
        self.token = secrets.token_urlsafe(REFRESH_TOKEN_LENGTH)


def oauth(force):
    """
    Verifies that the API request is authenticated, and queries the authenticated user.
    This decorator wraps around REST method handlers (get, post, put, etc.)
    :param force: if True, the request will be aborted if authentication fails; if False, the request will continue.
    """

    def wrapper(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            self.authenticated = False
            self.user_data = None
            headers = dict(request.headers)
            if "Authorization" not in headers:
                if force:
                    raise Unauthorized(description="This resource requires authentication.")
                else:
                    return f(self, *args, **kwargs)

            auth_header = headers["Authorization"].split(" ", maxsplit=1)
            if len(auth_header) is not 2 or auth_header[0] != "Bearer":
                if force:
                    raise Unauthorized(description="Invalid Authorization header.")
                else:
                    return f(self, *args, **kwargs)

            bearer_token = auth_header[1]
            # Check if the token exists
            token_doc = self.db.get_doc("oauth_tokens", bearer_token)
            if not token_doc:
                if force:
                    raise Unauthorized(description="Invalid access token.")
                else:
                    return f(self, *args, **kwargs)

            # Check if the token is expired
            expiration: datetime.datetime = token_doc["expires"]
            if expiration < datetime.datetime.now(expiration.tzinfo):
                if force:
                    raise Unauthorized(
                        description="The provided access token is expired."
                                    "Use the /auth/refresh route with a refresh token to get a new access token.")
                else:
                    return f(self, *args, **kwargs)

            user_id = token_doc["user_id"]
            self.user_data = self.db.get_doc("users", user_id)
            if not self.user_data:
                raise NotFound()

            # All is good
            self.authenticated = True
            return f(self, *args, **kwargs)

        return inner

    return wrapper
