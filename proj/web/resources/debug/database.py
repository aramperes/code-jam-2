from proj.web.base_resource import BaseResource


class DebugDatabaseResource(BaseResource):
    url = "/debug/db"
    name = "api.debug.database"

    def get(self):
        result = {
            "database_connected": self.db.connection.is_open()
        }
        if not result["database_connected"]:
            return result
        # list of tables
        result["tables"] = self.db.run(self.db.table_list())
        return result
