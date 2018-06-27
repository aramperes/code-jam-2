from proj.web.base_resource import BaseResource


class ParamDemoResource(BaseResource):
    url = "/something/<string:id>"
    name = "api.param_demo"

    def get(self, id):
        # The 'id' parameter is a string, as defined in the URL
        # So, accessing /something/abc would return { input_id: "abc" }
        return {
            "input_id": id
        }
