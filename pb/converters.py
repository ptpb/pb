# -*- coding: utf-8 -*-
"""
    converters
    ~~

    url converters and mixin classes

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

import re
from os import path
from binascii import unhexlify, hexlify, Error as BinError
from base64 import urlsafe_b64encode, urlsafe_b64decode

from werkzeug.routing import BaseConverter

class UnhexMixin:
    def to_url(self, value, length=None):
        length = length if length else self.length
        def f(v):
            v = '{:0>{length}}'.format(v[-(length):], length = length)
            return urlsafe_b64encode(unhexlify(v)).decode('utf-8')

        if isinstance(value, str):
            return f(value)
        sid, filename = value
        ext = path.splitext(filename)[1] if filename else ''
        return '{}{}'.format(f(sid), ext)

class SREMixin:
    def to_python(self, value):
        name, label = self.sre.match(value).groups()
        return label, name

class SIDConverter(UnhexMixin, BaseConverter):
    def __init__(self, map, length):
        super().__init__(map)
        self.regex = '(([A-Za-z0-9_~.-]{{{}}})(?:[.][^/]*)?)'.format(length)
        self.sre = re.compile(self.regex)
        if length % 4 != 0:
            raise NotImplementedError('{} % 4 != 0; kthx'.format(length))
        self.length = 6 * (length // 4)

    def to_python(self, value):
        name, sid = self.sre.match(value).groups()
        try:
            _hex = hexlify(urlsafe_b64decode(sid)[-20:]).decode('utf-8')
        except BinError:
            _hex = None
        return _hex, name, value[:4]

class SHA1Converter(UnhexMixin, SREMixin, BaseConverter):
    def __init__(self, map):
        super().__init__(map)
        self.regex = '(([A-Za-z0-9]{40})(?:[.][^/]*)?)'
        self.sre = re.compile(self.regex)
        self.length = 42

class LabelConverter(SREMixin, BaseConverter):
    def __init__(self, map):
        super().__init__(map)
        self.regex = '((~[^/.]+)(?:[.][^/]*)?)'
        self.sre = re.compile(self.regex)

    def to_url(self, value, length=None):
        if isinstance(value, str):
            return value
        label, filename = value
        ext = path.splitext(filename)[1] if filename else ''
        return '{}{}'.format(label, ext)
