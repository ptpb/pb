"""
    wsgi stub
    ~~~~~~~~~

    intended to be conveniently used by wsgi servers.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

# XXX: werkzeug is garbage: https://github.com/pallets/werkzeug/issues/461
# because both writing my own reloader and replacing werkzeug with something not
# as terrible are too hard, just hack at sys.path

if __name__ == '__main__':
    # remove the pb module from sys.path; it should never be in there
    import sys, __main__
    from pathlib import Path as path
    _path = path(__main__.__file__).resolve().parent
    for index, p in enumerate(sys.path):
        p = path(p).resolve()
        if p == _path:
            assert path.cwd().resolve() != p
            sys.path[index] = str(path.cwd().resolve())


import os

from werkzeug.serving import run_simple

from pb import db
from pb.pb import create_app
from pb.runonce import add_indexes

app = create_app()


if __name__ == '__main__':
    host = os.environ.get('LISTEN_ADDRESS', '::1')
    port = os.environ.get('LISTEN_PORT', 10002)

    with app.app_context():
        pass
        #add_indexes(db.get_db())

    run_simple(host, int(port), app,
               use_reloader=True,
               use_debugger=True,
               use_evalex=True)
