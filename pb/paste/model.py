# -*- coding: utf-8 -*-
"""
    paste.model
    ~~~~~~~~~~~

    paste database model.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from datetime import datetime, timedelta
from hashlib import sha1
from itertools import filterfalse
from uuid import UUID, uuid4

from bson import ObjectId
from pymongo import DESCENDING

from pb.db import get_db, get_fs


def _transform(kwargs):
    for key, value in kwargs.items():
        if not value:
            continue
        if key == 'uuid':
            yield '_id', value.hex
        else:
            yield key, value


def transform(kwargs):
    return dict(_transform(kwargs))


def _put(stream):
    b = stream.read()
    digest = sha1(b).hexdigest()
    size = len(b)
    try:
        if stream.getbuffer().nbytes > 2 ** 23:
            b = get_fs().put(b)
    except AttributeError:
        # FIXME: what the actual fuck, mitsuhiko?
        b = get_fs().put(b)
    return dict(
        content=b,
        digest=digest,
        short=digest[-6:],
        size=size
    )


def _get(content):
    if isinstance(content, ObjectId):
        return get_fs().get(content).read()
    return content


def insert(stream, **kwargs):
    kwargs.update(**_put(stream))
    d = dict(
        _id=uuid4().hex,
        date=datetime.utcnow(),
        **transform(kwargs)
    )
    get_db().pastes.insert(d)
    return d


def put(stream, mimetype=None, headers={}, **kwargs):
    args = _put(stream)
    args.update(mimetype=mimetype, headers=headers)
    return get_db().pastes.update(transform(kwargs), {
        '$set': transform(args)
    })


def delete(**kwargs):
    return get_db().pastes.remove(transform(kwargs))


def get_digest(stream=None, content=None):
    cur = get_db().pastes.find(dict(
        digest=sha1(content if content else stream.read()).hexdigest()
    )).sort('date', DESCENDING)
    # fixme: wtf?
    if stream:
        stream.seek(0)

    return filterfalse(_is_expired, cur)


def get_content(**kwargs):
    cur = get_db().pastes.find(transform(kwargs), dict(
        content=1,
        redirect=1,
        sunset=1,
        date=1,
        _id=1,
        mimetype=1,
        headers=1,
    )).sort('date', DESCENDING)

    return filterfalse(_is_expired, cur)


def get_meta(**kwargs):
    cur = get_db().pastes.find(
        transform(kwargs)
    )

    return filterfalse(_is_expired, cur)


def _is_expired(paste):
    if not paste.get('sunset'):
        return False

    max_age = paste['sunset'] - datetime.utcnow()
    if not (max_age < timedelta()):
        return False

    uuid = UUID(hex=paste['_id'])
    # XXX: we shouldn't actually need to invalidate here because we set
    # cache_control headers correctly
    delete(uuid=uuid)

    return True
