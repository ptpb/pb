# -*- coding: utf-8 -*-
"""
    pb
    ~~

    pb is a lightweight pastebin.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from flask import Flask, Response, request

import yaml
from xdg import BaseDirectory

from pb.paste.views import paste
from pb.db import init_db
from pb.cache import init_cache, invalidate
from pb.converters import SIDConverter, SHA1Converter, LabelConverter

class TextResponse(Response):
    default_mimetype = 'text/plain'

def load_yaml(app, filename):
    for filename in BaseDirectory.load_config_paths('pb', filename):
        with open(filename) as f:
            obj = yaml.load(f)
            app.config.from_mapping(obj)

def cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    print(response.data)
    return response

def create_app(config_filename='config.yaml'):
    app = Flask(__name__)
    app.response_class = TextResponse
    app.url_map.converters['sid'] = SIDConverter
    app.url_map.converters['sha1'] = SHA1Converter
    app.url_map.converters['label'] = LabelConverter

    load_yaml(app, config_filename)
    init_db(app)
    init_cache(app)

    app.after_request(cors)

    app.register_blueprint(paste)

    return app
