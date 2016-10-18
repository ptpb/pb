#!/usr/bin/env python3
"""
    index stub
    ~~~~~~~~~~

    run this once to create indexes for paste document fields
    this can create users and butter your toast for you as well

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from urllib import parse
from pymongo import MongoClient
import pymongo

from pb.config import load_config

config = load_config(None, 'config.yaml')

def add_config_user(db):
    up = parse.urlparse(config['MONGO']['host'])

    auth = [getattr(up, k) for k in ['username', 'password']]

    db.client.admin.add_user(*auth, roles=[{'role': 'readWrite', 'db': config['MONGO_DATABASE']}])

def add_indexes(db):
    db.pastes.create_index('digest', unique=True)
    db.pastes.create_index('short', unique=True)
    db.pastes.create_index('date')
    db.pastes.create_index('label', unique=True, sparse=True)
    db.pastes.create_index(
        [('label', pymongo.ASCENDING),
         ('namespace', pymongo.ASCENDING)], unique=True, sparse=True)
    db.pastes.create_index('private', sparse=True)

    db.namespaces.create_index('name', unique=True)

def _admin(db):
    add_config_user(db)
    add_indexes(db)

def main(uri=None, func=add_indexes):
    con = MongoClient(**config['MONGO'] if not uri else {'host':uri})
    db = con[config['MONGO_DATABASE']]

    func(db)

if __name__ == '__main__':
    main()
