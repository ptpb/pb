# -*- coding: utf-8 -*-
"""
    pb
    ~~

    pb is a lightweight pastebin.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from flask import Flask, request
from xdg import BaseDirectory

from pb.cache import init_cache
from pb.config import load_config
from pb.converters import (LabelConverter, NamespaceConverter, SHA1Converter,
                           SIDConverter)
from pb.db import init_db
from pb.logging import init_logging
from pb.namespace.views import namespace
from pb.paste.handler import HandlerConverter
from pb.paste.views import paste
from pb.responses import BaseResponse
from pb.routing import RequestContext, Rule
from pb.template import init_template


cors_map = {
    'Origin': 'Access-Control-Allow-Origin',
    'Access-Control-Request-Headers': 'Access-Control-Allow-Headers',
    'Access-Control-Request-Method': 'Access-Control-Allow-Methods',
}


def cors(response):
    for request_header, response_header in cors_map.items():
        value = request.headers.get(request_header)
        if value:
            response.headers[response_header] = value

    return response


class App(Flask):
    response_class = BaseResponse
    url_rule_class = Rule

    def request_context(self, environ):
        return RequestContext(self, environ)


def xdg_static_folder():
    for path in BaseDirectory.load_data_paths('pbs'):
        return path
    return 'static'


def create_app(config_filename='config.yaml'):

    app = App(__name__, static_url_path='/static', static_folder=xdg_static_folder())
    app.url_map.converters.update(dict(
        sid=SIDConverter,
        sha1=SHA1Converter,
        label=LabelConverter,
        namespace=NamespaceConverter,
        handler=HandlerConverter
    ))

    load_config(app, config_filename)
    init_db(app)
    init_cache(app)
    init_template(app)
    init_logging(app)

    app.after_request(cors)

    app.register_blueprint(paste)
    app.register_blueprint(namespace)

    app.url_map.update()
    #print('\n'.join(repr(i) for i in app.url_map._rules))

    return app
