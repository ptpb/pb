from os import path
from base64 import urlsafe_b64encode, urlsafe_b64decode, b85encode, b85decode
from bitstring import Bits
import binascii

from urllib.parse import quote, unquote

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

def id_b85(id):
    b85 = b85encode(Bits(length=16, int=int(id)).bytes)
    return quote(b85)

def b85_id(b85):
    b85 = unquote(b85)
    return Bits(bytes=b85decode(b85)).int

def id_url(**kwargs):
    return url_for('.get', _external=True, _scheme='https', **kwargs)
