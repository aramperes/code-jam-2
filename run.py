import logging
import os

from proj.config_parser import Config
from proj.web.app import WebApp

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    config_file = os.path.join("config", "main_config.yaml")
    MAIN_CONFIG = Config(config_file)

    web = WebApp(MAIN_CONFIG)
    web.serve()
