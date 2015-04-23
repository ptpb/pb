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

from flask import Blueprint, Response, request, render_template, current_app
from jinja2 import Markup
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_all_lexers

from pb.paste import model, handler as _handler
from pb.util import highlight, redirect, request_content, id_url, rst, markdown, any_url, dict_response, absolute_url

paste = Blueprint('paste', __name__)

@paste.app_template_global(name='url')
def _url(endpoint, **kwargs):
    return absolute_url(endpoint, **kwargs)

@paste.route('/')
def index():
    content = rst(render_template("index.rst"))

    return Response(render_template("generic.html", content=content), mimetype='text/html')

@paste.route('/f')
def form():
    return Response(render_template("form.html"), mimetype='text/html')

@paste.route('/', methods=['POST'])
@paste.route('/<label:vanity>', methods=['POST'])
def post(vanity=None):
    stream, filename = request_content()
    if not stream:
        return "Nope.\n", 400

    cur = model.get_digest(stream)
    if not cur.count():
        if vanity:
            label, _ = vanity
            paste = model.insert(stream, label=label)
        elif request.form.get('p'):
            paste = model.insert(stream, private=1)
        else:
            paste = model.insert(stream)
        uuid = str(UUID(hex=paste['_id']))
    else:
        paste = cur.__next__()
        uuid = '<redacted>'

    url = any_url(paste, filename=filename)
    gs = lambda l: current_app.url_map.converters['sid'].to_url(None, paste['digest'], l)

    body = {
        'url': url,
        'long': gs(42),
        'short': gs(6),
        'uuid': uuid,
        'sha1': paste['digest']
    }

    return dict_response(body, url=url)

@paste.route('/<uuid:uuid>', methods=['PUT'])
def put(uuid):
    stream, filename = request_content()
    if not stream:
        return "Nope.\n", 400

    cur = model.get_digest(stream)
    if cur.count():
        url = any_url(cur.__next__())
        return redirect(url, "Paste already exists.\n", 409)

    result = model.put(uuid, stream)
    if result['n']:
        # FIXME: need to invalidate cache
        return "{} pastes updated.\n".format(result['n']), 200

    return "Not found.\n", 404

@paste.route('/<uuid:uuid>', methods=['DELETE'])
def delete(uuid):
    result = model.delete(uuid)
    if result['n']:
        # FIXME: need to invalidate cache
        return "{} pastes deleted.\n".format(result['n']), 200
    return "Not found.\n", 404

@paste.route('/<sid(length=28):sha1>')
@paste.route('/<sid(length=28):sha1>/<string(minlength=0):lexer>')
@paste.route('/<string(length=1):handler>/<sid(length=28):sha1>')
@paste.route('/<sid(length=4):sid>')
@paste.route('/<sid(length=4):sid>/<string(minlength=0):lexer>')
@paste.route('/<string(length=1):handler>/<sid(length=4):sid>')
@paste.route('/<sha1:sha1>')
@paste.route('/<sha1:sha1>/<string(minlength=0):lexer>')
@paste.route('/<string(length=1):handler>/<sha1:sha1>')
@paste.route('/<label:label>')
@paste.route('/<label:label>/<string(minlength=0):lexer>')
@paste.route('/<string(length=1):handler>/<label:label>')
def get(sid=None, sha1=None, label=None, lexer=None, handler=None):
    cur = None
    if sid:
        sid, name, value = sid
        cur = model.get_content(**{
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
        cur = model.get_content(digest = digest).hint([('digest', 1)])
    if label:
        label, name = label
        cur = model.get_content(label = label).hint([('label', 1)])

    if not cur or not cur.count():
        return "Not found.\n", 404

    paste = cur.__next__()
    content = model._get(paste.get('content'))

    if paste.get('redirect'):
        content = content.decode('utf-8')
        return redirect(content, '{}\n'.format(content))

    mimetype, _ = guess_type(name)

    if lexer != None:
        return highlight(content, lexer)
    if handler != None:
        return _handler.get(handler, content, mimetype)
    if mimetype:
        return Response(content, mimetype=mimetype)

    return content

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
        return "Nope.\n", 400

    stream = BytesIO(stream.read().decode('utf-8').split('\n')[0].encode('utf-8'))

    cur = model.get_digest(stream)
    if not cur.count():
        url = model.insert(stream, redirect=1)
    else:
        url = cur.__next__()

    url = id_url(sid=url['digest'])
    return redirect(url, "{}\n".format(url), 200)

@paste.route('/s')
def stats():
    cur = model.get_stats()
    return dict_response(dict(pastes=cur.count()))

@paste.route('/static/highlight.css')
def highlight_css():
    css = HtmlFormatter().get_style_defs('.code')
    return Response(css, mimetype='text/css')

@paste.route('/l')
def list_lexers():
    lexers = '\n'.join(' '.join(i) for _, i, _, _ in get_all_lexers())
    return '{}\n'.format(lexers)
