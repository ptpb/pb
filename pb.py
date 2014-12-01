from flask import Flask, Response, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import BINARY, MEDIUMBLOB, TINYINT
import yaml
from datetime import datetime
from os import urandom, path
from base64 import urlsafe_b64encode as b64encode, urlsafe_b64decode as b64decode
import hashlib

class TextResponse(Response):
    default_mimetype = 'text/plain'

def load_yaml(app, filename):
    filename = path.join(app.root_path, filename)
    with open(filename) as f:
        obj = yaml.load(f)

    return app.config.from_mapping(obj)

app = Flask(__name__)
app.response_class = TextResponse
load_yaml(app, 'config.yaml')

db = SQLAlchemy(app)

class Paste(db.Model):
    __tablename__ = "paste"

    id = db.Column(BINARY(6), primary_key=True, unique=True, nullable=False)
    digest = db.Column(BINARY(20), index=True, unique=True, nullable=False)
    content = db.Column(MEDIUMBLOB(), nullable=False)
    raw = db.Column(TINYINT(), nullable=False)

    def __init__(self, id, digest, content, raw):
        self.id = id
        self.digest = digest
        self.content = content
        self.raw = raw

db.create_all()
db.session.commit()

def make_id():
    while True:
        id = urandom(6)
        p = Paste.query.filter_by(id=id).all()
        if not p:
            return id

def get_digest(c):
    m = hashlib.new('sha1')
    m.update(c)
    digest = m.digest()
    return Paste.query.filter_by(digest=digest).first(), digest

def redirect(location, rv):
    response = TextResponse(rv, 302)
    response.headers['Location'] = location
    return response

def make_paste(content, raw):
    p, digest = get_digest(content)
    if not p:
        p = Paste(make_id(), digest, content, raw)
        db.session.add(p)
        db.session.commit()

    #url = url_for('paste', _external=True, id=p.id)
    url = "https://ptpb.pw/p/{}".format(b64encode(p.id))
    return redirect(url, "{}\n".format(url))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return Response(render_template("index.html"), mimetype='text/html')
    elif request.method == "POST":
        if 'c' in request.form:
            return make_paste(request.form['c'].encode('utf-8'), 0)
    return "Nope.", 204

@app.route('/r', methods=['POST'])
def stream():
    return make_paste(request.stream.read(), 1)

@app.route('/f')
def form():
    return Response(render_template("form.html"), mimetype='text/html')

@app.route('/p/<id>')
def paste(id):
    p = Paste.query.filter_by(id=b64decode(id.encode('utf-8'))).first()
    if p and p.raw:
        return Response(p.content, mimetype='application/octet-stream')
    if p:
        return p.content
    return "Not found.", 404

@app.route('/s')
def stats():
    p = Paste.query.count()
    return "We have {} pastes.".format(p)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=10002)
