import bcrypt
from flask import request

from proj.web.base_resource import BaseResource


class LoginResource(BaseResource):
    """
    The login endpoint (/login).
    """
    url = "/login"
    name = "api.login"

    def post(self):
        data = request.json or {}
        if 'username' not in data or 'password' not in data:
            return {'success': False, 'reason': 'Provide a username and password'}

        # Makes sure the input credentials are strings
        username = str(data["username"])
        password = str(data["password"])

        # Check if the username exists
        users = self.db.get_all("users", username, index="username")
        if not users:  # this checks if the users array is empty
            return {'success': False, 'reason': 'Unknown username. Use the /register endpoint to create an account.'}

        user_document = users[0]
        password_hash = user_document["password_hash"]

        if bcrypt.checkpw(password.encode(), password_hash.encode()):
            return {'success': True}
        else:
            return {'success': False, 'reason': 'Incorrect password.'}
