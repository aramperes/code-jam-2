from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from proj.web.api.base_resource import BaseResource
from proj.web.api.oauth import OAuthAccessToken


class RefreshTokenResource(BaseResource):
    """
    The endpoint to create new OAuth access tokens from refresh tokens. (/auth/refresh)
    """
    url = "/auth/refresh"
    name = "auth.refresh"

    def post(self):
        data = request.json or {}
        if "refresh_token" not in data:
            raise BadRequest(description="The 'refresh_token' field is required.")

        refresh_token = data["refresh_token"]
        token_doc = self.db.get_doc("oauth_refresh_tokens", refresh_token)
        if not token_doc:
            raise Unauthorized(description="Unknown refresh token.")

        user_id = token_doc["user_id"]
        # Create a new OAuth Access Token
        access_token = OAuthAccessToken(user_id)

        # Insert token into the database
        token_document = {
            "token": access_token.token,
            "user_id": user_id,
            "expires": access_token.token_expiration
        }
        insert_token_query = self.db.query("oauth_tokens").insert(token_document)
        self.db.run(insert_token_query)

        # Send the OAuth information to the client
        return {
            "token_type": "bearer",
            "access_token": access_token.token,
            "refresh_token": refresh_token,
            "expires": int(access_token.token_expiration.timestamp())
        }
