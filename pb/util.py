# -*- coding: utf-8 -*-
"""
    util
    ~~~~

    Utility functions.

    :copyright: Copyright (C) 2014 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from os import path

from flask import Response, render_template, current_app, request, url_for

from pygments import highlight as _highlight, format as _format
from pygments.token import Token
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

from docutils import core

b66c = 'QwdJxskgt6BE.levhL0zWNj8~1P_ZbHDq7YrpGOIX5CyimfK-cMoAR49FaUn3VT2Su'

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

def int_b66(length, i, filename=None):
    b66 = ''
    while i != 0:
        i, n = divmod(i, len(b66c))
        b66 = b66c[n] + b66
    ext = path.splitext(filename)[1] if filename else ''
    return '{:{zero}>{length}}{ext}'.format(b66, ext=ext, length=length, zero=b66c[0])

def b66_int(s):
    return sum(b66c.index(c) * len(b66c) ** (len(s) - i - 1) for i, c in enumerate(s))

def id_url(**kwargs):
    proto = request.environ.get('HTTP_X_FORWARDED_PROTO')
    scheme = proto if proto else request.scheme
    return url_for('.get', _external=True, _scheme=scheme, **kwargs)

def any_url(id, digest, label, **kwargs):
    if id:
        return id_url(b66=id, **kwargs)
    if digest:
        return id_url(sha1=digest, **kwargs)
    if label:
        return id_url(label=label, **kwargs)

def publish_parts(source):
    overrides = {'syntax_highlight': 'short'}
    parts = core.publish_parts(source, writer_name='html', settings_overrides=overrides)
    return parts['html_body']
