from flask import request
from werkzeug.exceptions import BadRequest

from proj.web.api.base_resource import BaseResource


class ExploreStoriesResource(BaseResource):
    name = "api.stories.explore"
    url = "/stories/explore"

    def get(self):
        # Optional GET parameter: max (default = 5, max = 10)
        # Find some stories in the database
        param_max = request.args.get("max", default=5, type=int)
        if not 10 >= param_max >= 0:
            raise BadRequest(description="'max' arg must be between 0 and 10, inclusively.")

        stories_query = self.db.query("stories").filter({"public": True}).sample(param_max).pluck(
            "id", "public", "sentences", "user_id", "media_type").coerce_to("array")
        stories = self.db.run(stories_query)
        for story in stories:
            author = self.db.get_doc("users", story["user_id"])["username"]
            story["author"] = author
            story["media"] = "/story/{0}/play".format(story["id"])
            story["url"] = "/story/{0}".format(story["id"])

        return stories
