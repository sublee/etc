# -*- coding: utf-8 -*-
"""
   etc.mock
   ~~~~~~~~
"""
from __future__ import absolute_import

from collections import OrderedDict
from datetime import datetime, timedelta
import itertools
import os
import threading

import six

from .adapters import Adapter
from .errors import KeyNotFound
from .results import Created, Deleted, Directory, Got, Set, Value


# key:
# history:
#     index: node
#     index2: node2
#     ...
# nodes:


class MockNode(object):

    __slots__ = ('key', 'history', 'nodes', 'created_index', 'modified_index')

    def __init__(self, key, index, value=None, dir=False,
                 ttl=None, expiration=None):
        if bool(dir) is (value is not None):
            raise TypeError('Choose one of value or directory')
        self.key = key
        self.history = OrderedDict()
        self.created_index = index
        self.set(index, value, ttl, expiration)
        self.nodes = {} if dir else None

    def set(self, index, value=None, ttl=None, expiration=None):
        snapshot = MockNodeSnapshot(value, ttl, expiration)
        self.history[index] = snapshot
        self.modified_index = index

    def add_node(self, node):
        if not node.key.startswith(self.key):
            raise ValueError('Out of this key')
        sub_key = node.key[len(self.key):].rstrip('/')
        if not sub_key.startswith('/'):
            sub_key = '/' + sub_key
        if sub_key in self.nodes:
            raise ValueError('Already exists')
        self.nodes[sub_key] = node

    def has_node(self, sub_key):
        return sub_key in self.nodes

    def get_node(self, sub_key):
        return self.nodes[sub_key]

    def pop_node(self, sub_key):
        return self.nodes.pop(sub_key)

    def canonicalize(self, index=None, sorted=False):
        modified_index = self.modified_index if index is None else index
        snapshot = self.history[modified_index]
        args = (modified_index, self.created_index,
                snapshot.ttl, snapshot.expiration)
        if self.nodes is None:
            node_class = Value
            value_or_nodes = snapshot.value
        else:
            node_class = Directory
            if index is None:
                value_or_nodes = [n.canonicalize() for n in
                                  six.viewvalues(self.nodes)]
                if sorted:
                    value_or_nodes.sort(key=lambda n: n.key)
            else:
                value_or_nodes = []
        return node_class(self.key, value_or_nodes, *args)


class MockNodeSnapshot(object):

    __slots__ = ('value', 'ttl', 'expiration')

    def __init__(self, value=None, ttl=None, expiration=None):
        self.value = value
        self.ttl = ttl
        self.expiration = expiration


class MockAdapter(Adapter):

    def __init__(self, __):
        self.events = {}
        self.index = 0
        self.root = MockNode('/', self.index, dir=True)

    def next_index(self):
        self.index += 1
        return self.index

    def wake_waiters(self, key):
        try:
            event = self.events[key]
        except KeyError:
            pass
        else:
            event.set()
            self.events.pop(key, None)

    def split_key(self, key):
        if key == '/':
            return ()
        key_chunks = os.path.split(key)
        if key_chunks[0] == '/':
            key_chunks = list(key_chunks)
            key_chunks[1] = '/' + key_chunks[1]
            return key_chunks[1:]
        else:
            return key_chunks

    def get(self, key, recursive=False, sorted=False, quorum=False,
            wait=False, wait_index=None, timeout=None):
        key_chunks = self.split_key(key)
        if wait:
            while True:
                node = reduce(MockNode.get_node, key_chunks, self.root)
                if wait_index <= node.modified_index:
                    break
                event = self.events.setdefault(key, threading.Event())
                event.wait()
        else:
            try:
                node = reduce(MockNode.get_node, key_chunks, self.root)
            except KeyError:
                raise KeyNotFound(index=self.index)
        c_node = node.canonicalize(wait_index, sorted=sorted)
        return Got(c_node, None, self.index)

    def set(self, key, value=None, dir=False, ttl=None,
            prev_value=None, prev_index=None, prev_exist=None, timeout=None):
        expiration = ttl and (datetime.utcnow() + timedelta(ttl))
        key_chunks = self.split_key(key)
        index = self.next_index()
        parent_node = reduce(MockNode.get_node, key_chunks[:-1], self.root)
        try:
            node = parent_node.get_node(key_chunks[-1])
        except KeyError:
            if prev_exist:
                raise KeyNotFound(index=self.index)
            node = MockNode(key, index, value, dir, ttl, expiration)
            parent_node.add_node(node)
        else:
            node.set(index, value, ttl, expiration)
        self.wake_waiters(key)
        c_node = node.canonicalize()
        return Set(c_node, None, self.index)

    def append(self, key, value=None, dir=False, ttl=None, timeout=None):
        expiration = ttl and (datetime.utcnow() + timedelta(ttl))
        key_chunks = self.split_key(key)
        parent_node = reduce(MockNode.get_node, key_chunks[:-1], self.root)
        for x in itertools.count(len(parent_node.nodes)):
            item_key = '%16d' % x
            if not parent_node.has_node(item_key):
                break
        index = self.next_index()
        node = MockNode(os.path.join(key, item_key),
                        index, value, dir, ttl, expiration)
        parent_node.add_node(node)
        self.wake_waiters(key)
        c_node = node.canonicalize()
        return Created(c_node, None, self.index)

    def delete(self, key, dir=False, recursive=False,
               prev_value=None, prev_index=None, timeout=None):
        key_chunks = self.split_key(key)
        parent_node = reduce(MockNode.get_node, key_chunks[:-1], self.root)
        node = parent_node.pop_node(key_chunks[-1])
        c_node = node.canonicalize()
        return Deleted(c_node, None, self.index)
