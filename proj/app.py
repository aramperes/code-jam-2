from config_parser import Config
from flask import Flask, request


app = Flask(__name__)


@app.route('/', methods=['POST'])
def get_env():
    data = request.json or {}
    god_name = data.get('name')
    if god_name:
        return 'Data coming soon.'
    else:
        return 'Please enter a god\'s name from greek mythology!'


if __name__ == "__main__":
    MAIN_CONFIG = Config.parse("config/main_config.config")
    app.run(host = MAIN_CONFIG["IP"], port = MAIN_CONFIG["PORT"])
