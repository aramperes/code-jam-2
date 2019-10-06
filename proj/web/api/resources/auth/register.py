import re

import bcrypt
from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from proj.web.api.base_resource import BaseResource

USERNAME_REGEX = re.compile(r"^([0-9a-zA-Z_]+$)")
USERNAME_LENGTH_MIN = 4
USERNAME_LENGTH_MAX = 12

PASSWORD_LENGTH_MIN = 2
PASSWORD_LENGTH_MAX = 64


class RegisterResource(BaseResource):
    """
    The register endpoint (/auth/register).
    """
    url = "/auth/register"
    name = "auth.register"

    def post(self):
        data = request.json or {}
        if 'username' not in data or 'password' not in data:
            raise BadRequest(description="Provide a username and a password to register.")

        # Makes sure the input credentials are strings
        username = str(data["username"])
        password = str(data["password"])

        # Check if the username and password are valid
        if not (USERNAME_LENGTH_MIN <= len(username) <= USERNAME_LENGTH_MAX):
            raise BadRequest(description=f"Username must be between {USERNAME_LENGTH_MIN}"
                                         f" and {USERNAME_LENGTH_MAX} characters long.")
        if not USERNAME_REGEX.fullmatch(username):
            raise BadRequest(description="Username contains illegal characters.")

        if not (PASSWORD_LENGTH_MIN <= len(password) <= PASSWORD_LENGTH_MAX):
            raise BadRequest(description=f"Password must be between {PASSWORD_LENGTH_MIN}"
                                         f" and {PASSWORD_LENGTH_MAX} characters long.")

        # Check if the username is taken
        users = self.db.get_all("users", username, index="username", limit=1)
        username_taken = len(users) > 0
        if username_taken:
            # There are more than 0 users with that username, so it must be taken.
            raise Unauthorized(description="Username is already taken.")

        # The dictionary (document) to insert in the database
        user_info = {
            'username': username,
            'password_hash': bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        }

        # The username isn't taken, so let's add the user.
        # We have to create a query to the table we want to insert a document into
        insert_query = self.db.query("users").insert(user_info)
        # Run the query in the database
        self.db.run(insert_query)

        return {'success': True}
