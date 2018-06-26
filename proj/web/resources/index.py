from proj.web.base_resource import BaseResource


class IndexResource(BaseResource):
    """
    The index endpoint (/).
    """
    url = "/"
    name = "api.index"

    def get(self):
        return {}
