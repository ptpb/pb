# -*- coding: utf-8 -*-
"""
    url.model
    ~~~~~~~~~

    url database model.

    :copyright: Copyright (C) 2014 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from hashlib import sha1

from flask import request

def insert(content):
    args = (content, None)
    (_, id) = request.cur.callproc('url_insert', args)
    return int(id) if id else None

def get_digest(content):
    args = (sha1(content).digest(), None)
    (_, id) = request.cur.callproc('url_get_digest', args)
    return int(id) if id else None

def get_content(id):
    args = (id, None)
    (_, content) = request.cur.callproc('url_get_content', args)
    return content
