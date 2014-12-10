from os import path

from flask import Response, render_template, current_app, request, url_for

from pygments import highlight as _highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

b66c = 'QwdJxskgt6BE.levhL0zWNj8~1P_ZbHDq7YrpGOIX5CyimfK-cMoAR49FaUn3VT2Su'

def redirect(location, rv, code=302):
    response = current_app.response_class(rv, code)
    response.headers['Location'] = location
    return response

def highlight(content, lexer):
    try:
        lexer = get_lexer_by_name(lexer)
    except ClassNotFound:
        return "No such lexer.", 400

    content = _highlight(content, lexer, HtmlFormatter(linenos='table', anchorlinenos=True, lineanchors='L', linespans='L'))
    template = render_template('highlight.html', content=content)

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
    ext = path.splitext(filename)[1] if filename else None
    return '{:{zero}>{length}}'.format(''.join(b66, ext) if ext else b66, length=length, zero=b66c[0])

def b66_int(s):
    return sum(b66c.index(c) * len(b66c) ** (len(s) - i - 1) for i, c in enumerate(s))

def id_url(**kwargs):
    return url_for('.get', _external=True, _scheme='https', **kwargs)
