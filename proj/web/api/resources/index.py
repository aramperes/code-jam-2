from proj.web.api.base_resource import BaseResource


class IndexResource(BaseResource):
    """
    The index endpoint (/).
    """
    url = "/"
    name = "index"

    def get(self):
        # list all available resources
        resources = []
        for resource in self.web_app.api.resources:
            resource = resource[0]
            data = {
                "name": resource.name,
                "url": resource.url,
                "methods": list(resource.methods)
            }
            resources.append(data)
        return {
            "resources": resources
        }
