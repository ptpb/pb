"""
    wsgi stub
    ~~~~~~~~~

    intended to be conveniently used by wsgi servers.

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from werkzeug.serving import run_simple

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


from pb.pb import create_app


app = create_app()


if __name__ == '__main__':
    run_simple('::1', 10002, app,
               use_reloader=True,
               use_debugger=True,
               use_evalex=True)
