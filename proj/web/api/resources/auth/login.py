import bcrypt
from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from proj.web.api.base_resource import BaseResource
from proj.web.api.oauth import OAuthAccessToken, OAuthRefreshToken


class LoginResource(BaseResource):
    """
    The login endpoint (/auth/login).
    """
    url = "/auth/login"
    name = "auth.login"

    def post(self):
        data = request.json or {}
        if 'username' not in data or 'password' not in data:
            raise BadRequest(description="Provide a username and a password to login.")

        # Makes sure the input credentials are strings
        username = str(data["username"])
        password = str(data["password"])

        # Check if the username exists
        users = self.db.get_all("users", username, index="username")
        if not users:  # this checks if the users array is empty
            raise Unauthorized(description="Unknown username. Use the /register endpoint to create an account.")

        user_document = users[0]
        password_hash = user_document["password_hash"]

        if not bcrypt.checkpw(password.encode(), password_hash.encode()):
            raise Unauthorized(description="Incorrect username or password.")

        # Create an OAuth2 Bearer
        user_id = user_document["id"]
        access_token = OAuthAccessToken(user_id)

        # Insert token into the database
        token_document = {
            "token": access_token.token,
            "user_id": user_id,
            "expires": access_token.token_expiration
        }
        insert_token_query = self.db.query("oauth_tokens").insert(token_document)
        self.db.run(insert_token_query)

        # Create an OAuth2 Refresh Token
        refresh_token = OAuthRefreshToken(user_id)

        # Insert the refresh token into the database
        refresh_token_document = {
            "refresh_token": refresh_token.token,
            "user_id": user_id
        }
        insert_refresh_token_query = self.db.query("oauth_refresh_tokens").insert(refresh_token_document)
        self.db.run(insert_refresh_token_query)

        # Send the OAuth information to the client
        return {
            "token_type": "bearer",
            "access_token": access_token.token,
            "refresh_token": refresh_token.token,
            "expires": int(access_token.token_expiration.timestamp())
        }
