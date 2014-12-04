from flask import request

from uuid import uuid4
import hashlib

def insert_paste(content, raw):
    uuid = uuid4().bytes
    args = (uuid, content, raw, None)
    (_, _, _, id) = request.cur.callproc('insert_paste', args)
    return id, uuid

def get_stats():
    args = (None, None)
    (count, length) = request.cur.callproc('get_stats', args)
    return int(count), int(length)

def get_digest(content):
    digest = hashlib.new('sha1', content).digest()
    args = (digest, None)
    (_, id) = request.cur.callproc('get_digest', args)
    return id, None

def get_content(id):
    args = (id,) + (None,) * 2
    (_, content, raw) = request.cur.callproc('get_content', args)
    return content, raw
