from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class UserResource(BaseResource):
    """
    Gets the information about the current logged-in user.
    This route requires OAuth2 authentication.
    """
    url = "/me"
    name = "api.user.me"

    @oauth(force=True)
    def get(self):
        return {
            "username": self.user_data["username"],
            "id": self.user_data["id"]
        }
