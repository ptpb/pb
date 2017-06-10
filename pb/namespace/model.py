# -*- coding: utf-8 -*-
"""
    namespace.model
    ~~~~~~~~~~~~~~~

    namespace database model.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from uuid import uuid4

from pb.db import get_db


def auth(name, uuid):
    ns = get_db().namespaces.find(dict(
        name=name,
        _id=uuid.hex
    ))

    return ns


def get(name):
    ns = get_db().namespaces.find(dict(
        name=name
    ))

    return ns


def create(name):
    d = dict(
        _id=uuid4().hex,
        name=name
    )
    get_db().namespaces.insert(d)
    return d
