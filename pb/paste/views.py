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


@paste.route('/<namespace:namespace>', namespace_only=True, methods=['POST'])
@paste.route('/', methods=['POST'])
@paste.route('/<label:label>', methods=['POST'])
def post(label=None, namespace=None):
    stream, filename = request_content()
    if not stream:
        return StatusResponse("no post content", 400)

    cur = model.get_digest(stream)

    args = {}
    if filename:
        args['mimetype'], _ = guess_type(filename)

    for key, value in request_keys('private', 'sunset'):
        try:
            if key == 'sunset':
                args[key] = parse_sunset(value)
            else:
                args[key] = int(value)
        except (ValueError, OverflowError):
            return StatusResponse({
                "invalid request params": {key: value}
            }, 400)

    if label:
        label, _ = label
        if len(label) == 1:
            return StatusResponse("invalid label", 400)
        args['label'] = label
    if namespace:
        host = get_host_name(request)
        if not _auth_namespace(host):
            return StatusResponse("invalid auth", 403)
        label, _ = namespace
        args.update(dict(
            label=label,
            namespace=host
        ))

    try:
        paste = next(cur)
        uuid = None
        status = "already exists"
    except StopIteration:
        try:
            paste = model.insert(stream, **args)
        except errors.DuplicateKeyError:
            return StatusResponse("label already exists.", 409)
        invalidate(**paste)
        uuid = str(UUID(hex=paste['_id']))
        status = "created"

    return PasteResponse(paste, status, filename, uuid)


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

    # FIXME: such query; wow
    result = model.put(stream, **kwargs)
    if result['n']:
        invalidate(**kwargs)
        paste = next(model.get_meta(**kwargs))
        return PasteResponse(paste, "updated")

    return StatusResponse("not found", 404)


@paste.route('/<namespace:namespace>', methods=['DELETE'], namespace_only=True)
@paste.route('/<uuid:uuid>', methods=['DELETE'])
def delete(**kwargs):
    if 'namespace' in kwargs:
        kwargs = _namespace_kwargs(kwargs)

    result = model.delete(**kwargs)
    if result['n']:
        paste = invalidate(**kwargs)
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


@paste.route('/<namespace:namespace>', namespace_only=True)
@paste.route('/<namespace:namespace>/<string(minlength=0):lexer>', namespace_only=True)
@paste.route('/<namespace:namespace>/<string(minlength=0):lexer>/<formatter>', namespace_only=True)
@paste.route('/<handler:handler>/<namespace:namespace>', namespace_only=True)
@paste.route('/<sid(length=28):sha1>')
@paste.route('/<sid(length=28):sha1>/<string(minlength=0):lexer>')
@paste.route('/<sid(length=28):sha1>/<string(minlength=0):lexer>/<formatter>')
@paste.route('/<handler:handler>/<sid(length=28):sha1>')
@paste.route('/<sid(length=4):sid>')
@paste.route('/<sid(length=4):sid>/<string(minlength=0):lexer>')
@paste.route('/<sid(length=4):sid>/<string(minlength=0):lexer>/<formatter>')
@paste.route('/<handler:handler>/<sid(length=4):sid>')
@paste.route('/<sha1:sha1>')
@paste.route('/<sha1:sha1>/<string(minlength=0):lexer>')
@paste.route('/<sha1:sha1>/<string(minlength=0):lexer>/<formatter>')
@paste.route('/<handler:handler>/<sha1:sha1>')
@paste.route('/<label:label>')
@paste.route('/<label:label>/<string(minlength=0):lexer>')
@paste.route('/<label:label>/<string(minlength=0):lexer>/<formatter>')
@paste.route('/<handler:handler>/<label:label>')
def get(sid=None, sha1=None, label=None, namespace=None, lexer=None, handler=None, formatter=None):
    cur, name, path = _get_paste(model.get_content, sid, sha1, label, namespace)

    paste = next(cur)
    if paste.get('sunset'):
        max_age = parse_sunset(**paste) - datetime.utcnow()
        request.max_age = max_age.seconds

    content = model._get(paste.get('content'))

    if paste.get('redirect'):
        content = content.decode('utf-8')
        return redirect(content, content)

    mimetype, _ = guess_type(name)
    if not mimetype:
        mimetype = paste.get('mimetype', 'text/plain')

    if lexer is not None:
        return highlight(content, lexer, formatter)
    if handler is not None:
        return _handler.get(handler, content, mimetype, path=path)

    return BaseResponse(content, mimetype=mimetype)


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
