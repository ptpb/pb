from time import time
from hashlib import sha1

from flask import url_for

from pb.pb import create_app

def test_get_digest():
    app = create_app()

    c = str(time())
    app.test_client().post('/', data=dict(
        c = c
    ))

    hexdigest = sha1(c.encode('utf-8')).hexdigest()
    with app.test_request_context():
        url = url_for('paste.get', sha1=hexdigest)

    rv = app.test_client().get(url)
    assert rv.status_code == 200
