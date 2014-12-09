from os import path
import string
from base64 import urlsafe_b64encode, urlsafe_b64decode
from bitstring import Bits
import binascii

from flask import Response, render_template, current_app, request, url_for

from pygments import highlight as _highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

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

def id_b64(id, filename=None):
    b64 = urlsafe_b64encode(Bits(length=24, int=int(id)).bytes)
    ext = path.splitext(filename)[1] if filename else None
    return b''.join((b64, ext.encode('utf-8'))) if ext else b64

def b64_id(b64):
    root, _ = path.splitext(b64)

    try:
        return Bits(bytes=urlsafe_b64decode(root)).int
    except binascii.Error:
        pass

def int_b36(i):
    char_set = string.digits + string.ascii_lowercase
    if i < 36:
        return char_set[i]
    b36 = ''
    while i != 0:
        i, n = divmod(i, 36)
        b36 = char_set[n] + b36
    return b36

def id_url(**kwargs):
    return url_for('.get', _external=True, _scheme='https', **kwargs)
