# -*- coding: utf-8 -*-
"""
    paste.handler
    ~~~~~~~~~~~~~

    handlers to mangle paste content.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from json import dumps
from flask import render_template, url_for, request
from werkzeug.routing import BaseConverter

from pb.util import rst, markdown, style_args
from pb.responses import StatusResponse

from mimetypes import add_type

add_type('text/x-markdown', '.md')
add_type('text/x-rst', '.rst')

mimetypes = {
    'text/x-markdown': markdown,
    'text/x-rst': rst
}

def render(content, mimetype, partial=False, **kwargs):
    renderer = mimetypes.get(mimetype, rst)
    content = renderer(content)
    if not partial:
        content = render_template("generic.html", cc='container-fluid', content=content, **style_args())
    return content

options = ['autoPlay', 'loop', 'startAt', 'speed', 'snapshot',
           'fontSize', 'theme', 'title', 'author', 'authorURL', 'authorImgURL']

def lazy_int(num):
    try:
        return int(num)
    except ValueError:
        return num

def terminal(content, mimetype, path=None, **kwargs):
    # FIXME: this is really bad, because the db bothered to give us
    # content, and we discard it here.
    url = url_for('paste.get', label='{}.json'.format(path))
    content = render_template("asciinema.html", url=url)
    return content

handlers = {
    'r': render,
    't': terminal
}

def get(handler, content, mimetype, **kwargs):
    h = handlers.get(handler)
    if not h:
        return StatusResponse({"invalid handler": handler}, 400)
    return h(content, mimetype, **kwargs)

# dirtyhack
class HandlerConverter(BaseConverter):
    regex = '[{}]'.format(''.join(handlers))
    weight = 50
