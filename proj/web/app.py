import os
from typing import Type

import waitress
from flask import Blueprint, Flask, request
from flask_restful import Api
from werkzeug.exceptions import NotFound

from proj.config_parser import Config
from proj.database.database_manager import DatabaseManager
from proj.web.api.base_resource import BaseResource
from proj.web.api.resources.auth.login import LoginResource
from proj.web.api.resources.auth.refresh import RefreshTokenResource
from proj.web.api.resources.auth.register import RegisterResource
from proj.web.api.resources.debug.config import DebugConfigResource
from proj.web.api.resources.debug.database import DebugDatabaseResource
from proj.web.api.resources.game.challenge import ChallengeResource
from proj.web.api.resources.game.create_character import CreateCharacterResource
from proj.web.api.resources.game.decide_challenge import ChallengeDecisionResource
from proj.web.api.resources.game.play_game import PlayGameResource
from proj.web.api.resources.index import IndexResource
from proj.web.api.resources.stories.corpus import ListCorpusStoriesResource
from proj.web.api.resources.stories.create_story import CreateStoryResource
from proj.web.api.resources.stories.explore_stories import ExploreStoriesResource
from proj.web.api.resources.stories.list_own_stories import ListOwnStoriesResource
from proj.web.api.resources.stories.list_user_stories import ListUserStoriesResource
from proj.web.api.resources.stories.play_story import PlayStoryResource
from proj.web.api.resources.stories.story import StoryResource
from proj.web.api.resources.user import UserResource
from proj.web.api.resources.user_list import UserListResource
from proj.web.console.base_view import BaseView
from proj.web.console.views.index import ConsoleIndexView
from proj.web.landing import LandingView


class WebApp:
    """
    The API web application.
    """

    def __init__(self, config: Config):
        self.config = config
        self.debug = bool(self.config.get("debug", default=False))

        # Database setup
        self.db = DatabaseManager(config)
        self.db.create_tables()
        self.db.migrate()

        # Flask setup
        root_path = os.getcwd()
        static_dir = os.path.join(root_path, "static")
        templates_dir = os.path.join(root_path, "templates")
        self.flask_app = Flask(__name__,
                               root_path=root_path,
                               template_folder=templates_dir,
                               static_folder=static_dir)
        self.db.attach_flask(self.flask_app)
        self.blueprint_api = Blueprint("api", __name__, url_prefix="/api")
        self.blueprint_console = Blueprint("console", __name__, url_prefix="/console",
                                           root_path=root_path,
                                           template_folder=os.path.join(templates_dir, "console"),
                                           static_folder=static_dir)

        # Flask-RESTful setup
        self.api = Api()
        self.register_api_resources()
        self.api.init_app(self.blueprint_api)

        # Console setup
        self.register_console_view(ConsoleIndexView)

        # Landing page setup
        self.register_landing_view()

        # Finally, register the blueprints
        self.flask_app.register_blueprint(self.blueprint_api)
        self.flask_app.register_blueprint(self.blueprint_console)

        # Patch 404s for blueprints
        self._patch_flask_blueprint_404(self.flask_app, self.blueprint_api, self.api.handle_error)

    def register_api_resources(self):
        """
        Registers the API resources.
        """
        # todo: auto-discovery?

        self.register_api_resource(IndexResource)
        self.register_api_resource(UserResource)
        self.register_api_resource(UserListResource)

        # Authentication resources
        # Documentation: https://gitlab.com/DefiantSails/code-jam-2/wikis/Authentication
        self.register_api_resource(LoginResource)
        self.register_api_resource(RegisterResource)
        self.register_api_resource(RefreshTokenResource)

        # Stories
        # Documentation: https://gitlab.com/DefiantSails/code-jam-2/wikis/Mythological-Stories-API
        self.register_api_resource(ListOwnStoriesResource)
        self.register_api_resource(ListUserStoriesResource)
        self.register_api_resource(CreateStoryResource)
        self.register_api_resource(PlayStoryResource)
        self.register_api_resource(StoryResource)
        self.register_api_resource(ExploreStoriesResource)
        self.register_api_resource(ListCorpusStoriesResource)

        # Game Resources
        self.register_api_resource(ChallengeResource)
        self.register_api_resource(ChallengeDecisionResource)
        self.register_api_resource(CreateCharacterResource)
        self.register_api_resource(PlayGameResource)

        # Debug resources
        if self.debug:
            self.register_api_resource(DebugDatabaseResource)
            self.register_api_resource(DebugConfigResource)

    def register_api_resource(self, resource_class: Type[BaseResource]):
        """
        Registers a resource to the Flask-RESTful API instance
        :param resource_class: the class of the resource
        """
        class_setup = resource_class.setup(self)
        endpoint = resource_class.name
        self.api.add_resource(
            class_setup,
            resource_class.url,
            endpoint=endpoint
        )

    def register_console_view(self, view_class: Type[BaseView]):
        class_setup = view_class.setup(self)
        endpoint = view_class.name
        self.blueprint_console.add_url_rule(class_setup.url, view_func=class_setup.as_view(endpoint))

    def register_landing_view(self):
        self.flask_app.add_url_rule("/", view_func=LandingView().as_view("landing"))

    def serve(self):
        """
        Serves the Flask application using the waitress WSGI.
        """
        waitress.serve(self.flask_app,
                       host=self.config.get("web", "ip"),
                       port=self.config.get("web", "port"))

    @staticmethod
    def _patch_flask_blueprint_404(flask_app: Flask, blueprint: Blueprint, handler):
        def patched_handler(e):
            path = request.path
            if path.startswith(blueprint.url_prefix):
                return handler(e)
            return flask_app.make_response(NotFound())

        flask_app.register_error_handler(404, patched_handler)
