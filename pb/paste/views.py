# -*- coding: utf-8 -*-
"""
    paste.views
    ~~~~~~~~~~~

    paste url routes and views.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from uuid import UUID
from mimetypes import guess_type
from io import BytesIO

from datetime import timedelta, datetime

from flask import Blueprint, Response, request, render_template, current_app
from jinja2 import Markup
from pygments.formatters import HtmlFormatter, get_all_formatters
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.util import ClassNotFound
from pymongo import errors

from pb.paste import model, handler as _handler
from pb.util import highlight, request_content, rst, markdown, absolute_url
from pb.cache import invalidate
from pb.responses import StatusResponse, PasteResponse, DictResponse, redirect

paste = Blueprint('paste', __name__)

@paste.app_template_global(name='url')
def _url(endpoint, **kwargs):
    return absolute_url(endpoint, **kwargs)

@paste.route('/')
def index():
    content = rst(render_template("index.rst"))

    return render_template("generic.html", content=content)

@paste.route('/f')
def form():
    return render_template("form.html")

@paste.route('/', methods=['POST'])
@paste.route('/<label:label>', methods=['POST'])
def post(label=None):
    stream, filename = request_content()
    if not stream:
        return StatusResponse("no post content", 400)

    cur = model.get_digest(stream)

    args = {}
    if request.form.get('p'):
        args['private'] = 1
    if request.form.get('s'):
        try:
            args['sunset'] = int(request.form['s'])
        except ValueError:
            return StatusResponse("invalid sunset value", 400)
    if label:
        label, _ = label
        args['label'] = label

    if not cur.count():
        try:
            paste = model.insert(stream, **args)
        except errors.DuplicateKeyError:
            return StatusResponse("label already exists.", 409)
        uuid = str(UUID(hex=paste['_id']))
        status = "created"
    else:
        paste = next(cur)
        uuid = None
        status = "already exists"

    return PasteResponse(paste, status, filename, uuid)

@paste.route('/<uuid:uuid>', methods=['PUT'])
def put(uuid):
    stream, filename = request_content()
    if not stream:
        return StatusResponse("no post content", 400)

    cur = model.get_digest(stream)
    if cur.count():
        return PasteResponse(next(cur), "already exists", filename)

    # FIXME: such query; wow
    invalidate(uuid)
    result = model.put(uuid, stream)
    if result['n']:
        paste = next(model.get_meta(_id=uuid.hex))
        return PasteResponse(paste, "updated")

    return StatusResponse("not found", 404)

@paste.route('/<uuid:uuid>', methods=['DELETE'])
def delete(uuid):
    paste = invalidate(uuid)
    result = model.delete(uuid)
    if result['n']:
        return PasteResponse(paste, "deleted")
    return StatusResponse("not found", 404)

def _get_paste(cb, sid=None, sha1=None, label=None):
    if sid:
        sid, name, value = sid
        path = value
        return cb(**{
            '$or' : [
                {
                    'digest': {
                        '$regex': '{}$'.format(sid)
                    }
                },
                {
                    'label' : value
                }
            ],
            'private': {
                '$exists': False
            }
        })
    if sha1:
        digest, name = sha1[:2]
        path = digest
        return cb(digest = digest).hint([('digest', 1)])
    if label:
        label, name = label
        path = label
        return cb(label = label).hint([('label', 1)])

@paste.route('/<sid(length=28):sha1>', methods=['REPORT'])
@paste.route('/<sid(length=4):sid>', methods=['REPORT'])
@paste.route('/<sha1:sha1>', methods=['REPORT'])
@paste.route('/<label:label>', methods=['REPORT'])
def report(sid=None, sha1=None, label=None):
    cur = _get_paste(model.get_meta, sid, sha1, label)

    if not cur or not cur.count():
        return StatusResponse("not found", 404)

    paste = next(cur)
    return PasteResponse(paste, "found")

@paste.route('/<sid(length=28):sha1>')
@paste.route('/<sid(length=28):sha1>/<string(minlength=0):lexer>')
@paste.route('/<sid(length=28):sha1>/<string(minlength=0):lexer>/<formatter>')
@paste.route('/<string(length=1):handler>/<sid(length=28):sha1>')
@paste.route('/<sid(length=4):sid>')
@paste.route('/<sid(length=4):sid>/<string(minlength=0):lexer>')
@paste.route('/<sid(length=4):sid>/<string(minlength=0):lexer>/<formatter>')
@paste.route('/<string(length=1):handler>/<sid(length=4):sid>')
@paste.route('/<sha1:sha1>')
@paste.route('/<sha1:sha1>/<string(minlength=0):lexer>')
@paste.route('/<sha1:sha1>/<string(minlength=0):lexer>/<formatter>')
@paste.route('/<string(length=1):handler>/<sha1:sha1>')
@paste.route('/<label:label>')
@paste.route('/<label:label>/<string(minlength=0):lexer>')
@paste.route('/<label:label>/<string(minlength=0):lexer>/<formatter>')
@paste.route('/<string(length=1):handler>/<label:label>')
def get(sid=None, sha1=None, label=None, lexer=None, handler=None, formatter=None):
    cur = _get_paste(model.get_content, sid, sha1, label)

    if not cur or not cur.count():
        return StatusResponse("not found", 404)

    paste = next(cur)
    if paste.get('sunset'):
        request.max_age = (paste['date'] + timedelta(seconds=paste['sunset'])) - datetime.utcnow()
        if request.max_age < timedelta():
            request.max_age = 0
        else:
            request.max_age = request.max_age.seconds

        if paste['date'] + timedelta(seconds=paste['sunset']) < datetime.utcnow():
            max_age = datetime.utcnow() - (paste['date'] + timedelta(seconds=paste['sunset']))
            uuid = UUID(hex=paste['_id'])
            paste = invalidate(uuid)
            result = model.delete(uuid)
            if not result['n']:
                return StatusResponse("this should not happen", 500)
            return PasteResponse(paste, "expired")

    content = model._get(paste.get('content'))

    if paste.get('redirect'):
        content = content.decode('utf-8')
        return redirect(content, content)

    mimetype, _ = guess_type(name)
    if not mimetype:
        mimetype = 'text/plain'

    if lexer != None:
        return highlight(content, lexer, formatter)
    if handler != None:
        return _handler.get(handler, content, mimetype, path=path)

    return Response(content, mimetype=mimetype)

@paste.route('/<string(length=1):handler>', methods=['POST'])
def preview(handler):
    stream, filename = request_content()

    if not stream:
        return ''

    mimetype = None
    if filename:
        mimetype, _ = guess_type(filename)

    return _handler.get(handler, stream.read(), mimetype, partial=True)

@paste.route('/u', methods=['POST'])
def url():
    stream, _ = request_content()
    if not stream:
        return StatusResponse("no post content", 400)

    stream = BytesIO(stream.read().decode('utf-8').split()[0].encode('utf-8'))

    cur = model.get_digest(stream)
    if not cur.count():
        url = model.insert(stream, redirect=1)
        status = "created"
    else:
        url = next(cur)
        status = "already exists"

    return PasteResponse(url, status)

@paste.route('/s')
def stats():
    cur = model.get_stats()
    return DictResponse(dict(pastes=cur.count()))

@paste.route('/static/<style>.css')
def highlight_css(style="default"):
    try:
        css = HtmlFormatter(style=style).get_style_defs('.code')
    except ClassNotFound:
        return StatusResponse("not found", 404)

    return Response(css, mimetype='text/css')

@paste.route('/lf')
def list_formatters():
    formatters = [i.aliases for i in get_all_formatters()]
    return DictResponse(formatters)

@paste.route('/l')
def list_lexers():
    lexers = [i for _, i, _, _ in get_all_lexers()]
    return DictResponse(lexers)

@paste.route('/ls')
def list_styles():
    return DictResponse(list(get_all_styles()))
