from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class UserResource(BaseResource):
    """
    Gets information about all users.
    This route requires OAuth2 authentication.
    """
    url = "/user/list"
    name = "api.user.list"

    @oauth
    def get(self):
        final_data = {}
        user_query = self.db.query('users').pluck('username').coerce_to('array')

        for user in self.db.run(user_query):

            if self.db.get_all("games", user, "challenger_username"):
                final_data[user] = "In a game (challenger)"
                continue

            elif self.db.get_all("games", user, "defender_username"):
                final_data[user] = "In a game (defender)"
                continue

            final_data[user] = "Not in a game"


        return final_data
