from flask import make_response
from rethinkdb import ReqlNonExistenceError
from werkzeug.exceptions import NotFound

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class PlayStoryResource(BaseResource):
    name = "api.stories.play"
    url = "/story/<string:story_id>/play"

    @oauth(force=False)
    def get(self, story_id):
        # Find the story in the database
        try:
            story_query = self.db.query("stories").get(story_id).pluck("user_id", "public", "media")
            story = self.db.run(story_query)
        except ReqlNonExistenceError:
            raise NotFound()

        media = story["media"]

        response = make_response(media)
        response.headers["Content-Type"] = "audio/mpeg"

        return response
