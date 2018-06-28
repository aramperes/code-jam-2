import rethinkdb
from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class UserResource(BaseResource):
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


    @oauth
    def post(self):
        max_points = main_config.get("user", "max_stat_points")
        data = request.json or {}

        if "name" not in data:
            return BadRequest(description="Your character requires a name!")

        elif "description" not in data:
            return BadRequest(description="Your character requires a description!")

        elif "strength" not in data:
            return BadRequest(description="Your character requires a strength stat!")

        elif "dexterity" not in data:
            return BadRequest(description="Your character requires a dexterity stat!")

        elif "health" not in data:
            return BadRequest(description="Your character requires a health stat!")

        elif "special" not in data:
            return BadRequest(description="Your character requires a special selection!")

        elif data[special] not in ["lightning", "wither", "gamble"]:
            return BadRequest(description="Please select lightning, wither, or gamble as your special.")

        elif int(data["strength"] + data["dexterity"] + data["health"]) > max_points:
            return BadRequest(description="Point value of stats exceeds maximum of {}".format(str(max_points)))

        # All the checks succeeded, so let's set up a document.
        document = {
            "owner": self.user_data["username"],
            "name": data["name"],
            "description": data["description"],
            "strength": data["strength"],
            "dexterity": data["dexterity"],
            "health": data["health"],
            "special": data["special"]
        }

        # Everything checks out, so let's add their character to the database.
        # We have to create a query to the table we want to insert a document into
        insert_query = self.db.query("characters").insert(document)
        # Run the query in the database
        self.db.run(insert_query)

        return {'success': True}
