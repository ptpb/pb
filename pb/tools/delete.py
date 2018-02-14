# -*- coding: utf-8 -*-
"""
    delete
    ~~~~~~

    administratively delete pastes by id; used for legal/etc... requests

    This script requires direct access to the database.

    :copyright: Copyright (C) 2018 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

import requests

from pb.cache import invalidate
from pb.paste import model
from pb.pb import create_app


parser = ArgumentParser(description='administratively delete pastes by digest',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('id',
                    help='paste id to delete')
parser.add_argument('--endpoint',
                    help='pb endpoint', default='https://ptpb.pw')


def delete_paste(digest):
    invalidate(digest=digest)
    model.delete(digest=digest)


def main():
    ns = parser.parse_args()

    res = requests.request('REPORT', f'{ns.endpoint}/{ns.id}', headers={
        'accept': 'application/json'
    })

    assert res.ok

    digest = res.json()['digest']

    with create_app().app_context():
        delete_paste(digest)


if __name__ == '__main__':
    main()
