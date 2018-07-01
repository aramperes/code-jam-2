import rethinkdb

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
        challenges_off = self.db.query("challenges").filter({"challenger_username": self.user_data["username"]}).coerce_to("array")
        challenges_def = self.db.query("challenges").filter({"defender_username": self.user_data["username"]}).coerce_to("array")

        active_game = self.db.query("games").filter(
            (rethinkdb.row["defender_username"] == self.user_data['username']) | 
            (rethinkdb.row["challenger_username"] == self.user_data['username'])
        ).coerce_to("array")
        game = self.db.run(active_game)
        playing_game = None

        for game_entry in game:
            if not game_entry["won"]:
                playing_game = game_entry

        return {
            "username": self.user_data["username"],
            "id": self.user_data["id"],
            "active_challenger_games": self.db.run(challenges_off),
            "active_defender_games": self.db.run(challenges_def),
            "active_game": playing_game
        }
