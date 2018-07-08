import logging
import os

import pytest
import rethinkdb

from proj.config_parser import Config
from proj.web.app import WebApp

log = logging.getLogger(__name__)


class ConfigShim(Config):
    def __init__(self):
        self.config = {
            "database": {
                "ip": os.environ.get("RETHINKDB_HOST", default="127.0.0.1"),
                "port": 28015,
                "database_name": "temp_test_database"
            },
            "debug": True,
            "stories": {
                "ffmpeg": os.environ.get("FFMPEG_EXEC", default="ffmpeg")
            },
            "game": {
                "max_stat_points": 20
            }
        }


@pytest.fixture(scope="module")
def client(request):
    """
    Client fixture.
    """
    config = ConfigShim()

    # check if rethinkdb temp database already exists
    db_name = config.get("database", "database_name")
    with rethinkdb.connect(host=config.get("database", "ip"), port=config.get("database", "port"),
                           db=config.get("database", "database_name")) as conn:
        if db_name in rethinkdb.db_list().run(conn):
            rethinkdb.db_drop(db_name).run(conn)
            log.warning("Dropped temporary test database {0}".format(db_name))

    web = WebApp(config)
    test_client = web.flask_app.test_client()

    def teardown():
        with web.db.connect() as conn:
            rethinkdb.db_drop(db_name).run(conn)
            log.info("Dropped temporary test database {0}".format(db_name))

    request.addfinalizer(teardown)
    return test_client
