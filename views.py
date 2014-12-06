from uuid import UUID
from mimetypes import guess_type

from flask import Blueprint, Response, request, render_template, current_app, url_for
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_all_lexers

from db import cursor
from model import insert_paste, put_paste, delete_paste, get_stats, get_digest, get_content
from util import highlight, redirect, request_content, get_id_url, pid_id

view = Blueprint('view', __name__)

@view.route('/')
def index():
    return Response(render_template("index.html"), mimetype='text/html')

@view.route('/f')
def form():
    return Response(render_template("form.html"), mimetype='text/html')

@view.route('/', methods=['POST'])
@cursor
def post():
    content, filename = request_content()
    if not content:
        return "Nope.\n", 400

    id, uuid = get_digest(content)
    if not id:
        id, uuid = insert_paste(content)

    url = get_id_url(id, filename)
    uuid = UUID(bytes=uuid) if uuid else '[redacted]'
    return redirect(url, "{}\nuuid: {}\n".format(url, uuid))

@view.route('/<uuid>', methods=['PUT'])
@cursor
def put(uuid):
    content, filename = request_content()
    if not content:
        return "Nope.\n", 400

    uuid = UUID(uuid).bytes

    id, _ = get_digest(content)
    if id:
        url = get_id_url(id, None)
        return redirect(url, "Paste already exists.\n", 409)

    count = int(put_paste(uuid, content))
    if count:
        # FIXME: geif Location
        return "{} pastes updated.\n".format(count), 200

    return "Not found.\n", 404

@view.route('/<uuid>', methods=['DELETE'])
@cursor
def delete(uuid):
    uuid = UUID(uuid).bytes
    count = int(delete_paste(uuid))
    if count:
        return "{} pastes deleted.\n".format(count), 200
    return "Not found.\n", 404

@view.route('/<id>')
@view.route('/<id>/<lexer>')
@cursor
def get(id, lexer=None):
    mimetype, _ = guess_type(id)
    id = pid_id(id)
    if not id:
        return "Invalid id.\n", 400

    content = get_content(id)
    if not content:
        return "Not found.\n", 404

    if lexer:
        return highlight(content, lexer)
    elif mimetype:
        return Response(content, mimetype=mimetype)

    return content

@view.route('/s')
@cursor
def stats():
    count, length = get_stats()
    return "{} pastes\n{} bytes\n".format(count, length)

@view.route('/static/highlight.css')
def highlight_css():
    css = HtmlFormatter().get_style_defs('.highlight')
    return Response(css, mimetype='text/css')

@view.route('/l')
def list_lexers():
    lexers = '\n'.join(' '.join(i) for _, i, _, _ in get_all_lexers())
    return '{}\n'.format(lexers)
