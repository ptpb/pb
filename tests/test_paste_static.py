from flask import url_for

from pb.pb import create_app

def test_get_index():
    app = create_app()

    with app.test_request_context():
        rv = app.test_client().get(url_for('paste.index'))
        assert rv.status_code == 200

def test_get_form():
    app = create_app()

    with app.test_request_context():
        url = url_for('paste.form')

    rv = app.test_client().get(url)
    assert rv.status_code == 200

def test_get_stats():
    app = create_app()

    with app.test_request_context():
        url = url_for('paste.stats')

    rv = app.test_client().get(url)
    assert rv.status_code == 200

def test_get_css():
    app = create_app()

    with app.test_request_context():
        url = url_for('paste.highlight_css', style='default')

    rv = app.test_client().get(url)
    assert rv.status_code == 200

def test_get_lexers():
    app = create_app()

    with app.test_request_context():
        url = url_for('paste.list_lexers')

    rv = app.test_client().get(url)
    assert rv.status_code == 200
