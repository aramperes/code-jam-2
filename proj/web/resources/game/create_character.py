from flask import request
from werkzeug.exceptions import BadRequest

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class CreateCharacterResource(BaseResource):
    """
    Used to create a character. Format is:
    {
        "name": string,
        "description": string,
        "strength": int,
        "dexterity": int,
        "health": int,
        "special": string
    }
    This route requires OAuth2 authentication.
    """
    url = "/game/create_character"
    name = "api.game.create_character"

    @oauth(force=True)
    def post(self):
        max_points = self.web_app.config.get("game", "max_stat_points", default=20)
        data = request.json or {}

        if "name" not in data:
            raise BadRequest(description="Your character requires a name!")

        elif "description" not in data:
            raise BadRequest(description="Your character requires a description!")

        elif "strength" not in data:
            raise BadRequest(description="Your character requires a strength stat!")

        elif "dexterity" not in data:
            raise BadRequest(description="Your character requires a dexterity stat!")

        elif "health" not in data:
            raise BadRequest(description="Your character requires a health stat!")

        elif "special" not in data:
            raise BadRequest(description="Your character requires a special selection!")

        elif data["special"] not in ("lightning", "wither", "gamble"):
            raise BadRequest(description="Please select lightning, wither, or gamble as your special.")

        elif (int(data["strength"]) + int(data["dexterity"]) + int(data["health"])) > max_points:
            raise BadRequest(description="Point value of stats exceeds maximum of {0}".format(max_points))

        # All the checks succeeded, so let's set up a document.
        document = {
            "owner": str(self.user_data["username"]),
            "name": str(data["name"]),
            "description": str(data["description"]),
            "strength": int(data["strength"]),
            "dexterity": int(data["dexterity"]),
            "health": int(data["health"]),
            "special": str(data["special"])
        }

        # Everything checks out, so let's add their character to the database.
        # We have to create a query to the table we want to insert a document into
        insert_query = self.db.query("characters").insert(document)
        # Run the query in the database
        self.db.run(insert_query)

        return {'success': True}
