# -*- coding: utf-8 -*-
"""
   etc.helpers
   ~~~~~~~~~~~
"""
from __future__ import absolute_import


__all__ = ['registry']


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
