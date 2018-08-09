# -*- coding: utf-8 -*-
"""
    lexers
    ~~~~~~

    :copyright: Copyright (C) 2018 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from itertools import chain, repeat

from pb.lexers.lexers import *  # noqa
from pb.lexers.puppet import PuppetLexer
from pb.lexers.toml import TOMLLexer


__all__ = ['PuppetLexer', 'TOMLLexer']

LEXERS = [
    PuppetLexer,
    TOMLLexer,
]

# XXX: this is a little too much for an __init__; forgive my transgression
ALIAS_MAP = dict(chain.from_iterable(zip(cls.aliases, repeat(cls)) for cls in LEXERS))
