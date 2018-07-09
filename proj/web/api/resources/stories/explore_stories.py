from flask import request
from werkzeug.exceptions import BadRequest

from proj.web.api.base_resource import BaseResource
from proj.web.api.resources.stories.list_common import sample_stories


class ExploreStoriesResource(BaseResource):
    name = "stories.explore"
    url = "/stories/explore"

    def get(self):
        # Optional GET parameter: max (default = 5, max = 10)
        # Find some stories in the database
        param_max = request.args.get("max", default=5, type=int)
        if not 10 >= param_max >= 0:
            raise BadRequest(description="'max' arg must be between 0 and 10, inclusively.")

        return sample_stories(self, param_max, "summary" in request.args)
