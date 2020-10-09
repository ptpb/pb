# -*- coding: utf-8 -*-
"""
    paste.views
    ~~~~~~~~~~~

    paste url routes and views.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from datetime import datetime
from io import BytesIO
from mimetypes import guess_type
from uuid import UUID

from flask import Blueprint, render_template, request
from pygments.formatters import HtmlFormatter, get_all_formatters
from pygments.styles import get_all_styles
from pygments.util import ClassNotFound
from pymongo import errors

from pb.cache import invalidate
from pb.lexers import get_lexer_aliases
from pb.namespace import model as ns_model
from pb.paste import handler as _handler
from pb.paste import model
from pb.responses import (BaseResponse, DictResponse, PasteResponse,
                          StatusResponse, redirect)
from pb.util import (absolute_url, get_host_name, highlight,
                     parse_sunset, request_content, request_keys, rst)
from pb import storage
from pb.storage import apocrypha

paste = Blueprint('paste', __name__)


@paste.app_template_global(name='url')
def _url(endpoint, **kwargs):
    return absolute_url(endpoint, **kwargs)


@paste.route('/')
def index():
    content = rst(render_template("index.rst"))

    return render_template("generic.html", content=content)


def _auth_namespace(namespace):
    uuid = request.headers.get('X-Namespace-Auth')
    if not uuid:
        return

    try:
        uuid = UUID(uuid)
    except ValueError:
        return

    cur = ns_model.auth(namespace, uuid)
    try:
        return next(cur)
    except StopIteration:
        pass


whitelist_headers = {
    #'content-type',
    'content-encoding',
    'content-disposition',
}

blacklist_headers = {
    'x-forwarded-proto',
    'x-forwarded-host',
    'x-forwarded-for',
}


def allowed_headers(headers):
    for key, value in headers.items():
        key = key.lower()
        if key in whitelist_headers:
            yield key, value
        if key in blacklist_headers:
            continue
        if key.startswith('x-'):
            yield key, value


@paste.route('/', methods=['POST'])
def post():
    stream, _ = request_content()
    if not stream:
        return StatusResponse("no post content", 400)

    status, label = apocrypha.write(stream.read())
    if status is storage.WRITE.CREATED:
        return PasteResponse(dict(
            url="/" + label
        ))
    else:
        return StatusResponse("error", 500)


def _namespace_kwargs(kwargs):
    host = get_host_name(request)
    if not _auth_namespace(host):
        return StatusResponse("invalid auth", 403)
    label, _ = kwargs['namespace']
    return dict(
        label=label,
        namespace=host,
    )


@paste.route('/<namespace:namespace>', methods=['PUT'], namespace_only=True)
@paste.route('/<uuid:uuid>', methods=['PUT'])
def put(**kwargs):
    if 'namespace' in kwargs:
        kwargs = _namespace_kwargs(kwargs)

    stream, filename = request_content()
    if not stream:
        return StatusResponse("no post content", 400)

    cur = model.get_digest(stream)
    try:
        return PasteResponse(next(cur), "already exists", filename)
    except StopIteration:
        pass

    if filename:
        kwargs['mimetype'], _ = guess_type(filename)

    # this entirely replaces paste headers, which might not be expected behavior
    headers = dict(allowed_headers(request.headers))

    # FIXME: such query; wow
    invalidate(**kwargs)
    result = model.put(stream, headers=headers, **kwargs)
    if result['n']:
        paste = next(model.get_meta(**kwargs))
        return PasteResponse(paste, "updated")

    return StatusResponse("not found", 404)


@paste.route('/<namespace:namespace>', methods=['DELETE'], namespace_only=True)
@paste.route('/<uuid:uuid>', methods=['DELETE'])
def delete(**kwargs):
    if 'namespace' in kwargs:
        kwargs = _namespace_kwargs(kwargs)

    paste = invalidate(**kwargs)
    result = model.delete(**kwargs)
    if result['n']:
        return PasteResponse(paste, "deleted")
    return StatusResponse("not found", 404)


def _get_paste(cb, sid=None, sha1=None, label=None, namespace=None):
    if sid:
        sid, name, value = sid
        return cb(**{
            'short': sid,
            'private': {
                '$exists': False
            },
            'namespace': {
                '$exists': False
            }
        }), name, value
    if sha1:
        digest, name = sha1[:2]
        return cb(**{
            'digest': digest,
            'namespace': {
                '$exists': False
            }
        }), name, digest
    if label:
        label, name = label
        return cb(**{
            'label': label,
            'namespace': {
                '$exists': False
            }
        }), name, label
    if namespace:
        label, name = namespace
        host = get_host_name(request)
        return cb(
            label=label,
            namespace=host
        ), name, label

    return None, None, None


@paste.route('/<namespace:namespace>', methods=['REPORT'], namespace_only=True)
@paste.route('/<sid(length=28):sha1>', methods=['REPORT'])
@paste.route('/<sid(length=4):sid>', methods=['REPORT'])
@paste.route('/<sha1:sha1>', methods=['REPORT'])
@paste.route('/<label:label>', methods=['REPORT'])
def report(sid=None, sha1=None, label=None, namespace=None):
    cur, name, path = _get_paste(model.get_meta, sid, sha1, label, namespace)

    paste = next(cur)

    return PasteResponse(paste, "found")


@paste.route('/<string(minlength=3):label>')
@paste.route('/<string(minlength=3):label>/<string(minlength=0):lexer>')
@paste.route('/<string(minlength=3):label>/<string(minlength=0):lexer>/<formatter>')
@paste.route('/<handler:handler>/<string(minlength=3):label>')
def get(label, lexer=None, formatter=None, handler=None):
    status, content = apocrypha.read(label)
    if status is storage.READ.FOUND:
        pass
    elif status is storage.READ.NOT_FOUND:
        return StatusResponse("not found", 404)
    else:
        return StatusResponse("error", 500)

    if lexer is not None:
        return highlight(content, lexer, formatter)
    elif handler is not None:
        return _handler.get(handler, content, mimetype, path=path)
    else:
        mimetype, _ = guess_type(label)
        response = BaseResponse(content, mimetype=mimetype)
        return response


@paste.route('/<handler:handler>', methods=['POST'])
def preview(handler):
    stream, filename = request_content()

    if not stream:
        return ''

    mimetype = None
    if filename:
        mimetype, _ = guess_type(filename)

    return _handler.get(handler, stream.read(), mimetype, partial=True)


@paste.route('/u', methods=['POST'])
@paste.route('/u/<label:label>', methods=['POST'])
def url(label=None):
    stream, _ = request_content()
    if not stream:
        return StatusResponse("no post content", 400)

    args = {}

    if label:
        label, _ = label
        if len(label) == 1:
            return StatusResponse("invalid label", 400)
        args['label'] = label

    stream = BytesIO(stream.read().decode('utf-8').split()[0].encode('utf-8'))

    cur = model.get_digest(stream)

    try:
        url = next(cur)
        status = "already exists"
    except StopIteration:
        url = model.insert(stream, redirect=1, **args)
        status = "created"

    return PasteResponse(url, status)


@paste.route('/s')
def stats():
    # fixme: use mapreduce
    return DictResponse(dict(pastes=-1))


@paste.route('/static/<style>.css')
def highlight_css(style="default"):
    try:
        css = HtmlFormatter(style=style).get_style_defs('body')
    except ClassNotFound:
        return StatusResponse("not found", 404)

    return BaseResponse(css, mimetype='text/css')


@paste.route('/lf')
def list_formatters():
    formatters = [i.aliases for i in get_all_formatters()]
    return DictResponse(formatters)


@paste.route('/l')
def list_lexers():
    return DictResponse(list(get_lexer_aliases()))


@paste.route('/ls')
def list_styles():
    return DictResponse(list(get_all_styles()))
