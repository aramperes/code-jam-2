from proj.web.base_resource import BaseResource


class IndexResource(BaseResource):
    url = "/"
    name = "api.index"

    def get(self):
        return {}