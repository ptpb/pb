from time import time

from flask import url_for
from yaml import load

from pb.pb import create_app

def test_put():
    app = create_app()

    t1 = time()
    rv = app.test_client().post('/', data=dict(
        c = str(t1)
    ))
    data = load(rv.get_data())

    assert data.get('uuid')
    assert data.get('url')
    assert 'redacted' not in data.get('uuid')

    with app.test_request_context():
        url = url_for('paste.put', uuid=data.get('uuid'))
        
    f = lambda c: app.test_client().put(url, data=dict(
        c = str(c) if c else c
    ))

    rv = f(None)
    assert rv.status_code == 400

    rv = f(t1)
    assert rv.status_code == 409

    t2 = time()
    rv = f(t2)
    assert rv.status_code == 200

    rv = app.test_client().get(data.get('url'))
    assert rv.get_data().decode('utf-8') == str(t2)

def test_delete():
    app = create_app()

    rv = app.test_client().post('/', data=dict(
        c = 'delete me KU7cC3JBrz0jMXYRCWsZ6YGa/YTYIZWw'
    ))
    data = load(rv.get_data())
    assert 'redacted' not in data.get('uuid')

    with app.test_request_context():
        url = url_for('paste.delete', uuid=data.get('uuid'))

    rv = app.test_client().delete(url)
    assert rv.status_code == 200
    
    rv = app.test_client().delete(url)
    assert rv.status_code == 404

    with app.test_request_context():
        url = url_for('paste.put', uuid=data.get('uuid'))

    rv = app.test_client().put(url, data=dict(
        c = str(time())
    ))
    assert rv.status_code == 404
