import rethinkdb
from flask import request
from werkzeug.exceptions import BadRequest

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

    @oauth(force=True)
    def post(self):
        data = request.json or {}

        if "id" not in data:
            raise BadRequest("Challenge's 'id' field is required.")

        active_game = self.db.run(
            self.db.query("games").filter(
                (rethinkdb.row["defender_username"] == self.user_data['username']) |
                (rethinkdb.row["challenger_username"] == self.user_data['username'])
            ).coerce_to("array")
        )

        for game_entry in active_game:
            if not game_entry['won']:
                raise BadRequest(description="You are already in a live game!")

        challenge_doc = self.db.get_doc("challenges", data['id'])
        if not challenge_doc:
            raise BadRequest(description="This challenge does not exist!")

        if challenge_doc["defender_username"] != self.user_data["username"]:
            raise BadRequest(description="This challenge is not directed towards you!")

        try:
            if not bool(data["accept"]):
                self.db.run(self.db.query("challenges").get(data["id"]).delete())
                return {'success': True}
        except ValueError:
            raise BadRequest(description="'accept' field must be a boolean.")

        char_challenger = self.db.get_all("characters", challenge_doc['challenger_character'], index="name")[0]
        char_defender = self.db.get_all("characters", data['character'], index="name")
        if not char_defender:
            raise BadRequest(description="Unknown character: {0}".format(data["character"]))
        char_defender = char_defender[0]

        try:
            # All the checks succeeded and they accepted the challenge, so let's set up a document.
            document = {
                "challenger_username": str(challenge_doc["challenger_username"]),
                "challenger_character": str(challenge_doc["challenger_character"]),
                "defender_username": str(challenge_doc["defender_username"]),
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
                "max_turns": int(challenge_doc["max_turns"]),
                "turn": str(self.user_data["username"]),
                "won": None
            }
        except ValueError:
            raise BadRequest(description="Your character must exist!")

        # Everything checks out, so let's add their character to the database.
        # We have to create a query to the table we want to insert a document into
        insert_query = self.db.query("games").insert(document)
        # Run the query in the database
        result = self.db.run(insert_query)
        # Delete the challenge now that we've accepted it
        self.db.run(self.db.query("challenges").get(data["id"]).delete())

        return {'success': True, "game_id": result["generated_keys"][0]}
