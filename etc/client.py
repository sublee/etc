# -*- coding: utf-8 -*-
"""
   etc.client
   ~~~~~~~~~~
"""
from __future__ import absolute_import

from .helpers import gen_repr


__all__ = ['Client']


class Client(object):
    """An etcd client.  It wraps an :class:`etc.adapter.Adapter` and exposes
    humane public methods.
    """

    def __init__(self, adapter):
        self._adapter = adapter

    @property
    def url(self):
        return self._adapter.url

    def __repr__(self):
        return gen_repr(self.__class__, u"'{0}'", self.url, short=True)

    def get(self, key, recursive=False, sorted=False, quorum=False,
            timeout=None):
        """Gets a value of a node.

        ::

           >>> etcd.get('/hello')
           <etc.Got <etc.Value /hello='Hello, world' ...> ...>
           >>> etcd.get('/container', recursive=True)
           <etc.Got <etc.Directory /container[2] ...> ...>

        :param key: the key of the node to get.
        :param recursive: include sub nodes recursively.
        :param sorted: sort sub nodes by their keys.
        :param quorum: ensure all quorums are ready to make result.
        :param timeout: timeout in seconds.

        """
        return self._adapter.get(key, recursive=recursive, sorted=sorted,
                                 quorum=quorum, timeout=timeout)

    def wait(self, key, index=0, recursive=False, sorted=False, quorum=False,
             timeout=None):
        """Waits until a node changes.

        :param key: the key of the node where it waits changes from.
        :param index: wait a modification after this index.
        :param recursive: wait until sub nodes change also.
        :param sorted: sort sub nodes by their keys.
        :param quorum: ensure all quorums are ready to make result.
        :param timeout: timeout in seconds.

        """
        return self._adapter.get(key, recursive=recursive, sorted=sorted,
                                 quorum=quorum, wait=True, wait_index=index,
                                 timeout=timeout)

    def set(self, key, value=None, dir=False, ttl=None,
            prev_value=None, prev_index=None, timeout=None):
        """Sets a value to a node.

        :param key: the key of the node to be created or updated.
        :param value: the node value.  This parameter and `dir` parameter are
                      exclusive of each other.
        :param dir: make the node to be a directory.  This parameter and
                    `value` parameter are exclusive of each other.
        :param ttl: tile to the node lives in seconds.
        :param prev_value: check the current node value is equivalent with this
                           value.
        :param prev_index: check the current node's modified index is
                           equivalent with this index.
        :param timeout: timeout in seconds.

        :type value: unicode

        """
        return self._adapter.set(key, value, dir=dir, ttl=ttl,
                                 prev_value=prev_value, prev_index=prev_index,
                                 timeout=timeout)

    def create(self, key, value=None, dir=False, ttl=None, timeout=None):
        """Creates a new key.

        :param key: the key of the node to be created.
        :param value: the node value.  This parameter and `dir` parameter are
                      exclusive of each other.
        :param dir: make the node to be a directory.  This parameter and
                    `value` parameter are exclusive of each other.
        :param ttl: tile to the node lives in seconds.
        :param timeout: timeout in seconds.

        :type value: unicode

        """
        return self._adapter.set(key, value, dir=dir, ttl=ttl,
                                 prev_exist=False, timeout=timeout)

    def update(self, key, value=None, dir=False, ttl=None,
               prev_value=None, prev_index=None, timeout=None):
        """Updates an existing key.

        :param key: the key of the node to be updated.
        :param value: the node value.  This parameter and `dir` parameter are
                      exclusive of each other.
        :param dir: make the node to be a directory.  This parameter and
                    `value` parameter are exclusive of each other.
        :param ttl: tile to the node lives in seconds.
        :param prev_value: check the current node value is equivalent with this
                           value.
        :param prev_index: check the current node's modified index is
                           equivalent with this index.
        :param timeout: timeout in seconds.

        :type value: unicode

        """
        return self._adapter.set(key, value, dir=dir, ttl=ttl,
                                 prev_value=prev_value, prev_index=prev_index,
                                 prev_exist=True, timeout=timeout)

    def append(self, key, value=None, dir=False, ttl=None, timeout=None):
        """Creates a new automatically increasing key in the given directory
        key.

        :param key: the directory node key which will contain the new node.
        :param value: the node value.  This parameter and `dir` parameter are
                      exclusive of each other.
        :param dir: make the node to be a directory.  This parameter and
                    `value` parameter are exclusive of each other.
        :param ttl: tile to the node lives in seconds.
        :param timeout: timeout in seconds.

        :type value: unicode

        """
        return self._adapter.append(key, value, dir=dir, ttl=ttl,
                                    timeout=timeout)

    def delete(self, key, dir=False, recursive=False,
               prev_value=None, prev_index=None, timeout=None):
        """Deletes a node.

        :param key: the node key to be deleted.
        :param dir: whether the node is directory or not.
        :param recursive: delete sub nodes recursively.
        :param prev_value: check the current node value is equivalent with this
                           value.
        :param prev_index: check the current node's modified index is
                           equivalent with this index.
        :param timeout: timeout in seconds.

        """
        return self._adapter.delete(key, dir=dir, recursive=recursive,
                                    prev_value=prev_value,
                                    prev_index=prev_index, timeout=timeout)
