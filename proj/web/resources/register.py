from proj.web.base_resource import BaseResource
from flask import request
import bcrypt


class RegisterResource(BaseResource):
    """
    The register endpoint (/register).
    """
    url = "/register"
    name = "api.register"

    def post(self):
        data = request.json or {}
        if 'username' not in data or 'password' not in data:
            return {'success': False, 'reason': 'Enter a username and a password.'}

        # The dictionary (document) to insert in the database
        user_info = {
            'username': data.get('username'),
            'password_hash': bcrypt.hashpw(data.get('password').encode(), bcrypt.gensalt()).decode()
        }

        # First, let's check if the username is already taken
        # To do that, we want to check if there is already a document with that username inside it.
        # So, we want to count how many users have that username. If not 0, then someone is already taking it.
        check_user_query = self.db.query("users").filter(
            {
                "username": user_info['username']
            }
        ).count()

        # Run the query
        username_taken = self.db.run(check_user_query) > 0
        if username_taken:
            # There are more than 0 users with that username, so it must be taken.
            return {'success': False, 'reason': 'Username already taken.'}

        # The username isn't taken, so let's add the user.
        # We have to create a query to the table we want to insert a document into
        insert_query = self.db.query("users").insert(user_info)
        # Run the query in the database
        self.db.run(insert_query)

        return {'success': True}
