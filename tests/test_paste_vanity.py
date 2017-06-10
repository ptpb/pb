from time import time

from flask import url_for
from yaml import load

from pb.pb import create_app


def test_paste_vanity():
    app = create_app()

    c = str(time())
    rv = app.test_client().post('/~foo1234', data=dict(
        c=c
    ))

    data = load(rv.get_data())
    assert 'foo1234' in data['url']

    rv = app.test_client().get(data['url'])
    assert rv.status_code == 200
    assert rv.get_data() == c.encode('utf-8')

    with app.test_request_context():
        url = url_for('paste.put', uuid=data.get('uuid'))

    rv = app.test_client().put(url, data=dict(
        c=str(time())
    ))
    assert rv.status_code == 200

    rv = app.test_client().delete(url)
    assert rv.status_code == 200
