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

from pb.db import get_db

def insert(content, **kwargs):
    d = dict(
        content = content,
        digest = sha1(content).hexdigest(),
        _id = uuid4().hex,
        date = datetime.utcnow(),
        **kwargs
    )
    get_db().pastes.insert(d)
    return d

def put(uuid, content):
    return get_db().pastes.update(dict(
        _id = uuid.hex
    ), {
        '$set': dict(
            content = content,
            digest = sha1(content).hexdigest()
        )
    })

def delete(uuid):
    return get_db().pastes.remove(dict(
        _id = uuid.hex
    ))

def get_digest(content):
    return get_db().pastes.find(dict(
        digest = sha1(content).hexdigest()
    )).sort('date', DESCENDING)

def get_content(**kwargs):
    return get_db().pastes.find(dict(
        **kwargs
    ), dict(
        content = 1,
        redirect = 1
    )).sort('date', DESCENDING)

def get_stats():
    return get_db().pastes.find()
