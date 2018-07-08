import bcrypt
from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from proj.web.api.base_resource import BaseResource


class RegisterResource(BaseResource):
    """
    The register endpoint (/auth/register).
    """
    url = "/auth/register"
    name = "api.auth.register"

    def post(self):
        data = request.json or {}
        if 'username' not in data or 'password' not in data:
            raise BadRequest(description="Provide a username and a password to register.")

        # Makes sure the input credentials are strings
        username = str(data["username"])
        password = str(data["password"])

        # First, let's check if the username is already taken
        # To do that, we want to check if there is already a document with that username inside it.
        # So, we want to count how many users have that username. If not 0, then someone is already taking it.
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
