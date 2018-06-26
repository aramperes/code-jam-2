import importlib
import logging
import os

import rethinkdb
from flask import Flask

from proj.config_parser import Config
from proj.database.schema import SCHEMA

log = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, config: Config):
        self.ip = config.config["database"]["ip"]
        self.port = int(config.config["database"]["port"])
        self.database_name = config.config["database"]["database_name"]
        self.connection = None

        with self.connect() as self.connection:
            self.try_create_database()

    def connect(self):
        return rethinkdb.connect(host=self.ip, port=self.port, db=self.database_name)

    def get_doc(self, table, key):
        """
        Gets a single document with the given primary key value in the given table.
        :param table: the table to lookup
        :param key: the primary key (usually an ID) of the document to find
        :return: a dict containing the document's fields, or None if no such document exists
        """
        doc = rethinkdb.table(table).get(key).run(self.connection)
        return dict(doc) if doc else None

    def try_create_database(self):
        try:
            rethinkdb.db_create(self.database_name).run(self.connection)
            log.debug("Created database '{0}'.".format(self.database_name))
        except rethinkdb.ReqlRuntimeError:
            log.debug("Failed to create database '{0}'; already exists.".format(self.database_name))

    def create_tables(self):
        with self.connect() as self.connection:
            # find the existing tables first
            existing_tables = rethinkdb.db(self.database_name).table_list().run(self.connection)
            log.debug(f"Found {len(existing_tables)} table(s): {str(existing_tables)}.")

            for table_name, schema in SCHEMA.items():
                if table_name in existing_tables:
                    continue

                log.debug(f"Creating new table '{table_name}'.")
                rethinkdb.table_create(table_name, primary_key=schema.primary_key).run(self.connection)

    def migrate(self):
        migrations_table = "_migrations"
        migrations_directory = os.path.abspath(os.path.join(".", "proj", "database", "migrations"))
        table_names = SCHEMA.keys()

        with self.connect() as self.connection:
            for table in table_names:
                try:
                    table_directory = os.path.join(migrations_directory, table)
                    # check if there is a directory for that migration
                    if not os.path.exists(table_directory):
                        log.debug("No migrations found for table '{0}'.".format(table))
                        continue

                    current_revision = 0
                    migration_data = self.get_doc(migrations_table, table)
                    if migration_data is not None:
                        current_revision = int(migration_data["version"])

                    running_revision = current_revision + 1
                    while True:
                        migration_file = os.path.join(table_directory, "v{0}.py".format(running_revision))
                        if not os.path.exists(migration_file):
                            # no more migrations for this table
                            break
                        log.debug("Running migration {0}/v{1}".format(table, running_revision))
                        migration_module = importlib.import_module(
                            "proj.database.migrations.{0}.v{1}".format(table, running_revision)
                        )
                        # run the migration
                        migration_module.migrate(self, table)

                        # go to the next migration
                        running_revision += 1

                    # the last migration that was run
                    last_migration = running_revision - 1
                    if current_revision == last_migration:
                        log.debug("Table '{0}' is up-to-date.".format(table))
                        continue
                    migration_data = {
                        "table_name": table,
                        "version": last_migration
                    }

                    # update the migrations table
                    rethinkdb.table(migrations_table).insert(migration_data,
                                                             conflict="replace",
                                                             durability="soft").run(self.connection)
                except Exception:
                    log.warning("Failed to migrate '{0}'".format(table))
                    raise

    def attach_flask(self, app: Flask):
        # Attach flask request handlers and other settings
        app.before_request(self._flask_before_request)
        app.teardown_request(self._flask_teardown_request)

    def _flask_before_request(self):
        # connect to the database
        self.connection = self.connect()

    def _flask_teardown_request(self, exception):
        # close the connection
        try:
            self.connection.close()
        except AttributeError:
            pass
