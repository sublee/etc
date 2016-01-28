# -*- coding: utf-8 -*-
"""
   etc.client
   ~~~~~~~~~~
"""
from __future__ import absolute_import

import io
from urlparse import urljoin

import requests


__all__ = ['Client']


class Adapter(object):

    def get(self, key, recursive=False, sorted=False, quorum=False,
            wait=False, wait_index=0, timeout=None):
        raise NotImplementedError

    def set(self, key, value=None, dir=False, ttl=None,
            prev_value=None, prev_index=None, prev_exist=None, timeout=None):
        raise NotImplementedError

    def append(self, key, value=None, dir=False, ttl=None, timeout=None):
        raise NotImplementedError

    def delete(self, key, recursive=False,
               prev_value=None, prev_index=None, timeout=None):
        raise NotImplementedError


class EtcdAdapter(Adapter):
    """Communicates with an etcd server.  It implements several essential raw
    methods of etcd.
    """

    def __init__(self, url=u'http://127.0.0.1:4001', default_timeout=60):
        self.url = url
        self.default_timeout = default_timeout
        self.session = requests.Session()

    def make_url(self, path, api_root=u'/v2/'):
        """Gets a full URL from just path."""
        return urljoin(urljoin(self.url, api_root), path)

    def make_key_url(self, key):
        """Gets a URL for a key."""
        if type(key) is bytes:
            key = key.decode('utf-8')
        buf = io.StringIO()
        buf.write(u'keys')
        if not key.startswith(u'/'):
            buf.write(u'/')
        buf.write(key)
        return self.make_url(buf.getvalue())

    @staticmethod
    def build_args(args=None, **kwargs):
        if args is None:
            args = {}
        for key, (type_, value) in kwargs.items():
            if value is None:
                continue
            if type_ is bool:
                args[key] = u'true' if value else u'false'
            else:
                args[key] = value
        return args

    def wrap_result(self, res):
        return res.json(), res.headers

    def get(self, key, recursive=False, sorted=False, quorum=False,
            wait=False, wait_index=0, timeout=None):
        """Requests to get a node by the given key."""
        url = self.make_key_url(key)
        params = self.build_args(recursive=(bool, recursive or None),
                                 sorted=(bool, sorted or None),
                                 quorum=(bool, quorum or None),
                                 wait=(bool, wait or None),
                                 wait_index=(int, wait_index))
        with self.session as s:
            res = s.get(url, params=params, timeout=timeout)
        return self.wrap_result(res)

    def set(self, key, value=None, dir=False, ttl=None,
            prev_value=None, prev_index=None, prev_exist=None, timeout=None):
        """Requests to create an ordered node into a node by the given key."""
        if (value is None) == (not dir):
            raise ValueError('Set value or make as directory')
        if value is not None and not isinstance(value, unicode):
            raise TypeError('Set unicode value')
        url = self.make_key_url(key)
        data = self.build_args(value=(unicode, value),
                               dir=(bool, dir or None),
                               ttl=(int, ttl),
                               prev_value=(unicode, prev_value),
                               prev_index=(int, prev_index),
                               prev_exist=(bool, prev_exist))
        with self.session as s:
            res = s.put(url, data=data, timeout=timeout)
        return self.wrap_result(res)

    def append(self, key, value=None, dir=False, ttl=None, timeout=None):
        """Requests to create an ordered node into a node by the given key."""
        if (value is None) == (not dir):
            raise ValueError('Set value or make as directory')
        if value is not None and not isinstance(value, unicode):
            raise TypeError('Set unicode value')
        url = self.make_key_url(key)
        data = self.build_args(value=(unicode, value),
                               dir=(bool, dir or None),
                               ttl=(int, ttl))
        with self.session as s:
            res = s.post(url, data=data, timeout=timeout)
        return self.wrap_result(res)

    def delete(self, key, recursive=False,
               prev_value=None, prev_index=None, timeout=None):
        """Requests to delete a node by the given key."""
        url = self.make_key_url(key)
        data = self.build_args(recursive=(bool, recursive or None),
                               prev_value=(unicode, prev_value),
                               prev_index=(int, prev_index))
        with self.session as s:
            res = s.delete(url, data=data, timeout=timeout)
        return self.wrap_result(res)


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
        return self._adapter.get(
            key, recursive=recursive, sorted=sorted, quorum=quorum,
            timeout=timeout)

    def wait(self, key, index=0, recursive=False, sorted=False, quorum=False,
             timeout=None):
        return self._adapter.get(
            key, recursive=recursive, sorted=sorted, quorum=quorum,
            wait=True, wait_index=index, timeout=timeout)

    def set(self, key, value=None, dir=False, ttl=None,
            prev_value=None, prev_index=None, timeout=None):
        return self._adapter.set(
            key, value, dir=dir, ttl=ttl,
            prev_value=prev_value, prev_index=prev_index, timeout=timeout)

    def create(self, key, value=None, dir=False, ttl=None, timeout=None):
        return self._adapter.set(
            key, value, dir=dir, ttl=ttl, prev_exist=False, timeout=timeout)

    def update(self, key, value=None, dir=False, ttl=None,
               prev_value=None, prev_index=None, timeout=None):
        return self._adapter.set(
            key, value, dir=dir, ttl=ttl,
            prev_value=prev_value, prev_index=prev_index, prev_exist=True,
            timeout=timeout)

    def delete(self, key, recursive=False,
               prev_value=None, prev_index=None, timeout=None):
        return self._adapter.delete(
            key, recursive=recursive, prev_value=prev_value,
            prev_index=prev_index, timeout=timeout)
