#!/usr/bin/env python3
"""
    index stub
    ~~~~~~~~~~

    run this once to create indexes for paste document fields

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from run import app
from pb.db import get_db

if __name__ == "__main__":
    with app.app_context():
        db = get_db()
        db.pastes.ensure_index('digest', unique=True)
        db.pastes.ensure_index('date', unique=True)
        db.pastes.ensure_index('label', unique=True, sparse=True)
        db.pastes.ensure_index('private', sparse=True)
