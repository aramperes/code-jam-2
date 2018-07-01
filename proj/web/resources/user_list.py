from proj.web.base_resource import BaseResource


class UserListResource(BaseResource):
    """
    Gets information about all users.
    """
    url = "/users"
    name = "api.user.list"

    def get(self):
        final_data = []
        user_query = self.db.query('users').pluck('username').coerce_to('array')

        for user in self.db.run(user_query):
            user_data = {
                "username": user["username"],
                "current_game": None,
                "current_role": None
            }

            main_query = self.db.run(
                self.db.query("games").get_all(user["username"], index="challenger_username").filter({
                    "won": None
                }).coerce_to("array")
            )
            if main_query:
                user_data["current_game"] = main_query[0]["id"]
                user_data["current_role"] = "challenger"
                final_data.append(user_data)
                continue

            secondary_query = self.db.run(
                self.db.query("games").get_all(user["username"], index="defender_username").filter({
                    "won": None
                }).coerce_to("array")
            )
            if secondary_query:
                user_data["current_game"] = secondary_query[0]["id"]
                user_data["current_role"] = "defender"
                final_data.append(user_data)
                continue

            final_data.append(user_data)

        return final_data
