from time import time

from flask import url_for
from yaml import load

from pb.pb import create_app


def test_paste_render():
    app = create_app()

    rv = app.test_client().post('/', data=dict(
        c=str(time())
    ))

    data = load(rv.get_data())
    with app.test_request_context():
        nurl = url_for('paste.get', label=data['short'], lexer='')
        iurl = url_for('paste.get', label=data['short'], lexer='bogus')
        lurl = url_for('paste.get', label=data['short'], lexer='pycon')

    rv1 = app.test_client().get(nurl)
    rv2 = app.test_client().get(iurl)
    rv3 = app.test_client().get(lurl)

    assert rv1.status_code == 200
    assert rv2.status_code == 400
    assert rv3.status_code == 200
