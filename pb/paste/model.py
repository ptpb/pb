# -*- coding: utf-8 -*-
"""
    paste.model
    ~~~~~~~~~~~

    paste database model.

    :copyright: Copyright (C) 2014 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from flask import request

from uuid import uuid4
from hashlib import sha1

def insert(content):
    secret = uuid4().bytes
    args = (secret, content, None)
    (_, _, id) = request.cur.callproc('paste_insert', args)
    return int(id) if id else None, secret

def insert_private(content):
    secret = uuid4().bytes
    args = (secret, content, None)
    (_, _, digest) = request.cur.callproc('paste_insert_private', args)
    return bytes(digest) if digest else None, secret
    
def put(secret, content):
    args = (secret, content, None, None)
    (_, _, id, digest) = request.cur.callproc('paste_put', args)
    return int(id) if id else None, bytes(digest) if digest else None

def delete(uuid):
    args = (uuid, None, None)
    (_, id, digest) = request.cur.callproc('paste_delete', args)
    return int(id) if id else None, bytes(digest) if digest else None

def get_digest(content):
    digest = sha1(content).digest()
    args = (digest, None, None)
    (_, id, exists) = request.cur.callproc('paste_get_digest', args)
    return int(id) if id else None, digest if exists else None

def get_content(id):
    args = (id,) + (None,)
    (_, content) = request.cur.callproc('paste_get_content', args)
    return content

def get_content_digest(digest):
    args = (digest, None)
    (_, content) = request.cur.callproc('paste_get_content_digest', args)
    return content

def get_stats():
    args = (None, None)
    (count, length) = request.cur.callproc('paste_get_stats', args)
    return int(count), int(length)
