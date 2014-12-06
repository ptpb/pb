#!/usr/bin/python3

from hashlib import sha1

from flask import Flask, Response, request


import yaml
from os import path

from views import view
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
app.register_blueprint(view)

@app.after_request
def add_cache_header(response):
    if request.method == 'GET' and not response.cache_control.public:
        etag = sha1(response.data).hexdigest()
        response.add_etag(etag)
        response.cache_control.public = True
        response.cache_control.max_age = app.get_send_file_max_age(request.path)
        response.make_conditional(request)

    return response

@app.after_request
def invalidate_cache(response):
    location = response.headers.get('Location')
    if location:
        invalidate(location)
    return response

if __name__ == '__main__':
    app.run(host='::1', port=10002)
