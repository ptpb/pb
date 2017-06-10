from flask import url_for
from time import time

from yaml import load
from pb.pb import create_app


def test_paste_render():
    app = create_app()

    rv = app.test_client().post('/', data=dict(
        c=str(time())
    ))

    data = load(rv.get_data())
    with app.test_request_context():
        url = url_for('paste.get', handler='r', label=data['short'])

    rv = app.test_client().get(url)
    assert rv.status_code == 200
