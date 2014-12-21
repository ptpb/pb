from time import time, monotonic
from io import BytesIO
from os import urandom

from pb.pb import create_app

def test_post_content():
    app = create_app()

    rv = app.test_client().post('/')
    assert rv.status_code == 400

    rv = app.test_client().post('/', data=dict(
        c = str(time())
    ))
    assert rv.status_code == 302

    location = rv.headers.get('Location')
    assert location

    rv = app.test_client().get(location)
    assert rv.status_code == 200

def test_post_file():
    app = create_app()

    c = urandom(24)
    ext = int(time())
    rv = app.test_client().post('/', data=dict(
        c = (BytesIO(c), 'foo.{}'.format(ext))
    ))

    location = rv.headers.get('Location')
    assert '.{}'.format(ext) in location

    rv = app.test_client().get(location)
    assert c == rv.get_data()

def test_post_unqiue():
    app = create_app()

    f = lambda c: app.test_client().post('/', data=dict(
        c = str(c)
    ))

    rv1 = f(monotonic())
    rv2 = f(monotonic())

    assert rv1.headers.get('Location') != rv2.headers.get('Location')

    c = time()
    rv1 = f(c)
    rv2 = f(c)

    assert rv1.headers.get('Location') == rv2.headers.get('Location')

def test_get_mimetype():
    app = create_app()

    rv = app.test_client().post('/', data=dict(
        c = str('ello')
    ))

    rv = app.test_client().get('{}.py'.format(rv.headers.get('Location')))

    assert 'text/x-python' in rv.headers.get('Content-Type')
