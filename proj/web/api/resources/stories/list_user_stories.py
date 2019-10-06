from flask import request
from werkzeug.exceptions import NotFound

from proj.web.api.base_resource import BaseResource
from proj.web.api.oauth import oauth
from proj.web.api.resources.stories.list_common import list_stories


class ListUserStoriesResource(BaseResource):
    name = "stories.list.user"
    url = "/stories/user/<string:username>"

    @oauth(force=False)
    def get(self, username):
        # check if the user exists
        user_list = self.db.get_all("users", username, index="username", limit=1)
        if not user_list:
            raise NotFound()
        user = user_list[0]

        is_self = self.authenticated and user["id"] == self.user_data["id"]

        summary_mode = "summary" in request.args

        # get the user's stories
        return list_stories(self, user["id"], is_self, summary_mode)
