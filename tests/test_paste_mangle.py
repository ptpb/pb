from time import time
from os import path
from urllib import parse

from flask import url_for

from pb.pb import create_app
from pb.util import b66_int

def test_paste_mangle():
    app = create_app()

    with app.test_request_context():
        url = url_for('paste.post')

    rv = app.test_client().post(url, data=dict(
        c = str(time())
    ))

    location = rv.headers.get('Location') 
    url_path = parse.urlsplit(location).path
    id = b66_int(path.split(url_path)[-1])

    assert id != 0

    tests = [
        ({'lexer': 'py'}, 200),
        ({'lexer': ''}, 200),
        ({'lexer': 'buhLang'}, 400),
        ({'handler': 'r'}, 200),
        ({'handler': 'Z'}, 400)
    ]

    for kwargs, code in tests:
        with app.test_request_context():
            url = url_for('paste.get', b66=id, **kwargs)

        rv = app.test_client().get(url)
        assert rv.status_code == code
