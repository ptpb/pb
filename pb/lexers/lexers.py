# -*- coding: utf-8 -*-
"""
    lexers
    ~~~~~~

    :copyright: Copyright (C) 2018 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from itertools import chain
from operator import itemgetter, attrgetter

from pygments import lexers as pygments_lexers
from pygments.util import ClassNotFound

from pb import lexers


__all__ = ['get_lexer_by_name', 'get_lexer_aliases']


def get_lexer_by_name(name, **options):
    cls = lexers.ALIAS_MAP.get(name)
    if cls is not None:
        return cls(**options)
    return pygments_lexers.get_lexer_by_name(name, **options)


def get_lexer_aliases():
    external = map(itemgetter(1), pygments_lexers.get_all_lexers())
    internal = map(attrgetter('aliases'), lexers.LEXERS)

    return chain(external, internal)
