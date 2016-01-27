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


class Client(object):

    def __init__(self, url=u'http://127.0.0.1:4001', default_timeout=60):
        self.url = url
        self.default_timeout = default_timeout
        self.session = requests.Session()

    def _url(self, path, api_root=u'/v2/'):
        """Gets a full URL from just path."""
        return urljoin(urljoin(self.url, api_root), path)

    def _key_url(self, key):
        """Gets a URL for a key."""
        if type(key) is bytes:
            key = key.decode('utf-8')
        buf = io.StringIO()
        buf.write(u'keys')
        if not key.startswith(u'/'):
            buf.write(u'/')
        buf.write(key)
        return self._url(buf.getvalue())

    def _get(self, key, recursive=False, sorted=False, quorum=False,
             wait=False, wait_index=0, timeout=None):
        """Requests to get a node by the given key."""
        url = self._key_url(key)
        params = adapt_params(recursive=(bool, recursive),
                              sorted=(bool, sorted), quorum=(bool, quorum),
                              wait=(bool, wait), wait_index=(int, wait_index))
        with self.session as s:
            res = s.get(url, params=params, timeout=timeout)
        return res.json(), res.headers

    def get(self, key, recursive=False, sorted=False, quorum=False,
            timeout=None):
        return self._get(
            key, recursive=recursive, sorted=sorted, quorum=quorum,
            timeout=timeout)

    def watch(self, key, index=0, recursive=False, sorted=False, quorum=False,
              timeout=None):
        return self._get(
            key, recursive=recursive, sorted=sorted, quorum=quorum,
            wait=True, wait_index=index, timeout=timeout)


def adapt_params(params=None, **kwargs):
    if params is None:
        params = {}
    for key, (type_, value) in kwargs.items():
        if type_ is bool:
            if value:
                params[key] = u'true'
        else:
            params[key] = value
    return params
