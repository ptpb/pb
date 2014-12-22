# -*- coding: utf-8 -*-
"""
    pb
    ~~

    pb is a lightweight pastebin.

    :copyright: Copyright (C) 2014 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from werkzeug.routing import BaseConverter
from flask import Flask, Response, request

import re
import yaml
from xdg import BaseDirectory
from binascii import unhexlify, hexlify

from pb.paste.views import paste
from pb.url.views import url
from pb.db import init_db
from pb.cache import init_cache, invalidate
from pb.util import b66_int, int_b66

class TextResponse(Response):
    default_mimetype = 'text/plain'

class IDConverter(BaseConverter):
    def __init__(self, map, length):
        super().__init__(map)
        self.regex = '(([A-Za-z0-9.~_-]{{{}}})([.][^/]*)?)'.format(length)
        self.sre = re.compile(self.regex)
        self.length = length

    def to_python(self, value):
        (name, id, _) = self.sre.match(value).groups()
        return b66_int(id), name

    def to_url(self, value):
        if isinstance(value, int):
            return int_b66(self.length, value)
        return int_b66(self.length, *value)

class SHA1Converter(BaseConverter):
    def __init__(self, map):
        super().__init__(map)
        self.regex = '(([A-Za-z0-9]{40})([.][^/]*)?)'
        self.sre = re.compile(self.regex)

    def to_python(self, value):
        (name, hexdigest, _) = self.sre.match(value).groups()
        return unhexlify(hexdigest), name

def load_yaml(app, filename):
    for filename in BaseDirectory.load_config_paths('pb', filename):
        with open(filename) as f:
            obj = yaml.load(f)
            app.config.from_mapping(obj)

def create_app(config_filename='config.yaml'):
    app = Flask(__name__)
    app.response_class = TextResponse
    app.url_map.converters['id'] = IDConverter
    app.url_map.converters['sha1'] = SHA1Converter

    load_yaml(app, config_filename)
    init_db(app)
    init_cache(app)

    app.register_blueprint(paste)
    app.register_blueprint(url)

    return app
