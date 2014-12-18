#!/usr/bin/python3

from werkzeug.routing import BaseConverter
from flask import Flask, Response, request, current_app
from jinja2 import Markup
from docutils import core

import re
import yaml
from os import path

from paste.views import paste
from url.views import url
from db import init_db
from cache import init_cache, invalidate
from util import b66_int, int_b66

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
app.url_map.converters['id'] = IDConverter
app.register_blueprint(paste)
app.register_blueprint(url)

@app.template_filter(name='rst')
def filter_rst(source):
    html = core.publish_parts(source, writer_name='html')['html_body']
    return Markup(html)

@app.template_global()
def include_raw(filename):
    env = current_app.jinja_env
    source = current_app.jinja_loader.get_source(env, filename)[0]
    return Markup(source)

if __name__ == '__main__':
    app.run(host='::1', port=10002)
