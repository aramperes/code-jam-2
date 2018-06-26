import waitress
from flask import Flask, jsonify

from proj.config_parser import Config
from proj.database.database_manager import DatabaseManager


class WebApp:
    def __init__(self, config: Config):
        self.config = config

        # Database setup
        self.db = DatabaseManager(config)
        self.db.create_tables()
        self.db.migrate()

        self.app = Flask(__name__)
        self.db.attach_flask(self.app)

        # todo: remove this, use proper route manager
        @self.app.route('/', methods=["GET"])
        def index_route():
            return jsonify(
                {
                    "database_connected": self.db.connection.is_open()
                }
            )

    def serve(self):
        waitress.serve(self.app,
                       host=self.config.config["web"]["ip"],
                       port=self.config.config["web"]["port"])
