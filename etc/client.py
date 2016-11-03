# -*- coding: utf-8 -*-
"""
   etc.client
   ~~~~~~~~~~
"""
from __future__ import absolute_import

from .helpers import gen_repr


__all__ = ['Client']


class Client(object):

    def __init__(self, adapter):
        self.adapter = adapter

    @property
    def url(self):
        return self.adapter.url

    def clear(self):
        return self.adapter.clear()

    def __repr__(self):
        return gen_repr(self.__class__, u"'{0}'", self.url, short=True)

    def get(self, key, recursive=False, sorted=False, quorum=False,
            timeout=None):
        """Gets a value of key."""
        return self.adapter.get(key, recursive=recursive, sorted=sorted,
                                quorum=quorum, timeout=timeout)

    def wait(self, key, index=0, recursive=False, sorted=False, quorum=False,
             timeout=None):
        """Waits until a node changes."""
        return self.adapter.get(key, recursive=recursive, sorted=sorted,
                                quorum=quorum, wait=True, wait_index=index,
                                timeout=timeout)

    def set(self, key, value=None, dir=False, ttl=None,
            prev_value=None, prev_index=None, timeout=None):
        """Sets a value to a key."""
        return self.adapter.set(key, value, dir=dir, ttl=ttl,
                                prev_value=prev_value, prev_index=prev_index,
                                timeout=timeout)

    def create(self, key, value=None, dir=False, ttl=None, timeout=None):
        """Creates a new key."""
        return self.adapter.set(key, value, dir=dir, ttl=ttl,
                                prev_exist=False, timeout=timeout)

    def update(self, key, value=None, dir=False, ttl=None,
               prev_value=None, prev_index=None, timeout=None):
        """Updates an existing key."""
        return self.adapter.set(key, value, dir=dir, ttl=ttl,
                                prev_value=prev_value, prev_index=prev_index,
                                prev_exist=True, timeout=timeout)

    def append(self, key, value=None, dir=False, ttl=None, timeout=None):
        """Creates a new automatically increasing key in the given directory
        key.
        """
        return self.adapter.append(key, value, dir=dir, ttl=ttl,
                                   timeout=timeout)

    def delete(self, key, dir=False, recursive=False,
               prev_value=None, prev_index=None, timeout=None):
        """Deletes a key."""
        return self.adapter.delete(key, dir=dir, recursive=recursive,
                                   prev_value=prev_value,
                                   prev_index=prev_index, timeout=timeout)
