from os import path
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

from urllib.parse import urljoin, urlsplit
from requests.sessions import Session

from werkzeug.wrappers import get_host
from flask import request, current_app, g

def get_session():
    s = getattr(g, '_session', None)
    if s is None:
        s = g._session = Session()
        s.executor = ThreadPoolExecutor(4)
    return s

def invalidate(url):

    base = current_app.config.get('VARNISH_BASE')
    if not base:
        return
    s = get_session()

    url = urlsplit(url).path
    url = path.splitext(url.split('/')[1])[0]
    url = urljoin(base, '/{}.*'.format(url))
    headers = {'Host': get_host(request.environ)}

    return s.executor.submit(s.request, 'BAN', url, headers=headers)

def init_cache(app):
    @app.teardown_appcontext
    def teardown_cache(exception):
        s = getattr(g, '_session', None)
        if s is not None:
            s.executor.shutdown()
