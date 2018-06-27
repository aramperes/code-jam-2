from proj.web.base_resource import BaseResource
from flask import jsonify, request
import bcrypt


class LoginResource(BaseResource):
    """
    The login endpoint (/login).
    """
    url = "/login"
    name = "api.login"

    def post(self):
        data = request.json or {}

        if not data:
            resp = {'success': False, 'reason': 'enter a username and password'}
            return jsonify(resp)

        user_by_username_query = self.db.query("users").filter(
            {
                "username": data.get('username')
            }
        ).coerce_to("array")
        users = self.db.run(user_by_username_query)

        if not users:  # this checks if the users array is empty
            resp = {'success': False, 'reason': 'No user found. Use the /register endpoint to register for an account.'}
            return jsonify(resp)

        user_document = users[0]
        password_hash = user_document["password_hash"]

        if bcrypt.checkpw(data.get('password'), password_hash):
            resp = {'success': True}
            # create id param for game room
            return jsonify(resp)
        else:
            resp = {'success': False, 'reason': 'Incorrect password.'}
            return jsonify(resp)
