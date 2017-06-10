from time import time

from flask import url_for
import pytest
from yaml import load


lexer_tests = [
    ('py', 200),
    ('', 200),
    ('fake_test', 400),
]

handler_tests = [
    ('r', 200),
]


@pytest.fixture()
def digest(app):
    with app.test_request_context():
        url = url_for('paste.post')

    rv = app.test_client().post(url, data=dict(
        c=str(time())
    ))

    data = load(rv.get_data())
    return data['digest']


@pytest.mark.parametrize("lexer,code", lexer_tests)
def test_paste_lexer(app, digest, lexer, code):
    with app.test_request_context():
        url = url_for('paste.get', sha1=digest, lexer=lexer)

    rv = app.test_client().get(url)
    assert rv.status_code == code


@pytest.mark.parametrize("handler,code", handler_tests)
def test_paste_handler(app, digest, handler, code):
    with app.test_request_context():
        url = url_for('paste.get', handler=handler, sha1=digest)

    rv = app.test_client().get(url)
    assert rv.status_code == code
