from functools import wraps
from contextlib import closing

from flask import g, request, current_app
from mysql import connector

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connector.connect(autocommit=True, raw=True, **current_app.config['MYSQL'])
    return db

def cursor(f):
    @wraps(f)
    def cursor_func(*args, **kwargs):
        with closing(get_db().cursor()) as request.cur:
            return f(*args, **kwargs)
    return cursor_func

def init_db(app):
    @app.teardown_appcontext
    def teardown_db(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()
