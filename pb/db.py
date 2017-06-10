# -*- coding: utf-8 -*-
"""
    db
    ~~

    database functions.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from flask import g, request, current_app
from pymongo import MongoClient
from gridfs import GridFS


def get_db():
    con = getattr(g, 'con', None)
    if con is None:
        kwargs = current_app.config.get('MONGO', {'host': 'mongodb', 'port': 27017})
        g.con = con = MongoClient(**kwargs)
        g.db = con[current_app.config.get('MONGO_DATABASE', 'pb')]
    return g.db


def get_fs():
    fs = getattr(g, 'fs', None)
    if fs is None:
        g.fs = GridFS(get_db())
    return g.fs


def init_db(app):
    @app.teardown_appcontext
    def teardown_db(exception):
        con = getattr(g, 'con', None)
        if con is not None:
            con.close()
