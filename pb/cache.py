# -*- coding: utf-8 -*-
"""
    cache
    ~~~~~

    manipulate server-side and client browser caches.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from os import path
from functools import wraps
from concurrent.futures import ThreadPoolExecutor

from hashlib import sha1

from urllib.parse import urljoin, urlsplit
from requests.sessions import Session

from werkzeug.wrappers import get_host
from flask import request, current_app, g

from pb.paste import model

_methods = {
    'sid': 'digest',
    'sha1': 'digest',
    'label': 'label'
}

def all_urls(paste):
    for key, value in _methods.items():
        if value in paste:
            if key == 'sha1':
                yield paste[value]
                continue
            conv = current_app.url_map.converters[key]
            yield conv.to_url(None, paste[value], 6)

def get_session():
    s = getattr(g, '_session', None)
    if s is None:
        s = g._session = Session()
        s.executor = ThreadPoolExecutor(4)
    return s

def invalidate(**kwargs):
    cur = model.get_meta(**kwargs)
    if not cur or not cur.count():
        return
    paste = next(cur)

    base = current_app.config.get('VARNISH_BASE')
    if not base:
        return paste

    s = get_session()

    for url in all_urls(paste):
        url = urljoin(base, '/.*{}.*'.format(url))
        headers = {'Host': get_host(request.environ)}
        s.executor.submit(s.request, 'BAN', url, headers=headers)

    return paste

def add_cache_header(response):
    if not response._etag:
        return response
    if request.method == 'GET' and not response.cache_control.public:
        prefix = request.blueprint if request.blueprint else current_app.name
        # ugh
        etag = "{}-{}".format(prefix, sha1(response.data).hexdigest())
        response.set_etag(etag)
        response.cache_control.public = True
        if hasattr(request, 'max_age'):
            response.cache_control.max_age = request.max_age
        else:
            response.cache_control.max_age = current_app.get_send_file_max_age(request.path)
        response.make_conditional(request)
    return response

def teardown_cache(exception):
    s = getattr(g, '_session', None)
    if s is not None:
        s.executor.shutdown()

def init_cache(app):
    app.teardown_appcontext(teardown_cache)
    app.after_request(add_cache_header)
