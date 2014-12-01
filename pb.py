from flask import Flask, Response, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy

import yaml
from datetime import datetime
from os import urandom, path
from base64 import urlsafe_b64encode as b64encode
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

    content = db.Column(db.Text(length=16777216, collation='utf8_general_ci'))
    date = db.Column(db.DateTime)
    hash = db.Column(db.String(32))
    id = db.Column(db.String(9), primary_key=True, unique=True)

    def __init__(self, content, date, id, hash):
        self.content = content
        self.date = date
        self.id = id
        self.hash = hash

db.create_all()
db.session.commit()

def make_id():
    while True:
        id = b64encode(urandom(6))
        p = Paste.query.filter_by(id=id).all()
        if not p:
            return id

def get_hash(c):
    m = hashlib.md5()
    m.update(c)
    digest = m.hexdigest()
    return Paste.query.filter_by(hash=digest).first(), digest

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
            p, digest = get_hash(request.form['c'])
            if not p:
                p = Paste(request.form['c'], datetime.now(), make_id(), digest)
                db.session.add(p)
                db.session.commit()

            #url = url_for('paste', _external=True, id=p.id)
            url = "https://ptpb.pw/p/{}".format(p.id)
            return redirect(url, "{}\n".format(url))
        
    return "Nope.", 204

@app.route('/p/<id>', methods=['GET'])
def paste(id):
    p = Paste.query.filter_by(id=id).first()
    if p:
        return p.content
    return "Not found.", 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=10002)
