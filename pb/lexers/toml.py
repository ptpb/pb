# -*- coding: utf-8 -*-
"""
    puppet
    ~~~~~~

    TOML lexer

    :copyright: Copyright (C) 2012 by GitHub, Inc
    :copyright: Copyright (C) 2018 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from pygments.lexer import RegexLexer, bygroups
from pygments.token import *


class TOMLLexer(RegexLexer):
    """
    Lexer for TOML, a simple language for config files
    """

    name = 'TOML'
    aliases = ['toml']
    filenames = ['*.toml']

    tokens = {
        'root': [
            # heading
            (r'^(\s*)(\[+)(.*?)(\]+)$', bygroups(Text, Text, Keyword, Text)),

            # Basics, comments, strings
            (r'\s+$', Text),
            (r'^\s+', Text),
            (r'[ ]+', Text),  # hack
            (r'#.*?$', Comment.Single),
            (r'"(\\\\|\\"|[^"])*"', String),
            (r'(true|false)$', Keyword.Constant),

            # Key value pair
            (r'([^\s]+)(\s*)(=)(\s*)', bygroups(Name.Attribute, Text, Operator, Text)),

            # Eats everything
            (r'[a-zA-Z_][a-zA-Z0-9_\-]*', Name),

            # Datetime
            (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', Number.Integer),

            # Numbers
            (r'(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?j?', Number.Float),
            (r'\d+[eE][+-]?[0-9]+j?', Number.Float),
            (r'\-?\d+', Number.Integer),

            # Punctuation
            (r'[]{}:(),;[]', Punctuation),
            (r'\.', Punctuation),
        ],
    }
