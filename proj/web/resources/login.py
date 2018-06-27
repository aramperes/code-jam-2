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
            return {'success': False, 'reason': 'enter a username and password'}

        user_by_username_query = self.db.query("users").filter(
            {
                "username": data.get('username')
            }
        ).coerce_to("array")
        users = self.db.run(user_by_username_query)

        if not users:  # this checks if the users array is empty
            return {'success': False, 'reason': 'No user found. Use the /register endpoint to register for an account.'}

        user_document = users[0]
        password_hash = user_document["password_hash"]

        if bcrypt.checkpw(data.get('password').encode(), password_hash.encode()):
            # create id param for game room
            return {'success': True}
        else:
            return {'success': False, 'reason': 'Incorrect password.'}
