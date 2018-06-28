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
        primary_key="id",
        keys=[
            "id",
            "username",
            "password_hash"
        ]
    ),
    "oauth_tokens": TableSchema(
        primary_key="token",
        keys=[
            "token",
            "user_id",
            "expires"
        ]
    ),
    "oauth_refresh_tokens": TableSchema(
        primary_key="refresh_token",
        keys=[
            "refresh_token",
            "user_id"
        ]
    ),
    "characters": TableSchema(
        primary_key="id",
        keys=[
            "id",
            "user_id",
            "name",
            "description",
            "strength",
            "dexterity",
            "health",
            "special"
        ]
    ),
    "games": TableSchema(
        primary_key="id",
        keys=[
            "id",
            "challenger_username",
            "defender_username",
            "challenger_character",
            "challenger_character_stats",
            "defender_character",
            "defender_character_stats",
            "stats",
            "turn",
            "turn_number",
            "max_turns",
        ]
    ),
    "challenges": TableSchema(
        primary_key="id",
        keys=[
            "id",
            "challenger_username",
            "defender_username",
            "challenger_character",
            "max_turns"
        ]
    )
}
