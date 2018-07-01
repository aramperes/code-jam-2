from random import randint

from flask import request
from werkzeug.exceptions import BadRequest, Unauthorized

from proj.web.base_resource import BaseResource
from proj.web.oauth import oauth


class PlayGameResource(BaseResource):
    """
    Used to challenge another user to a game.
    Required data:
    POST:
    {
        "id": string
        "move": string
    }
    This route requires OAuth2 authentication.
    GET:
    {
        "id": string
    }
    This route requires OAuth2 authentication.
    """
    url = "/game/play"
    name = "api.game.play"

    @oauth(force=True)
    def post(self):
        data = request.json or {}
        game = self.db.get_doc("games", data["id"])

        if not game:
            raise BadRequest(description="Game not found.")

        if game["won"]:
            raise Unauthorized(description="You cannot play a game that has already been concluded.")

        if self.user_data["username"] not in (game["defender_username"], game["challenger_username"]):
            raise Unauthorized(description="You are not a player in this game.")

        try:
            if self.user_data["username"] == game["defender_username"]:
                attacker = game["defender_stats"]
                victim = game["challenger_stats"]

                # Let's do the check for a game cancel in here as we already know the user's position
                if data["move"].lower() == "cancel":
                    self.db.run(self.db.query("games").get(data["id"]).update({"won": "challenger"}))

                    return {
                        "success": True,
                        "game_data": self.db.get_doc("games", data["id"])
                    }

            else:
                attacker = game["challenger_stats"]
                victim = game["defender_stats"]

                # Let's do the check for a game cancel in here as we already know the user's position
                if data["move"].lower() == "cancel":
                    self.db.run(self.db.query("games").get(data["id"]).update({"won": "defender"}))

                    return {
                        "success": True,
                        "game_data": self.db.get_doc("games", data["id"])
                    }

            win = False
            special = False
            update = None  # "attacker" or "victim"
            valid = False

            if self.user_data["username"] == game["turn"]:
                if data["move"].lower() == "grapple":
                    valid = True

                    if attacker["strength"] + randint(-5, 5) > victim["dexterity"] + randint(-5, 5):
                        win = True

                elif data["move"].lower() == "punch":
                    valid = True

                    if attacker["dexterity"] + randint(-5, 5) > victim["strength"] + randint(-5, 5):
                        win = True

                elif data["move"].lower() == "kick":
                    valid = True

                    if attacker["dexterity"] + randint(-5, 5) > victim["dexterity"] + randint(-5, 5):
                        win = True

                elif data["move"].lower() in ("lightning", "wither", "gamble"):
                    # Check if the character can use this special ability
                    if attacker["special"] != data["move"].lower():
                        raise BadRequest("You cannot use this ability, "
                                         "because your character's special ability is {0}".format(attacker["special"]))
                    valid = True
                    special = True

                updated_stats = None
                if special:
                    if data["move"].lower() == "gamble":
                        if randint(1, 2) == 1:
                            # You lose points
                            update = "attacker"
                            updated_stats = attacker
                            updated_stats["strength"] -= 1
                            updated_stats["dexterity"] -= 1

                        else:
                            # They lose points
                            update = "victim"
                            updated_stats = victim
                            updated_stats["strength"] -= 1
                            updated_stats["dexterity"] -= 1

                    elif data["move"].lower() == "lightning":

                        update = "victim"
                        updated_stats = victim
                        updated_stats["dexterity"] -= 1

                    elif data["move"].lower() == "wither":
                        update = "victim"
                        updated_stats = victim
                        updated_stats["strength"] -= 1

                elif win:
                    update = "victim"
                    updated_stats = victim

                    if data["move"].lower() == "grapple":

                        updated_stats["dexterity"] -= 1
                        updated_stats["health"] -= 1

                    elif data["move"].lower() == "punch":

                        updated_stats["strength"] -= 1
                        updated_stats["health"] -= 1

                    elif data["move"].lower() == "kick":

                        updated_stats["strength"] -= 1
                        updated_stats["dexterity"] -= 1
                        updated_stats["health"] -= 1

                if valid:

                    if self.user_data["username"] == game["defender_username"]:

                        # Update the turn to the next person
                        self.db.run(
                            self.db.query("games").get(data["id"]).update({"turn": game["challenger_username"]}))
                        if updated_stats:
                            if update == "attacker":
                                self.db.run(
                                    self.db.query("games").get(data["id"]).update({"defender_stats": updated_stats}))
                            else:
                                self.db.run(
                                    self.db.query("games").get(data["id"]).update({"challenger_stats": updated_stats}))

                            if special and update == "attacker":

                                health_update = updated_stats
                                health_update["health"] -= 1
                                self.db.run(
                                    self.db.query("games").get(data["id"]).update({"defender_stats": health_update}))

                            elif special and update == "victim":

                                health_update = attacker
                                health_update["health"] -= 1
                                self.db.run(
                                    self.db.query("games").get(data["id"]).update({"defender_stats": health_update}))

                    elif self.user_data["username"] == game["challenger_username"]:

                        # Update the turn to the next person
                        self.db.run(self.db.query("games").get(data["id"]).update({"turn": game["defender_username"]}))

                        if updated_stats:
                            if update == "attacker":
                                self.db.run(
                                    self.db.query("games").get(data["id"]).update({"challenger_stats": updated_stats}))
                            else:
                                self.db.run(
                                    self.db.query("games").get(data["id"]).update({"defender_stats": updated_stats}))

                            if special and update == "attacker":

                                health_update = updated_stats
                                health_update["health"] -= 1
                                self.db.run(
                                    self.db.query("games").get(data["id"]).update({"challenger_stats": health_update}))

                            elif special and update == "victim":

                                health_update = attacker
                                health_update["health"] -= 1
                                self.db.run(
                                    self.db.query("games").get(data["id"]).update({"challenger_stats": health_update}))

                    # Increase the turn counter by one
                    self.db.run(self.db.query("games").get(data["id"]).update({"turn_number": game["turn_number"] + 1}))

                    # Our old DB document may be out of date now so let's get a new copy
                    health_check = self.db.get_doc("games", data["id"])

                    if health_check["defender_stats"]["health"] <= 0:
                        self.db.run(self.db.query("games").get(data["id"]).update({"won": "challenger"}))

                    elif health_check["challenger_stats"]["health"] <= 0:
                        self.db.run(self.db.query("games").get(data["id"]).update({"won": "defender"}))

                    elif health_check["turn_number"] > health_check["max_turns"]:
                        self.db.run(self.db.query("games").get(data["id"]).update({"won": "tie"}))

                    return {
                        "success": True,
                        "data": self.db.get_doc("games", data['id'])
                    }
            else:
                raise BadRequest(description="It is not your turn.")

            raise BadRequest(description="Please enter a valid move.")

        except ValueError:
            raise BadRequest(description="A move is required!")

    def get(self):
        game_id = request.args.get("id", type=str)
        if not game_id:
            raise BadRequest(description="Please enter an ID.")

        game = self.db.get_doc("games", game_id)
        if not game:
            raise BadRequest(description="Game not found.")

        return {
            "success": True,
            "data": game
        }
