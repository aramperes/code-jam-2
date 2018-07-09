from flask import request

from proj.web.api.base_resource import BaseResource
from proj.web.api.oauth import oauth
from proj.web.api.resources.stories.list_common import list_stories


class ListOwnStoriesResource(BaseResource):
    name = "stories.list.own"
    url = "/stories"

    @oauth(force=True)
    def get(self):
        user_id = self.user_data["id"]
        summary_mode = "summary" in request.args

        # get the user's stories
        return list_stories(self, user_id, True, summary_mode)
