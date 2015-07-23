from flask import url_for
from time import time, sleep

from yaml import load
from pb.pb import create_app

def test_paste_sunset():
    app = create_app()

    rv = app.test_client().post('/', data=dict(
        c = str(time()),
        s = 1
    ))

    data = load(rv.get_data())
    with app.test_request_context():
        url = url_for('paste.get', label=data['short'])

    sleep(1)

    rv = app.test_client().get(url)
    data = load(rv.get_data())

    assert data['status'] == 'expired'

    rv = app.test_client().get(url)

    assert rv.status_code == 404
