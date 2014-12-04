from bitstring import Bits
from base64 import urlsafe_b64encode, urlsafe_b64decode
from uuid import UUID

from flask import Blueprint, Response, request, render_template, current_app, url_for

from db import cursor
from model import insert_paste, put_paste, delete_paste, get_stats, get_digest, get_content
from util import highlight, redirect, request_content

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
    content, raw = request_content()
    if not content:
        return "Nope.", 400

    id, uuid = get_digest(content)
    if not id:
        id, uuid = insert_paste(content, raw)

    pid = urlsafe_b64encode(Bits(length=24, uint=int(id)).bytes)
    url = url_for('.get', id=pid, _external=True)
    uuid = UUID(bytes=uuid) if uuid else '[redacted]'
    return redirect(url, "{}\nuuid: {}\n".format(url, uuid))

@view.route('/<uuid>', methods=['PUT'])
@cursor
def put(uuid):
    content, raw = request_content()
    if not content:
        return "Nope.", 400

    uuid = UUID(uuid).bytes

    id, _ = get_digest(content)
    if not id:
        count = int(put_paste(uuid, content))
        return "{} pastes updated.\n".format(count), 200

    pid = urlsafe_b64encode(Bits(length=24, uint=int(id)).bytes)
    url = url_for('.get', id=pid, _external=True)

    return redirect(url, "Paste already exists.\n", 409)

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
    id = Bits(bytes=urlsafe_b64decode(id)).int

    content, raw = get_content(id)
    if not content:
        return "Not found.", 404

    if lexer:
        return highlight(content, lexer)
    elif int(raw):
        return Response(content, mimetype='application/octet-stream')

    return content

@view.route('/s')
@cursor
def stats():
    count, length = get_stats()
    return "{} pastes\n{} bytes\n".format(count, length)
