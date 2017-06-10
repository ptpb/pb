#!/usr/bin/env python3
"""
    index stub
    ~~~~~~~~~~

    run this once to create indexes for paste document fields
    this can create users and butter your toast for you as well

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from argparse import ArgumentParser

from pb.runonce import _admin, main

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
