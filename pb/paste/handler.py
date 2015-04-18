# -*- coding: utf-8 -*-
"""
    paste.handler
    ~~~~~~~~~~~~~

    handlers to mangle paste content.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from flask import Response, render_template, url_for, request

from pb.util import rst, markdown

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
        content = render_template("generic.html", content=content, override=request.args.get('css'))
    return Response(content, mimetype='text/html')

handlers = {
    'r': render
}

def get(handler, content, mimetype, **kwargs):
    h = handlers.get(handler)
    if not h:
        return "Invalid handler: '{}'.".format(handler), 400
    return h(content, mimetype, **kwargs)
