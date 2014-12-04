from bitstring import Bits
from base64 import urlsafe_b64encode, urlsafe_b64decode
from uuid import UUID

from flask import Blueprint, Response, request, render_template, current_app, url_for

from db import cursor
from model import insert_paste, get_stats, get_digest, get_content
from util import highlight, redirect

view = Blueprint('view', __name__)

@view.route('/')
def index():
    return Response(render_template("index.html"), mimetype='text/html')

@view.route('/f')
def form():
    return Response(render_template("form.html"), mimetype='text/html')

@view.route('/', methods=['POST'])
@view.route('/r', methods=['POST'])
@cursor
def post():
    raw = request.path == '/r'
    if not raw and 'c' in request.form:
        content = request.form['c'].encode('utf-8')
    elif raw:
        content = request.stream.read()
    else:
        return "Nope.", 400

    id, uuid = get_digest(content)
    if not id:
        id, uuid = insert_paste(content, raw)

    pid = urlsafe_b64encode(Bits(length=24, uint=int(id)).bytes)
    url = url_for('.paste', id=pid, _external=True)
    uuid = UUID(bytes=uuid) if uuid else '[redacted]'
    return redirect(url, "{}\nuuid: {}\n".format(url, uuid))

@view.route('/<id>')
@view.route('/<id>/<lexer>')
@cursor
def paste(id, lexer=None):
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
