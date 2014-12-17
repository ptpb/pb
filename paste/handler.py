from flask import Response
from docutils import core

def render(content):
    parts = core.publish_parts(content, writer_name='html')
    return Response(parts['html_body'], mimetype='text/html')

handlers = {
    'r': render
}

def get(handler, content):
    h = handlers.get(handler)
    if not h:
        return "Invalid handler: '{}'.".format(handler), 400
    return h(content)
