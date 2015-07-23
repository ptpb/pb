from time import time, monotonic
from io import BytesIO
from os import urandom, path
from urllib import parse

from yaml import load
from flask import url_for

from pb.pb import create_app

def test_post_content():
    app = create_app()

    rv = app.test_client().post('/')
    assert rv.status_code == 400

    rv = app.test_client().post('/', data=dict(
        c = str(time())
    ))
    assert rv.status_code == 200

    data = load(rv.get_data())
    assert data['url']

    rv = app.test_client().get(data['url'])
    assert rv.status_code == 200

def test_post_file():
    app = create_app()

    c = urandom(24)
    ext = int(time())
    rv = app.test_client().post('/', data=dict(
        c = (BytesIO(c), 'foo.{}'.format(ext))
    ))

    data = load(rv.get_data())
    assert '.{}'.format(ext) in data['url']

    rv = app.test_client().get(data['url'])
    assert c == rv.get_data()

def test_post_unique():
    app = create_app()

    f = lambda c: app.test_client().post('/', data=dict(
        c = str(c)
    ))

    rv1 = f(monotonic())
    rv2 = f(monotonic())

    assert load(rv1.get_data())['url'] != load(rv2.get_data())['url']

    c = time()
    rv1 = f(c)
    rv2 = f(c)

    assert load(rv1.get_data())['url'] == load(rv2.get_data())['url']

def test_get_mimetype():
    app = create_app()

    rv = app.test_client().post('/', data=dict(
        c = str('ello')
    ))

    rv = app.test_client().get('{}.py'.format(load(rv.get_data())['url']))

    assert 'text/x-python' in rv.headers.get('Content-Type')
