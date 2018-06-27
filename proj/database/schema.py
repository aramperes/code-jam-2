from typing import List


class TableSchema:
    def __init__(self, keys: List, primary_key="id"):
        self.primary_key = primary_key
        self.keys = keys


SCHEMA = {
    "_migrations": TableSchema(
        # The "_migrations" table keeps track of the state of the different tables in the database.
        # For each table, there is a corresponding version to keep track of the last migration run on
        # that particular table.
        primary_key="table_name",
        keys=[
            "table_name",
            "version"
        ]
    ),
    "users": TableSchema(
        primary_key="username",
        keys=[
            "username",
            "password_hash"
        ]
    )
}
