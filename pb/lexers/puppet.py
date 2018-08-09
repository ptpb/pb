# -*- coding: utf-8 -*-
"""
    puppet
    ~~~~~~

    Puppet lexer

    :copyright: Copyright (C) 2012 by GitHub, Inc
    :license: GPLv3, see LICENSE for details.
"""

from pygments.lexer import include, bygroups, RegexLexer
from pygments.token import *


class PuppetLexer(RegexLexer):
    name = 'Puppet'
    aliases = ['puppet']
    filenames = ['*.pp']

    tokens = {
        'root': [
            include('puppet'),
        ],
        'puppet': [
            include('comments'),
            (r'(class)(\s*)(\{)', bygroups(Name.Class, Text, Punctuation), ('type', 'namevar')),
            (r'(class|define)', Keyword.Declaration, ('block','class_name')),
            (r'node', Keyword.Declaration, ('block', 'node_name')),
            (r'elsif', Keyword.Reserved, ('block', 'conditional')),
            (r'if', Keyword.Reserved, ('block', 'conditional')),
            (r'unless', Keyword.Reserved, ('block', 'conditional')),
            (r'(else)(\s*)(\{)', bygroups(Keyword.Reserved, Text, Punctuation), 'block'),
            (r'case', Keyword.Reserved, ('case', 'conditional')),
            (r'(::)?([A-Z][\w:]+)+(\s*)(<{1,2}\|)', bygroups(Name.Class, Name.Class, Text, Punctuation), 'spaceinvader'),
            (r'(::)?([A-Z][\w:]+)+(\s*)(\{)', bygroups(Name.Class, Name.Class, Text, Punctuation), 'type'),
            (r'(::)?([A-Z][\w:]+)+(\s*)(\[)', bygroups(Name.Class, Name.Class, Text, Punctuation), ('type', 'override_name')),
            (r'(@{0,2}[\w:]+)(\s*)(\{)(\s*)', bygroups(Name.Class, Text, Punctuation, Text), ('type', 'namevar')),
            (r'\$(::)?(\w+::)*\w+', Name.Variable, 'var_assign'),
            (r'(include|require)', Keyword.Namespace, 'include'),
            (r'import', Keyword.Namespace, 'import'),
            (r'(\w+)(\()', bygroups(Name.Function, Punctuation), 'function'),
            (r'\s', Text),
        ],
        'block': [
            include('puppet'),
            (r'\}', Text, '#pop'),
        ],
        'override_name': [
            include('strings'),
            include('variables'),
            (r'\]', Punctuation),
            (r'\s', Text),
            (r'\{', Punctuation, '#pop'),
        ],
        'node_name': [
            (r'inherits', Keyword.Declaration),
            (r'[\w\.]+', String),
            include('strings'),
            include('variables'),
            (r',', Punctuation),
            (r'\s', Text),
            (r'\{', Punctuation, '#pop'),
        ],
        'class_name': [
            (r'inherits', Keyword.Declaration),
            (r'[\w:]+', Name.Class),
            (r'\s', Text),
            (r'\{', Punctuation, '#pop'),
            (r'\(', Punctuation, 'paramlist'),
        ],
        'include': [
            (r'\n', Text, '#pop'),
            (r'[\w:-]+', Name.Class),
            include('value'),
            (r'\s', Text),
        ],
        'import': [
            (r'\n', Text, '#pop'),
            (r'[\/\w\.]+', String),
            include('value'),
            (r'\s', Text),
        ],
        'case': [
            (r'(default)(:)(\s*)(\{)', bygroups(Keyword.Reserved, Punctuation, Text, Punctuation), 'block'),
            include('case_values'),
            (r'(:)(\s*)(\{)', bygroups(Punctuation, Text, Punctuation), 'block'),
            (r'\s', Text),
            (r'\}', Punctuation, '#pop'),
        ],
        'case_values': [
            include('value'),
            (r',', Punctuation),
        ],
        'comments': [
            (r'\s*#.*\n', Comment.Singleline),
        ],
        'strings': [
            (r"'.*?'", String.Single),
            (r'\w+', String.Symbol),
            (r'"', String.Double, 'dblstring'),
            (r'\/.+?\/', String.Regex),
        ],
        'dblstring': [
            (r'\$\{.+?\}', String.Interpol),
            (r'(?:\\(?:[bdefnrstv\'"\$\\/]|[0-7][0-7]?[0-7]?|\^[a-zA-Z]))', String.Escape),
            (r'[^"\\\$]+', String.Double),
            (r'\$', String.Double),
            (r'"', String.Double, '#pop'),
        ],
        'variables': [
            (r'\$(::)?(\w+::)*\w+', Name.Variable),
        ],
        'var_assign': [
            (r'\[', Punctuation, ('#pop', 'array')),
            (r'\{', Punctuation, ('#pop', 'hash')),
            (r'(\s*)(=)(\s*)', bygroups(Text, Operator, Text)),
            (r'(\(|\))', Punctuation),
            include('operators'),
            include('value'),
            (r'\s', Text, '#pop'),
        ],
        'booleans': [
            (r'(true|false)', Literal),
        ],
        'operators': [
            (r'(\s*)(==|=~|\*|-|\+|<<|>>|!=|!~|!|>=|<=|<|>|and|or|in)(\s*)', bygroups(Text, Operator, Text)),
        ],
        'conditional': [
            include('operators'),
            include('strings'),
            include('variables'),
            (r'\[', Punctuation, 'array'),
            (r'\(', Punctuation, 'conditional'),
            (r'\{', Punctuation, '#pop'),
            (r'\)', Punctuation, '#pop'),
            (r'\s', Text),
        ],
        'spaceinvader': [
            include('operators'),
            include('strings'),
            include('variables'),
            (r'\[', Punctuation, 'array'),
            (r'\(', Punctuation, 'conditional'),
            (r'\s', Text),
            (r'\|>{1,2}', Punctuation, '#pop'),
        ],
        'namevar': [
            include('value'),
            (r'\[', Punctuation, 'array'),
            (r'\s', Text),
            (r':', Punctuation, '#pop'),
            (r'\}', Punctuation, '#pop'),
        ],
        'function': [
            (r'\[', Punctuation, 'array'),
            include('value'),
            (r',', Punctuation),
            (r'\s', Text),
            (r'\)', Punctuation, '#pop'),
        ],
        'paramlist': [
            include('value'),
            (r'=', Punctuation),
            (r',', Punctuation),
            (r'\s', Text),
            (r'\[', Punctuation, 'array'),
            (r'\)', Punctuation, '#pop'),
        ],
        'type': [
            (r'(\w+)(\s*)(=>)(\s*)', bygroups(Name.Tag, Text, Punctuation, Text), 'param_value'),
            (r'\}', Punctuation, '#pop'),
            (r'\s', Text),
            include('comments'),
            (r'', Text, 'namevar'),
        ],
        'value': [
            (r'[\d\.]', Number),
            (r'([A-Z][\w:]+)+(\[)', bygroups(Name.Class, Punctuation), 'array'),
            (r'(\w+)(\()', bygroups(Name.Function, Punctuation), 'function'),
            include('strings'),
            include('variables'),
            include('comments'),
            include('booleans'),
            (r'(\s*)(\?)(\s*)(\{)', bygroups(Text, Punctuation, Text, Punctuation), 'selector'),
            (r'\{', Punctuation, 'hash'),
        ],
        'selector': [
            (r'default', Keyword.Reserved),
            include('value'),
            (r'=>', Punctuation),
            (r',', Punctuation),
            (r'\s', Text),
            (r'\}', Punctuation, '#pop'),
        ],
        'param_value': [
            include('value'),
            (r'\[', Punctuation, 'array'),
            (r',', Punctuation, '#pop'),
            (r';', Punctuation, '#pop'),
            (r'\s', Text, '#pop'),
            (r'', Text, '#pop'),
        ],
        'array': [
            include('value'),
            (r'\[', Punctuation, 'array'),
            (r',', Punctuation),
            (r'\s', Text),
            (r'\]', Punctuation, '#pop'),
        ],
        'hash': [
            include('value'),
            (r'\s', Text),
            (r'=>', Punctuation),
            (r',', Punctuation),
            (r'\}', Punctuation, '#pop'),
        ],
    }
