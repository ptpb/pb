# -*- coding: utf-8 -*-
"""
    paste.handler
    ~~~~~~~~~~~~~

    handlers to mangle paste content.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from flask import Response, render_template, url_for, request

from pb.util import publish_parts

def render(content):
    content = render_template("generic.html", content=publish_parts(content), override=request.args.get('css'))
    return Response(content, mimetype='text/html')

handlers = {
    'r': render
}

def get(handler, content):
    h = handlers.get(handler)
    if not h:
        return "Invalid handler: '{}'.".format(handler), 400
    return h(content)
