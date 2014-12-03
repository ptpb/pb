from flask import request

import hashlib

def insert_paste(content, raw):
    args = (content, raw, None)
    (_, _, id) = request.cur.callproc('insert_paste', args)
    return id

def get_stats():
    args = (None, None)
    (count, length) = request.cur.callproc('get_stats', args)
    return int(count), int(length)

def get_digest(content):
    digest = hashlib.new('sha1', content).digest()
    args = (digest, None)
    (_, id) = request.cur.callproc('get_digest', args)
    return id

def get_content(id):
    args = (id,) + (None,) * 2
    (_, content, raw) = request.cur.callproc('get_content', args)
    return content, raw
