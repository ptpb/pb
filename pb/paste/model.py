# -*- coding: utf-8 -*-
"""
    paste.model
    ~~~~~~~~~~~

    paste database model.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from uuid import uuid4
from hashlib import sha1
from datetime import datetime

from pymongo import DESCENDING
from bson import ObjectId

from pb.db import get_db, get_fs

def _put(stream):
    b = stream.read()
    digest = sha1(b).hexdigest()
    try:
        if stream.getbuffer().nbytes > 2 ** 23:
            b = get_fs().put(b)
    except AttributeError:
        # FIXME: what the actual fuck, mitsuhiko?
        b = get_fs().put(b)
    return dict(
        content = b,
        digest = digest
    )

def _get(content):
    if isinstance(content, ObjectId):
        return get_fs().get(content).read()
    return content

def insert(stream, **kwargs):
    kwargs.update(**_put(stream))
    d = dict(
        _id = uuid4().hex,
        date = datetime.utcnow(),
        **kwargs
    )
    get_db().pastes.insert(d)
    return d

def put(uuid, stream):
    return get_db().pastes.update(dict(
        _id = uuid.hex
    ), {
        '$set': _put(stream)
    })

def delete(uuid):
    return get_db().pastes.remove(dict(
        _id = uuid.hex
    ))

def get_digest(stream=None, content=None):
    paste = get_db().pastes.find(dict(
        digest = sha1(content if content else stream.read()).hexdigest()
    ), dict(
        digest = 1,
        label = 1,
        private = 1,
        _id = 1
    )).sort('date', DESCENDING)
    if stream:
        stream.seek(0)
    return paste

def get_content(**kwargs):
    paste = get_db().pastes.find(dict(
        **kwargs
    ), dict(
        content = 1,
        redirect = 1
    )).sort('date', DESCENDING)
    return paste

def get_stats():
    return get_db().pastes.find()
