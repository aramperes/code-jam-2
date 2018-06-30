from rethinkdb import ReqlNonExistenceError
from werkzeug.exceptions import NotFound, Unauthorized

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class StoryResource(BaseResource):
    name = "api.stories.story"
    url = "/story/<string:story_id>"

    @oauth(force=False)
    def get(self, story_id):
        try:
            story_query = self.db.query("stories").get(story_id).pluck("user_id", "public", "sentences", "media_type")
            story = self.db.run(story_query)
        except ReqlNonExistenceError:
            raise NotFound()

        is_own = self.authenticated and story["user_id"] == self.user_data["id"]
        if not story["public"] and not is_own:
            raise Unauthorized("The story you requested has been marked as private by its author.")

        author = self.db.get_doc("users", story["user_id"])["username"]
        return {
            "id": story_id,
            "public": story["public"],
            "sentences": story["sentences"],
            "author": author,
            "url": "/story/{0}".format(story_id),
            "media": "/story/{0}/play".format(story_id),
            "media_type": story["media_type"]
        }

    @oauth(force=True)
    def delete(self, story_id):
        try:
            story_query = self.db.query("stories").get(story_id).pluck("user_id")
            story = self.db.run(story_query)
        except ReqlNonExistenceError:
            raise NotFound()

        if story["user_id"] != self.user_data["id"]:
            raise Unauthorized()

        delete_query = self.db.query("stories").get(story_id).delete()
        self.db.run(delete_query)
        return {
            "success": True
        }
