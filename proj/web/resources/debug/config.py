from proj.web.base_resource import BaseResource


class DebugConfigResource(BaseResource):
    url = "/debug/config"
    name = "api.debug.config"

    def get(self):
        return self.web_app.config.config
