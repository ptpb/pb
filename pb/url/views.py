# -*- coding: utf-8 -*-
"""
    url.model
    ~~~~~~~~~

    url url routes and views.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from flask import Blueprint

from pb.util import redirect, request_content, id_url
from pb.url import model

url = Blueprint('url', __name__)

@url.route('/<sid(length=4):sid>')
def get(sid):
    id, name = sid
    cur = model.get_content(
        _id = {
            '$regex': '{}$'.format(id)
        }
    )
    if not cur or not cur.count():
        return 'Not found.\n', 404

    content = cur.__next__()['content'].decode('utf-8')

    return redirect(content, '{}\n'.format(content))

@url.route('/u', methods=['POST'])
def post():
    content, _ = request_content()
    if not content:
        return "Nope.\n", 400

    content = content.decode('utf-8').split('\n')[0].encode('utf-8')

    cur = model.get_digest(content)
    if not cur.count():
        url = model.insert(content)
    else:
        url = cur.__next__()

    url = id_url(sid=url['_id'])
    return redirect(url, "{}\n".format(url), 200)
