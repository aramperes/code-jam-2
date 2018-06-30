from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class ListOwnStoriesResource(BaseResource):
    name = "api.stories.list.own"
    url = "/stories"

    @oauth(force=True)
    def get(self):
        user_id = self.user_data["id"]
        # get the user's stories
        stories_query = self.db.query("stories").get_all(
            user_id, index="user_id").pluck("id", "public", "sentences").coerce_to("array")
        stories = self.db.run(stories_query)
        for story in stories:
            story["media"] = "/story/{0}/play".format(story["id"])
            story["url"] = "/story/{0}".format(story["id"])
        return stories
