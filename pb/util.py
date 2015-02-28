# -*- coding: utf-8 -*-
"""
    util
    ~~~~

    Utility functions.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

import string
from os import path

from flask import Response, render_template, current_app, request, url_for

from pygments import highlight as _highlight, format as _format
from pygments.token import Token
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

from docutils import core
from markdown import markdown as _markdown

b66c = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-_~.'

def redirect(location, rv, code=302):
    response = current_app.response_class(rv, code)
    response.headers['Location'] = location
    return response

def highlight(content, lexer_name):
    try:
        lexer = get_lexer_by_name(lexer_name)
    except ClassNotFound:
        if lexer_name != '':
            return "No such lexer.", 400

    formatter = HtmlFormatter(linenos='table', anchorlinenos=True, lineanchors='L', linespans='L')

    if lexer_name == '':
        tokens = ((Token.Text, '{}\n'.format(c.decode('utf-8'))) for c in content.splitlines())
        content = _format(tokens, formatter)
    else:
        content = _highlight(content, lexer, formatter)

    template = render_template('generic.html', content=content)

    return Response(template, mimetype='text/html')

def request_content():
    c = request.form.get('c')
    if c:
        return c.encode('utf-8'), None
    fs = request.files.get('c')
    if fs:
        return fs.stream.read(), fs.filename

    return None, None

def id_url(**kwargs):
    proto = request.environ.get('HTTP_X_FORWARDED_PROTO')
    scheme = proto if proto else request.scheme
    return url_for('.get', _external=True, _scheme=scheme, **kwargs)

def any_url(paste, filename=None):
    if paste.get('private'):
        return id_url(sha1=(paste['digest'], filename))
    if paste.get('label'):
        return id_url(label=(paste['label'], filename))
    return id_url(sid=(paste['_id'], filename))

def rst(source):
    overrides = {'syntax_highlight': 'short'}
    parts = core.publish_parts(source.decode('utf-8'), writer_name='html', settings_overrides=overrides)
    return parts['html_body']

def markdown(source):
    md = _markdown(source.decode('utf-8'), extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.admonition',
        'markdown.extensions.codehilite',
        'markdown.extensions.meta',
        'markdown.extensions.toc',
        'markdown.extensions.wikilinks'
    ], extension_configs = {
        'markdown.extensions.codehilite': {
            'css_class': 'code'
        }
    })
    return md
