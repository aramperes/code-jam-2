from proj.web.api.base_resource import BaseResource


class DebugConfigResource(BaseResource):
    """
    A debug resource to output the YAML configuration.
    Note: this resource is only accessible if the `debug` flag is set to `true` in the YAML configuration.
    """
    url = "/debug/config"
    name = "debug.config"

    def get(self):
        return self.web_app.config.get()
