from proj.database.mixin import ResourceWithDatabase


class IndexResource(ResourceWithDatabase):
    url = "/"
    name = "api.index"

    def get(self):
        return {
            "database_connected": self.db.connection.is_open()
        }
