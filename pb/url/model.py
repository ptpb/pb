# -*- coding: utf-8 -*-
"""
    url.model
    ~~~~~~~~~

    url database model.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from uuid import uuid4
from hashlib import sha1
from datetime import datetime

from pymongo import DESCENDING

from pb.db import get_db

def insert(content):
    d = dict(
        content = content,
        digest = sha1(content).hexdigest(),
        _id = uuid4().hex,
        date = datetime.utcnow(),
    )
    get_db().urls.insert(d)
    return d

def get_digest(content):
    return get_db().urls.find(dict(
        digest = sha1(content).hexdigest()
    )).sort('date', DESCENDING)

def get_content(**kwargs):
    return get_db().urls.find(dict(
        **kwargs
    ), dict(
        content = 1
    )).sort('date', DESCENDING)
