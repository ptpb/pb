from flask import request

from uuid import uuid4
import hashlib

def insert_paste(content):
    uuid = uuid4().bytes
    args = (uuid, content, None)
    (_, _, id) = request.cur.callproc('insert_paste', args)
    return id, uuid

def put_paste(uuid, content):
    args = (uuid, content, None)
    (_, _, id) = request.cur.callproc('put_paste', args)
    return id

def delete_paste(uuid):
    args = (uuid, None)
    (_, id) = request.cur.callproc('delete_paste', args)
    return id

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
    args = (id,) + (None,)
    (_, content) = request.cur.callproc('get_content', args)
    return content
