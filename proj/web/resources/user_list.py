from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class UserListResource(BaseResource):
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

            main_query = self.db.get_all("games", user, "challenger_username")

            if main_query["challenger_username"]:
                final_data[user] = {
                    "current_game": main_query["id"],
                    "current_role": "challenger"
                }
                continue


            secondary_query = self.db.get_all("games", user, "defender_username")

            if main_query["defender_username"]:
                final_data[user] = {
                    "current_game": main_query["id"],
                    "current_role": "defender"
                }

            final_data[user] = {
                "current_game": "none"
                "current_role": "none"
            }


        return final_data
