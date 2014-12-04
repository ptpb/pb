from flask import Response, render_template, current_app, request

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

    return Response(render_template('highlight.html', content=content), mimetype='text/html')

def request_content():
    raw = 'application/x-www-form-urlencoded' in request.headers.get('Content-Type')

    if not raw and 'c' in request.form:
        return request.form['c'].encode('utf-8'), raw
    elif raw:
        return request.stream.read(), raw

    return None, raw
