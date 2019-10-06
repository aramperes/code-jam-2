from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from proj.web.api.base_resource import BaseResource
from proj.web.api.oauth import oauth


class ChallengeResource(BaseResource):
    """
    Used to challenge another user to a game.
    Required data:
    {
    "defender": string,
    "challenge_config": {
            "max_turns": int,
            "character": string
        }
    }
    This route requires OAuth2 authentication.
    """
    url = "/game/challenge"
    name = "game.challenge"

    @oauth(force=True)
    def post(self):
        data = request.json or {}

        # Check to make sure all data is correct and workable.
        if "defender" not in data or "challenge_config" not in data:
            raise BadRequest(description="You must provide all required fields.")

        if "max_turns" not in data["challenge_config"] or "character" not in data["challenge_config"]:
            raise BadRequest(description="You must provide all required fields in challenge config.")

        if str(data["defender"]) == self.user_data["username"]:
            raise BadRequest(description="You cannot challenge yourself.")

        defender = self.db.get_all("users", data['defender'], index="username", limit=1)
        if not defender:  # Does the defender exist in the database?
            raise BadRequest(description="Defender does not exist in database.")

        character = self.db.get_all("characters", data['challenge_config']['character'], index="name", limit=1)
        if not character:  # Does the character exist in the database?
            raise BadRequest(description="Character does not exist.")
        character = character[0]

        if character["owner"] != self.user_data["username"]:
            raise Unauthorized(description="Character does not belong to you.")

        # All the checks passed, let's set up a document to insert into the database.
        challenge_data = {
            "challenger_username": str(self.user_data["username"]),
            "defender_username": str(data["defender"]),
            "challenger_character": str(data['challenge_config']["character"]),
            "max_turns": str(data['challenge_config']["max_turns"])
        }

        # Everything checks out, so let's add their challenge to the database.
        # We have to create a query to the table we want to insert a document into
        insert_query = self.db.query("challenges").insert(challenge_data)
        # Run the query in the database
        result = self.db.run(insert_query)

        return {"success": True, "challenge_id": result["generated_keys"][0]}
