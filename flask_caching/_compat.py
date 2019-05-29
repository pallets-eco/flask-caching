# -*- coding: utf-8 -*-
"""
    flask_caching._compat
    ~~~~~~~~~~~~~~~~~~~~~

    Some py2/py3 compatibility support based on a stripped down
    version of six so we don't have to depend on a specific version
    of it.

    :copyright: (c) 2013 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import sys

PYPY = hasattr(sys, "pypy_translation_info")


def to_bytes(x, charset=sys.getdefaultencoding(), errors='strict'):
    if x is None:
        return None
    if isinstance(x, (bytes, bytearray, memoryview)):  # noqa
        return bytes(x)
    if isinstance(x, str):
        return x.encode(charset, errors)
    raise TypeError('Expected bytes')

def to_native(x, charset=sys.getdefaultencoding(), errors='strict'):
    if x is None or isinstance(x, str):
        return x
    return x.decode(charset, errors)
