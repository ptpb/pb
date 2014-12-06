from os import path
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

from hashlib import sha1

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

def add_cache_header(response):
    if request.method == 'GET' and not response.cache_control.public:
        etag = sha1(response.data).hexdigest()
        response.add_etag(etag)
        response.cache_control.public = True
        response.cache_control.max_age = current_app.get_send_file_max_age(request.path)
        response.make_conditional(request)

    return response

def invalidate_cache(response):
    location = response.headers.get('Location')
    if location:
        invalidate(location)
    return response

def teardown_cache(exception):
    s = getattr(g, '_session', None)
    if s is not None:
        s.executor.shutdown()

def init_cache(app):
    app.teardown_appcontext(teardown_cache)
    app.after_request(add_cache_header)
    app.after_request(invalidate_cache)
