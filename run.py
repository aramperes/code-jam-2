import logging
import os

from proj.config_parser import Config
from proj.web.app import WebApp

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(name)s: %(message)s")

    config_file = os.path.join("config", "main_config.yaml")
    main_config = Config(config_file)

    web = WebApp(main_config)
    web.serve()
