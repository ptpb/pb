from flask import Flask, Response, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import BINARY
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

    id = db.Column(BINARY(6), primary_key=True, unique=True)
    digest = db.Column(BINARY(16), index=True, unique=True)
    content = db.Column(db.Text(length=16777216, collation='utf8_general_ci'))

    def __init__(self, id, digest, content):
        self.id = id
        self.digest = digest
        self.content = content

db.create_all()
db.session.commit()

def make_id():
    while True:
        id = urandom(6)
        p = Paste.query.filter_by(id=id).all()
        if not p:
            return id

def get_digest(c):
    m = hashlib.md5()
    m.update(c)
    digest = m.digest()
    return Paste.query.filter_by(digest=digest).first(), digest

def redirect(location, rv):
    response = TextResponse(rv, 302)
    response.headers['Location'] = location
    return response

@app.route('/', methods=['GET', 'POST'])
@app.route('/f', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return Response(render_template("form.html" if 'f' in request.path else "index.html"), mimetype='text/html')
    elif request.method == "POST":
        if 'c' in request.form:
            p, digest = get_digest(request.form['c'])
            if not p:
                p = Paste(make_id(), digest, request.form['c'])
                db.session.add(p)
                db.session.commit()

            #url = url_for('paste', _external=True, id=p.id)
            url = "https://ptpb.pw/p/{}".format(b64encode(p.id))
            return redirect(url, "{}\n".format(url))
        
    return "Nope.", 204

@app.route('/p/<id>', methods=['GET'])
def paste(id):
    p = Paste.query.filter_by(id=b64decode(id.encode('utf-8'))).first()
    if p:
        return p.content
    return "Not found.", 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=10002)
