from os import path
from time import time
from urllib import parse

from flask import url_for

from pb.pb import create_app

shorturl = 'https://google.com'


def test_url_post():
    app = create_app()

    with app.test_request_context():
        url = url_for('paste.url')

    rv = app.test_client().post(url)
    assert rv.status_code == 400

    f = lambda c: app.test_client().post(url, data=dict(
        c=str(c)
    ))
    rv = f(shorturl)
    assert rv.status_code == 200

    rv = f(time())
    assert rv.status_code == 200


def test_url_get():
    app = create_app()

    with app.test_request_context():
        url = url_for('paste.url')

    rv = app.test_client().post(url, data=dict(
        c=str(time())
    ))
    location = rv.headers.get('Location')
    assert location

    rv = app.test_client().get(location)
    assert rv.status_code == 302

    # FIXME
    #url_path = parse.urlsplit(location).path
    #id = b66_int(path.split(url_path)[-1])
    #assert id != 0

    #with app.test_request_context():
    #    url = url_for('url.get', b66=id+10)

    #rv = app.test_client().get(url)
    #assert rv.status_code == 404
