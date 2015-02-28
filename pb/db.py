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

def get_db():
    con = getattr(g, 'con', None)
    if con is None:
        g.con = con = MongoClient(**current_app.config['MONGO'])
        g.db = con[current_app.config['MONGO_DATABASE']]
    return g.db

def init_db(app):
    @app.teardown_appcontext
    def teardown_db(exception):
        con = getattr(g, 'con', None)
        if con is not None:
            con.disconnect()
