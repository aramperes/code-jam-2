from flask import make_response
from rethinkdb import ReqlNonExistenceError
from werkzeug.exceptions import NotFound, Unauthorized

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class PlayStoryResource(BaseResource):
    name = "api.stories.play"
    url = "/story/<string:story_id>/play"

    @oauth(force=False)
    def get(self, story_id):
        # Find the story in the database
        try:
            story_query = self.db.query("stories").get(story_id).pluck("user_id", "public", "media", "media_type")
            story = self.db.run(story_query)
        except ReqlNonExistenceError:
            raise NotFound()

        is_own = self.authenticated and story["user_id"] == self.user_data["id"]
        if not story["public"] and not is_own:
            raise Unauthorized("The story you requested has been marked as private by its author.")

        response = make_response(story["media"])
        response.headers["Content-Type"] = story["media_type"]

        return response
