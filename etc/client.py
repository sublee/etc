# -*- coding: utf-8 -*-
"""
   etc.client
   ~~~~~~~~~~
"""
from __future__ import absolute_import

from .adapters import EtcdAdapter


__all__ = ['Client']


class Client(object):

    def __init__(self, *args, **kwargs):
        self._adapter = EtcdAdapter(*args, **kwargs)

    @property
    def url(self):
        return self._adapter.url

    def __repr__(self):
        return u'<etc.%s \'%s\'>' % (self.__class__.__name__, self.url)

    def get(self, key, recursive=False, sorted=False, quorum=False,
            timeout=None):
        """Gets a value of key."""
        return self._adapter.get(
            key, recursive=recursive, sorted=sorted, quorum=quorum,
            timeout=timeout)

    def wait(self, key, index=0, recursive=False, sorted=False, quorum=False,
             timeout=None):
        """Waits until a node changes."""
        return self._adapter.get(
            key, recursive=recursive, sorted=sorted, quorum=quorum,
            wait=True, wait_index=index, timeout=timeout)

    def set(self, key, value=None, dir=False, ttl=None,
            prev_value=None, prev_index=None, timeout=None):
        """Sets a value to a key."""
        return self._adapter.set(
            key, value, dir=dir, ttl=ttl,
            prev_value=prev_value, prev_index=prev_index, timeout=timeout)

    def create(self, key, value=None, dir=False, ttl=None, timeout=None):
        """Creates a new key."""
        return self._adapter.set(
            key, value, dir=dir, ttl=ttl, prev_exist=False, timeout=timeout)

    def update(self, key, value=None, dir=False, ttl=None,
               prev_value=None, prev_index=None, timeout=None):
        """Updates an existing key."""
        return self._adapter.set(
            key, value, dir=dir, ttl=ttl,
            prev_value=prev_value, prev_index=prev_index, prev_exist=True,
            timeout=timeout)

    def append(self, key, value=None, dir=False, ttl=None, timeout=None):
        """Creates a new automatically increasing key in the given directory
        key.
        """
        return self._adapter.append(
            key, value, dir=dir, ttl=ttl, timeout=timeout)

    def delete(self, key, dir=False, recursive=False,
               prev_value=None, prev_index=None, timeout=None):
        """Deletes a key."""
        return self._adapter.delete(
            key, dir=dir, recursive=recursive,
            prev_value=prev_value, prev_index=prev_index, timeout=timeout)
