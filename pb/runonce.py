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
from argparse import ArgumentParser

from pb.pb import load_yaml

config = load_yaml(None, 'config.yaml')

def add_config_user(db):
    up = parse.urlparse(config['MONGO']['host'])

    auth = [getattr(up, k) for k in ['username', 'password']]

    db.client.admin.add_user(*auth, roles=[{'role': 'readWrite', 'db': config['MONGO_DATABASE']}])

def add_indexes(db):
    db.pastes.create_index('digest', unique=True)
    db.pastes.create_index('date')
    db.pastes.create_index('label', unique=True, sparse=True)
    db.pastes.create_index('private', sparse=True)

def _admin(db):
    add_config_user(db)
    add_indexes(db)

def main(uri=None, func=add_indexes):
    con = MongoClient(**config['MONGO'] if not uri else {'host':uri})
    db = con[config['MONGO_DATABASE']]

    func(db)

parser = ArgumentParser(description='Initial pb database setup')
sub = parser.add_subparsers(metavar='[admin]')
admin = sub.add_parser('admin', help='In this mode, the uri provided will be used to authenticate '
                       'initially, and the credentials in config.yaml will be used to create a '
                       'new user with access to the pb database.')

admin.add_argument('uri',
                    help='the admin mongodb uri: mongodb://username:password@host[:port]')
admin.set_defaults(func=_admin)

if __name__ == '__main__':
    ns = parser.parse_args()
    main(**vars(ns))
