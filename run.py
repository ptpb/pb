#!/usr/bin/env python3
"""
    wsgi stub
    ~~~~~~~~~

    intended to be conveniently used by wsgi servers.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from sys import path

from pb.pb import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='::1', port=10002)
