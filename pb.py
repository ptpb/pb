#!/usr/bin/python3

from flask import Flask, Response

import yaml
from os import path

from views import view
from db import init_db

class TextResponse(Response):
    default_mimetype = 'text/plain'

def load_yaml(app, filename):
    filename = path.join(app.root_path, filename)
    with open(filename) as f:
        obj = yaml.load(f)

    return app.config.from_mapping(obj)

app = Flask(__name__)
app.response_class = TextResponse
load_yaml(app, 'config.yaml')
init_db(app)
app.register_blueprint(view)

@app.after_request
def add_cache_header(response):
    response.cache_control.max_age = 300
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=10002)
