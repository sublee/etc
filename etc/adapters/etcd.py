# -*- coding: utf-8 -*-
"""
   etc.etcd
   ~~~~~~~~
"""
from __future__ import absolute_import

import io
import socket
import sys

import iso8601
import requests
from requests.exceptions import ChunkedEncodingError
from requests.packages.urllib3.exceptions import ReadTimeoutError
import six
from six import reraise
from six.moves.urllib.parse import urljoin

from ..adapter import Adapter
from ..errors import EtcdError, TimedOut
from ..results import Directory, EtcdResult, Node, Value


__all__ = ['EtcdAdapter']


class EtcdAdapter(Adapter):
    """An adapter which communicates with an etcd v2 server."""

    def __init__(self, url, default_timeout=60):
        super(EtcdAdapter, self).__init__(url)
        self.default_timeout = default_timeout
        self.session = requests.Session()

    def clear(self):
        self.session.close()

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

    @classmethod
    def make_node(cls, data):
        try:
            key = data['key']
        except KeyError:
            key, kwargs = u'/', {}
        else:
            kwargs = {'modified_index': int(data['modifiedIndex']),
                      'created_index': int(data['createdIndex'])}
        ttl = data.get('ttl')
        if ttl is not None:
            expiration = iso8601.parse_date(data['expiration'])
            kwargs.update(ttl=ttl, expiration=expiration)
        if 'value' in data:
            node_cls = Value
            args = (data['value'],)
        elif data.get('dir', False):
            node_cls = Directory
            args = ([cls.make_node(n) for n in data.get('nodes', ())],)
        else:
            node_cls, args = Node, ()
        return node_cls(key, *args, **kwargs)

    @classmethod
    def make_result(cls, data, headers=None):
        action = data['action']
        node = cls.make_node(data['node'])
        kwargs = {}
        try:
            prev_node_data = data['prevNode']
        except KeyError:
            pass
        else:
            kwargs['prev_node'] = cls.make_node(prev_node_data)
        if headers:
            kwargs.update(etcd_index=int(headers['X-Etcd-Index']),
                          raft_index=int(headers['X-Raft-Index']),
                          raft_term=int(headers['X-Raft-Term']))
        return EtcdResult.__dispatch__(action)(node, **kwargs)

    @classmethod
    def make_error(cls, data, headers=None):
        errno = data['errorCode']
        message = data['message']
        cause = data['cause']
        index = data['index']
        return EtcdError.__dispatch__(errno)(message, cause, index)

    @classmethod
    def wrap_response(cls, res):
        if res.ok:
            return cls.make_result(res.json(), res.headers)
        else:
            raise cls.make_error(res.json())

    @staticmethod
    def build_args(typed_args):
        args = {}
        for key, (type_, value) in typed_args.items():
            if value is None:
                continue
            if type_ is bool:
                args[key] = u'true' if value else u'false'
            else:
                args[key] = value
        return args

    @staticmethod
    def erred():
        """Wraps errors.  Call it in `except` clause::

           try:
               do_something()
           except:
               self.erred()

        """
        exc_type, exc, tb = sys.exc_info()
        if issubclass(exc_type, socket.timeout):
            raise TimedOut
        elif issubclass(exc_type, requests.ConnectionError):
            internal_exc = exc.args[0]
            if isinstance(internal_exc, ReadTimeoutError):
                raise TimedOut
        reraise(exc_type, exc, tb)

    def get(self, key, recursive=False, sorted=False, quorum=False,
            wait=False, wait_index=None, timeout=None):
        """Requests to get a node by the given key."""
        url = self.make_key_url(key)
        params = self.build_args({
            'recursive': (bool, recursive or None),
            'sorted': (bool, sorted or None),
            'quorum': (bool, quorum or None),
            'wait': (bool, wait or None),
            'waitIndex': (int, wait_index),
        })
        if timeout is None:
            # Try again when :exc:`TimedOut` thrown.
            while True:
                try:
                    try:
                        res = self.session.get(url, params=params)
                    except:
                        self.erred()
                except (TimedOut, ChunkedEncodingError):
                    continue
                else:
                    break
        else:
            try:
                res = self.session.get(url, params=params, timeout=timeout)
            except ChunkedEncodingError:
                raise TimedOut
            except:
                self.erred()
        return self.wrap_response(res)

    def set(self, key, value=None, dir=False, ttl=None,
            prev_value=None, prev_index=None, prev_exist=None, timeout=None):
        """Requests to create an ordered node into a node by the given key."""
        url = self.make_key_url(key)
        data = self.build_args({
            'value': (six.text_type, value),
            'dir': (bool, dir or None),
            'ttl': (int, ttl),
            'prevValue': (six.text_type, prev_value),
            'prevIndex': (int, prev_index),
            'prevExist': (bool, prev_exist),
        })
        try:
            res = self.session.put(url, data=data, timeout=timeout)
        except:
            self.erred()
        return self.wrap_response(res)

    def append(self, key, value=None, dir=False, ttl=None, timeout=None):
        """Requests to create an ordered node into a node by the given key."""
        url = self.make_key_url(key)
        data = self.build_args({
            'value': (six.text_type, value),
            'dir': (bool, dir or None),
            'ttl': (int, ttl),
        })
        try:
            res = self.session.post(url, data=data, timeout=timeout)
        except:
            self.erred()
        return self.wrap_response(res)

    def delete(self, key, dir=False, recursive=False,
               prev_value=None, prev_index=None, timeout=None):
        """Requests to delete a node by the given key."""
        url = self.make_key_url(key)
        params = self.build_args({
            'dir': (bool, dir or None),
            'recursive': (bool, recursive or None),
            'prevValue': (six.text_type, prev_value),
            'prevIndex': (int, prev_index),
        })
        try:
            res = self.session.delete(url, params=params, timeout=timeout)
        except:
            self.erred()
        return self.wrap_response(res)
