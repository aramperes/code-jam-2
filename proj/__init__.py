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
