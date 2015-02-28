# -*- coding: utf-8 -*-
"""
    pb
    ~~

    pb is a lightweight pastebin.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from werkzeug.routing import BaseConverter
from flask import Flask, Response, request

import re
import yaml
from os import path
from xdg import BaseDirectory
from binascii import unhexlify, hexlify, Error as BinError
from base64 import urlsafe_b64encode, urlsafe_b64decode

from pb.paste.views import paste
from pb.db import init_db
from pb.cache import init_cache, invalidate

class TextResponse(Response):
    default_mimetype = 'text/plain'

class SIDConverter(BaseConverter):
    def __init__(self, map, length):
        super().__init__(map)
        self.regex = '(([A-Za-z0-9_~.-]{{{}}})(?:[.][^/]*)?)'.format(length)
        self.sre = re.compile(self.regex)
        if length % 4 != 0:
            raise NotImplementedError('{} % 4 != 0; kthx'.format(length))
        self.length = 6 * (length // 4)

    def to_python(self, value):
        name, sid = self.sre.match(value).groups()
        try:
            _hex = hexlify(urlsafe_b64decode(sid)).decode('utf-8')
        except BinError:
            _hex = None
        return _hex, name, value

    def to_url(self, value, length=None):
        f = lambda v: urlsafe_b64encode(unhexlify(v[-(length if length else self.length):])).decode('utf-8')
        if isinstance(value, str):
            return f(value)
        uuid, filename = value
        ext = path.splitext(filename)[1] if filename else ''
        return '{}{}'.format(f(uuid), ext)

class SHA1Converter(BaseConverter):
    def __init__(self, map):
        super().__init__(map)
        self.regex = '(([A-Za-z0-9]{40})(?:[.][^/]*)?)'
        self.sre = re.compile(self.regex)

    def to_python(self, value):
        name, hexdigest = self.sre.match(value).groups()
        return hexdigest, name

    def to_url(self, value):
        if isinstance(value, str):
            return value
        hexdigest, filename = value
        ext = path.splitext(filename)[1] if filename else ''
        return '{}{}'.format(hexdigest, ext)

class LabelConverter(BaseConverter):
    def __init__(self, map):
        super().__init__(map)
        self.regex = '((~[^/.]+)(?:[.][^/]*)?)'
        self.sre = re.compile(self.regex)

    def to_python(self, value):
        name, label = self.sre.match(value).groups()
        return label, name

    def to_url(self, value):
        if isinstance(value, str):
            return value
        label, filename = value
        ext = path.splitext(filename)[1] if filename else ''
        return '{}{}'.format(label, ext)

def load_yaml(app, filename):
    for filename in BaseDirectory.load_config_paths('pb', filename):
        with open(filename) as f:
            obj = yaml.load(f)
            app.config.from_mapping(obj)

def create_app(config_filename='config.yaml'):
    app = Flask(__name__)
    app.response_class = TextResponse
    app.url_map.converters['sid'] = SIDConverter
    app.url_map.converters['sha1'] = SHA1Converter
    app.url_map.converters['label'] = LabelConverter

    load_yaml(app, config_filename)
    init_db(app)
    init_cache(app)

    app.register_blueprint(paste)

    return app
