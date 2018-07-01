import rethinkdb
from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth

class ChallengeDecisionResource(BaseResource):
    """
    Used to challenge another user to a game.
    Required data:
    {
    "id": string
    "accept": boolean
    # OPTIONAL KEYS BELOW
    "character": string
    }
    This route requires OAuth2 authentication.
    """
    url = "/game/challenge/decide"
    name = "api.game.challenge.decide"

    @oauth
    def post(self):
        
        data = request.json or {}
        active_game = self.db.query("games").filter(
            (rethinkdb.row["defender_username"] == self.user_data['username']) | 
            (rethinkdb.row["challenger_username"] == self.user_data['username'])
        ).coerce_to("array")

        try:
            if self.db.get_doc("challenges", data['id'])["defender_username"] != self.user_data["username"]:
                return BadRequest(description="This challenge is not directed towards you!")
        except ValueError:
            return BadRequest(description="This challenge does not exist!")

        try:
            if not bool(data["accept"]):
                self.db.run(self.db.query("challenges").get(data["id"]).delete())
                return {'success': True}
        except ValueError:
            return BadRequest(description="accept must be a boolean")

        if active_game:
            for game_entry in active_game:
                if not game_entry['won']:
                    return Unauthorized(description="A game is already in progress!")

        try:
            # All the checks succeeded and they accepted the challenge, so let's set up a document.
            info = self.db.get_doc("challenges", data['id'])
            char_challenger = self.db.get_doc("challenges", info['challenger_character'])
            char_defender = self.db.get_doc("characters", data['character'])
            document = {
                "challenger_username": str(info["challenger_username"]),
                "challenger_character": str(info["challenger_character"]),
                "defender_username": str(info["defender"]),
                "defender_character": str(data["character"]),
                "challenger_stats": {
                    "strength": int(char_challenger["strength"]),
                    "dexterity": int(char_challenger["dexterity"]),
                    "health": int(char_challenger["health"]),
                    "special": str(char_challenger["special"])
                },
                "defender_stats": {
                    "strength": int(char_defender["strength"]),
                    "dexterity": int(char_defender["dexterity"]),
                    "health": int(char_defender["health"]),
                    "special": str(char_defender["special"])
                },
                "turn_number": 1,
                "max_turns": int(info["max_turns"])
                "turn": str(self.user_data["username"])
                "won": None
            }
        except ValueError:
            BadRequest(description="Your character must exist!")

        # Everything checks out, so let's add their character to the database.
        # We have to create a query to the table we want to insert a document into
        insert_query = self.db.query("characters").insert(document)
        # Run the query in the database
        self.db.run(insert_query)
        # Delete the challenge now that we've accepted it
        self.db.run(self.db.query("challenges").get(data["id"]).delete())

        return {'success': True}
