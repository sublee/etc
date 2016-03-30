# -*- coding: utf-8 -*-
"""
   etc.helpers
   ~~~~~~~~~~~
"""
from __future__ import absolute_import

import io


__all__ = ['gen_repr', 'Missing', 'registry']


#: The placeholder for missing parameters.
Missing = object()


def registry(attr, base=type):
    """Generates a meta class to index sub classes by their keys."""
    class Registry(base):
        def __init__(cls, name, bases, attrs):
            super(Registry, cls).__init__(name, bases, attrs)
            if not hasattr(cls, '__registry__'):
                cls.__registry__ = {}
            key = getattr(cls, attr)
            if key is not NotImplemented:
                assert key not in cls.__registry__
                cls.__registry__[key] = cls
        def __dispatch__(cls, key):
            try:
                return cls.__registry__[key]
            except KeyError:
                raise ValueError('Unknown %s: %s' % (attr, key))
    return Registry


def gen_repr(cls, template, *args, **kwargs):
    """Generates a string for :func:`repr`."""
    buf = io.StringIO()
    buf.write(u'<')
    buf.write(cls.__module__.decode() if kwargs.pop('full', False) else u'etc')
    buf.write(u'.')
    buf.write(cls.__name__.decode())
    if not kwargs.pop('dense', False):
        buf.write(u' ')
    buf.write(template.format(*args, **kwargs))
    options = kwargs.pop('options', [])
    for attr, value in options:
        if value is not None:
            buf.write(u' %s=%s' % (attr, value))
    buf.write(u'>')
    return buf.getvalue()
