from proj.web.api.base_resource import BaseResource


class DebugDatabaseResource(BaseResource):
    """
    A debug resource to check the connection and status of the database.
    Note: this resource is only accessible if the `debug` flag is set to `true` in the YAML configuration.
    """
    url = "/debug/db"
    name = "debug.database"

    def get(self):
        result = {
            "database_connected": self.db.connection.is_open()
        }
        if not result["database_connected"]:
            return result
        # list of tables
        result["tables"] = self.db.run(self.db.table_list())
        return result
