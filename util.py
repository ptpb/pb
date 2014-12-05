from os import path
from base64 import urlsafe_b64encode, urlsafe_b64decode
from bitstring import Bits

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

    content = _highlight(content, lexer, HtmlFormatter())
    lines = range(1, sum(1 for line in content.splitlines()))
    template = render_template('highlight.html', content=content, lines=lines)

    return Response(template, mimetype='text/html')

def request_content():

    if 'application/x-www-form-urlencoded' in request.headers.get('Content-Type'):
        return request.stream.read(), None

    c = request.form.get('c')
    if c:
        return c.encode('utf-8'), None
    fs = request.files.get('c')
    if fs:
        return fs.stream.read(), fs.filename

    return None, None

def id_pid(id, filename):
    pid = urlsafe_b64encode(Bits(length=24, uint=int(id)).bytes)
    ext = path.splitext(filename)[1] if filename else None
    return b''.join((pid, ext.encode('utf-8'))) if ext else pid

def pid_id(pid):
    root, _ = path.splitext(pid)
    return Bits(bytes=urlsafe_b64decode(root)).int

def get_id_url(id, filename):
    pid = id_pid(id, filename)
    return url_for('.get', id=pid, _external=True)
