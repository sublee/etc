# -*- coding: utf-8 -*-
"""
   etc.adapter
   ~~~~~~~~~~~

   The interface for etcd adapters.  A subclass of :class:`Adapter` will be
   injected verification code automatically.

"""
from __future__ import absolute_import

import functools

import six


__all__ = ['Adapter']


def with_verifier(verify, func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        verify(*args, **kwargs)
        return func(self, *args, **kwargs)
    return wrapped


class AdapterMeta(type):

    def __new__(meta, name, bases, attrs):
        for attr, verify in [('set', meta.verify_set),
                             ('append', meta.verify_append)]:
            try:
                func = attrs[attr]
            except KeyError:
                continue
            attrs[attr] = with_verifier(verify, func)
        return super(AdapterMeta, meta).__new__(meta, name, bases, attrs)

    @staticmethod
    def verify_set(key, value=None, dir=False, ttl=None, prev_value=None,
                   prev_index=None, prev_exist=None, timeout=None):
        if (value is None) == (not dir):
            raise ValueError('Set value or make as directory')
        if value is not None and not isinstance(value, six.text_type):
            raise TypeError('Set %s value' % six.text_type.__name__)

    @staticmethod
    def verify_append(key, value=None, dir=False, ttl=None, timeout=None):
        if (value is None) == (not dir):
            raise ValueError('Set value or make as directory')
        if value is not None and not isinstance(value, six.text_type):
            raise TypeError('Set %s value' % six.text_type.__name__)


class Adapter(six.with_metaclass(AdapterMeta)):
    """An interface to implement several essential raw methods of etcd."""

    def __init__(self, url):
        self.url = url

    def clear(self):
        pass

    def get(self, key, recursive=False, sorted=False, quorum=False,
            wait=False, wait_index=None, timeout=None):
        raise NotImplementedError

    def set(self, key, value=None, dir=False, ttl=None,
            prev_value=None, prev_index=None, prev_exist=None, timeout=None):
        raise NotImplementedError

    def append(self, key, value=None, dir=False, ttl=None, timeout=None):
        raise NotImplementedError

    def delete(self, key, dir=False, recursive=False,
               prev_value=None, prev_index=None, timeout=None):
        raise NotImplementedError
