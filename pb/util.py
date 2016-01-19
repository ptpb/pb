# -*- coding: utf-8 -*-
"""
    util
    ~~~~

    Utility functions.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from io import BytesIO

from flask import render_template, request, url_for

from pygments import highlight as _highlight, format as _format
from pygments.token import Token
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter, get_formatter_by_name
from pygments.util import ClassNotFound

from werkzeug import http
from werkzeug.wrappers import get_host

from docutils import core
from markdown import markdown as _markdown

def style_args():
    return {k:request.args.get(k) for k in ['style','css']}

def highlight(content, lexer_name, formatter):
    try:
        lexer = get_lexer_by_name(lexer_name)
    except ClassNotFound:
        if lexer_name != '':
            return "No such lexer.", 400

    if formatter:
        formatter = get_formatter_by_name(formatter)
    else:
        formatter = HtmlFormatter(linenos='table', anchorlinenos=True, lineanchors='L', linespans='L')

    if lexer_name == '':
        tokens = ((Token.Text, '{}\n'.format(c.decode('utf-8'))) for c in content.splitlines())
        content = _format(tokens, formatter)
    else:
        content = _highlight(content, lexer, formatter)

    if not isinstance(formatter, HtmlFormatter):
        return content

    template = render_template("generic.html", cc='container-fluid', content=content, **style_args())

    return template

def _content_type():
    content_type = http.parse_options_header(request.headers.get('Content-Type', ''))
    if content_type:
        content_type, _ = content_type
        return content_type

def request_content():
    content = request_key('content')
    if content:
        content = BytesIO(content.encode('utf-8'))
        return content, request_key('filename')

    fs = request.files.get('content', request.files.get('c'))
    if fs:
        return fs.stream, request_key('filename') or fs.filename

def request_keys(*keys):
    for key in keys:
        value = request_key(key)
        if value:
            yield key, value

def request_key(key):
    if _content_type() == 'application/json':
        return request.json.get(key, request.json.get(key[0]))
    return request.form.get(key, request.form.get(key[0]))

def absolute_url(endpoint, **kwargs):
    proto = request.environ.get('HTTP_X_FORWARDED_PROTO')
    scheme = proto if proto else request.scheme
    return url_for(endpoint, _external=True, _scheme=scheme, **kwargs)

def rst(source):
    overrides = {'syntax_highlight': 'short'}
    parts = core.publish_parts(source, writer_name='html', settings_overrides=overrides)
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

def get_host_name(request):
    if not request:
        return
    host = get_host(request.environ)
    if host:
        host = host.split(':')[0]
        return host
