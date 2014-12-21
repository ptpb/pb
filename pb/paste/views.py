# -*- coding: utf-8 -*-
"""
    paste.views
    ~~~~~~~~~~~

    paste url routes and views.

    :copyright: Copyright (C) 2014 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from yaml import safe_dump
from uuid import UUID
from mimetypes import guess_type

from flask import Blueprint, Response, request, render_template, current_app, url_for
from jinja2 import Markup
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_all_lexers

from pb.db import cursor
from pb.paste import model, handler as _handler
from pb.util import highlight, redirect, request_content, id_url, publish_parts

paste = Blueprint('paste', __name__)

@paste.app_template_filter(name='rst')
def filter_rst(source):
    return Markup(publish_parts(source))

@paste.app_template_global()
def include_raw(filename):
    env = current_app.jinja_env
    source = current_app.jinja_loader.get_source(env, filename)[0]
    return Markup(source)

@paste.route('/')
def index():
    return Response(render_template("index.html"), mimetype='text/html')

@paste.route('/f')
def form():
    return Response(render_template("form.html"), mimetype='text/html')

@paste.route('/', methods=['POST'])
@cursor
def post():
    content, filename = request_content()
    if not content:
        return "Nope.\n", 400

    id, uuid = model.get_digest(content)
    if not id:
        id, uuid = model.insert(content)

    url = id_url(b66=(id, filename))
    uuid = str(UUID(bytes=uuid)) if uuid else '<redacted>'
    return redirect(url, safe_dump(dict(url=url, uuid=uuid), default_flow_style=False))

@paste.route('/<uuid:uuid>', methods=['PUT'])
@cursor
def put(uuid):
    content, filename = request_content()
    if not content:
        return "Nope.\n", 400

    id, _ = model.get_digest(content)
    if id:
        url = id_url(b66=id)
        return redirect(url, "Paste already exists.\n", 409)

    id = model.put(uuid.bytes, content)
    if id:
        url = id_url(b66=(id, filename))
        return redirect(url, "{} updated.\n".format(url), 200)

    return "Not found.\n", 404

@paste.route('/<uuid:uuid>', methods=['DELETE'])
@cursor
def delete(uuid):
    id = model.delete(uuid.bytes)
    if id:
        url = id_url(b66=id)
        return redirect(url, "{} deleted.\n".format(url), 200)
    return "Not found.\n", 404

@paste.route('/<id(length=4):b66>')
@paste.route('/<id(length=4):b66>/<string(minlength=0):lexer>')
@paste.route('/<string(length=1):handler>/<id(length=4):b66>')
@cursor
def get(b66, lexer=None, handler=None):
    id, name = b66
    mimetype, _ = guess_type(name)

    content = model.get_content(id)
    if not content:
        return "Not found.\n", 404

    if lexer != None:
        return highlight(content, lexer)
    if handler != None:
        return _handler.get(handler, content)
    if mimetype:
        return Response(content, mimetype=mimetype)

    return content

@paste.route('/s')
@cursor
def stats():
    count, length = model.get_stats()
    return safe_dump(dict(pastes=count, bytes=length), default_flow_style=False)

@paste.route('/static/highlight.css')
def highlight_css():
    css = HtmlFormatter().get_style_defs('.code')
    return Response(css, mimetype='text/css')

@paste.route('/l')
def list_lexers():
    lexers = '\n'.join(' '.join(i) for _, i, _, _ in get_all_lexers())
    return '{}\n'.format(lexers)
