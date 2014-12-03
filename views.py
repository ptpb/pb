import uuid

from flask import Blueprint, Response, request, render_template, current_app, url_for

from db import cursor
from model import insert_paste, get_stats, get_digest, get_content

view = Blueprint('view', __name__)

def redirect(location, rv):
    response = current_app.response_class(rv, 302)
    response.headers['Location'] = location
    return response

@view.route('/', methods=['GET', 'POST'])
@view.route('/r', methods=['POST'])
@cursor
def index():
    if request.method == "GET":
        return Response(render_template("index.html"), mimetype='text/html')
    elif request.method == "POST":
        raw = 'r' in request.path
        if not raw and 'c' in request.form:
            content = request.form['c'].encode('utf-8')
        elif raw:
            content = request.stream.read()
        else:
            return "Nope.", 400

        id = get_digest(content)
        if not id:
            id = insert_paste(content, raw)

        pid = uuid.UUID(bytes=bytes(id))
        url = url_for('.paste', id=pid, _external=True)
        return redirect(url, "{}\n".format(url))

@view.route('/f')
def form():
    return Response(render_template("form.html"), mimetype='text/html')

@view.route('/p/<id>')
@cursor
def paste(id):
    try:
        id = uuid.UUID(id).bytes
    except ValueError:
        return "Invalid id.", 400

    content, raw = get_content(id)
    if not content:
        return "Not found.", 404

    if int(raw):
        return Response(content, mimetype='application/octet-stream')
    else:
        return content

@view.route('/s')
@cursor
def stats():
    count, length = get_stats()
    return "{} pastes\n{} bytes\n".format(count, length)
