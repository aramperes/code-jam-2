from typing import Tuple


class TableSchema:
    def __init__(self, keys: Tuple[str, ...], primary_key="id"):
        self.primary_key = primary_key
        self.keys = keys


SCHEMA = {
    "_migrations": TableSchema(
        # The "_migrations" table keeps track of the state of the different tables in the database.
        # For each table, there is a corresponding version to keep track of the last migration run on
        # that particular table.
        primary_key="table_name",
        keys=(
            "table_name",
            "version"
        )
    ),
    "users": TableSchema(
        primary_key="id",
        keys=(
            "id",
            "username",
            "password_hash"
        )
    ),
    "oauth_tokens": TableSchema(
        primary_key="token",
        keys=(
            "token",
            "user_id",
            "expires"
        )
    ),
    "oauth_refresh_tokens": TableSchema(
        primary_key="refresh_token",
        keys=(
            "refresh_token",
            "user_id"
        )
    ),
    "stories": TableSchema(
        primary_key="id",
        keys=(
            "id",
            "user_id",
            "public",
            "sentences",
            "media"
        )
    )
}
