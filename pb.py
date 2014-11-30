from flask import *
from flask.ext.sqlalchemy import SQLAlchemy

from credentials import *

import datetime
import os
import hashlib

app = Flask(__name__)
connectionString = "mysql://%s:%s@%s:3306/%s" % (USERNAME, PASSWORD, HOSTNAME, DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = connectionString
db = SQLAlchemy(app)
app.secret_key = SECRET_KEY

class Paste(db.Model):
    __tablename__ = "paste"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    date = db.Column(db.DateTime)
    url = db.Column(db.String(25))

    def __init__(self, content, date, url):
        self.content = content
        self.date = date
        self.url = url

db.create_all()
db.session.commit()

def make_url():
    url = os.urandom(128)
    url = hashlib.md5(url).hexdigest()[:8]
    p = Paste.query.filter_by(url=url).all()
    if p:
        url = os.urandom(128)
        url = hashlib.md5(url).hexdigest()[:8]
        return url
    else:
        return url

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        if 'content' in request.form:
            try:
                p = Paste(request.form['content'], datetime.datetime.now(), make_url())
                db.session.add(p)
                db.session.commit()
                db.session.refresh(p)
            except:
                return "Failed." 

            return "http://ptpb.pw/p/%s\n" % p.url
    else:
        return "Nope."

@app.route('/p/<paste>', methods=['GET'])
def paste(paste):
    if paste:
        p = Paste.query.filter_by(url=paste).first()
        return render_template("paste.html", paste=p)
    else:
        return "Not found."

@app.route('/f', methods=['GET','POST'])
def form():
    if request.method == "GET":
        return render_template("form.html")
    elif request.method == "POST":
        if 'content' in request.form:
            try:
                p = Paste(request.form['content'], datetime.datetime.now(), make_url())
                db.session.add(p)
                db.session.commit()
                db.session.refresh(p)
            except Exception, e:
                return "Failed. %s" % str(e)

            return redirect('/p/%s' % p.url)
    else:
        return "Nope."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10002, debug=True)
