from werkzeug.exceptions import NotFound

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class ListUserStoriesResource(BaseResource):
    name = "api.stories.list.user"
    url = "/stories/user/<string:username>"

    @oauth(force=False)
    def get(self, username):
        # check if the user exists
        user_list = self.db.get_all("users", username, index="username", limit=1)
        if not user_list:
            raise NotFound()
        user = user_list[0]

        is_self = self.authenticated and user["id"] == self.user_data["id"]
        stories_query = self.db.query("stories").get_all(
            user["id"], index="user_id").filter({"public": None if is_self else True}).pluck(
            "id", "public", "sentences").coerce_to("array")
        stories = self.db.run(stories_query)
        for story in stories:
            story["media"] = "/story/{0}/play".format(story["id"])
            story["url"] = "/story/{0}".format(story["id"])
        return stories
