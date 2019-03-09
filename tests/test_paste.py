from io import BytesIO
from os import urandom
from time import monotonic, time

import pytest
from yaml import load

from pb.pb import create_app


@pytest.mark.parametrize("field_name", [
    "content",
    "c",
    "file"
])
def test_post_content(field_name):
    app = create_app()

    rv = app.test_client().post('/')
    assert rv.status_code == 400

    content = str(time())
    rv = app.test_client().post('/', data={
        field_name: content
    })
    assert rv.status_code == 200

    data = load(rv.get_data())
    assert data['url']

    rv = app.test_client().get(data['url'])
    assert rv.status_code == 200
    assert rv.get_data() == content.encode('utf-8')


@pytest.mark.parametrize("field_name", [
    "content",
    "c",
    "file"
])
def test_post_file(field_name):
    app = create_app()

    content = urandom(24)
    ext = int(time())
    rv = app.test_client().post('/', data={
        field_name: (BytesIO(content), 'foo.{}'.format(ext))
    })

    data = load(rv.get_data())
    assert '.{}'.format(ext) in data['url']

    rv = app.test_client().get(data['url'])
    assert rv.get_data() == content


def test_post_unique():
    app = create_app()

    def f(c):
        return app.test_client().post('/', data=dict(
            c=str(c)
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
        c=str('ello')
    ))

    rv = app.test_client().get('{}.py'.format(load(rv.get_data())['url']))

    assert 'text/x-python' in rv.headers.get('Content-Type')
