import os

from proj import app
from proj.config_parser import Config

if __name__ == "__main__":
    config_file = os.path.join("config", "main_config.yaml")
    MAIN_CONFIG = Config(config_file)

    app.run(host=MAIN_CONFIG.config["web"]["ip"], port=int(MAIN_CONFIG.config["web"]["port"]))
