#!/usr/bin/python3

from flask import Flask, Response, request

import yaml
from os import path

from paste.views import paste
from url.views import url
from db import init_db
from cache import init_cache, invalidate

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
init_cache(app)
app.register_blueprint(paste)
app.register_blueprint(url)

if __name__ == '__main__':
    app.run(host='::1', port=10002)
