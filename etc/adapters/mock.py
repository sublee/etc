# -*- coding: utf-8 -*-
"""
   etc.mock
   ~~~~~~~~
"""
from __future__ import absolute_import

import bisect
from datetime import datetime, timedelta
import itertools
import os
import threading
import warnings

import six
from six.moves import reduce, xrange

from ..adapter import Adapter
from ..errors import KeyNotFound, NodeExist, TestFailed, TimedOut
from ..results import (
    Created, Deleted, Directory, Got, Node, Set, Updated, Value)


__all__ = ['MockAdapter']


KEY_SEP = '/'


def split_key(key):
    if key == KEY_SEP:
        return ()
    key_chunks = tuple(key.strip(KEY_SEP).split(KEY_SEP))
    if key_chunks[0].startswith(KEY_SEP):
        return (key_chunks[0][len(KEY_SEP):],) + key_chunks[1:]
    else:
        return key_chunks


class Waiter(object):

    def __init__(self):
        self.event = threading.Event()

    def set(self, value):
        self.value = value
        self.event.set()

    def get(self, timeout=None):
        if not self.event.wait(timeout):
            raise TimedOut
        return self.value

    def is_set(self):
        return self.event.is_set()


class MockNode(Node):

    __slots__ = Node.__slots__ + ('value', 'nodes', 'dir')

    def __init__(self, key, index, value=None, dir=False,
                 ttl=None, expiration=None):
        self.key = key
        self.created_index = index
        self.dir = None
        self.set(index, value, dir, ttl, expiration)

    def set(self, index, value=None, dir=False, ttl=None, expiration=None):
        if bool(dir) is (value is not None):
            raise TypeError('Choose one of value or directory')
        if (ttl is not None) is (expiration is None):
            raise TypeError('Both of ttl and expiration required')
        self.value = value
        if self.dir != dir:
            self.dir = dir
            self.nodes = {} if dir else None
        self.ttl = ttl
        self.expiration = expiration
        self.modified_index = index

    def add_node(self, node):
        if not node.key.startswith(self.key):
            raise ValueError('Out of this key')
        sub_key = node.key[len(self.key):].strip(KEY_SEP)
        if sub_key in self.nodes:
            raise ValueError('Already exists')
        self.nodes[sub_key] = node

    def has_node(self, sub_key):
        return sub_key in self.nodes

    def get_node(self, sub_key):
        return self.nodes[sub_key]

    def pop_node(self, sub_key):
        return self.nodes.pop(sub_key)

    def canonicalize(self, include_nodes=True, sorted=False):
        """Generates a canonical :class:`etc.Node` object from this mock node.
        """
        node_class = Directory if self.dir else Value
        kwargs = {attr: getattr(self, attr) for attr in node_class.__slots__}
        if self.dir:
            if include_nodes:
                nodes = [node.canonicalize() for node in
                         six.viewvalues(kwargs['nodes'])]
                if sorted:
                    nodes.sort(key=lambda n: n.key)
                kwargs['nodes'] = nodes
            else:
                kwargs['nodes'] = []
        return node_class(**kwargs)


class MockAdapter(Adapter):

    def __init__(self):
        self.index = 0
        self.root = MockNode('', self.index, dir=True)
        self.history = {}
        self.indices = {}
        self.waiters = {}

    @property
    def url(self):
        warnings.warn('Mock adapter does not have URL')
        return ''

    def next_index(self):
        """Gets the next etcd index."""
        self.index += 1
        return self.index

    def make_result(self, result_class, node=None, prev_node=None,
                    key_chunks=None, remember=True, **kwargs):
        def canonicalize(node, **kwargs):
            return None if node is None else node.canonicalize(**kwargs)
        index = self.index
        result = result_class(canonicalize(node, **kwargs),
                              canonicalize(prev_node, **kwargs), index)
        if remember:
            result_without_nodes = result_class(
                canonicalize(node, include_nodes=False),
                canonicalize(prev_node, include_nodes=False), index)
            self.history[index] = result_without_nodes
            key_chunks = key_chunks or split_key(node.key)
            asymptotic_key_chunks = (key_chunks[:x + 1]
                                     for x in xrange(len(key_chunks)))
            waiter_keys = [(False, key_chunks)]
            for _key_chunks in asymptotic_key_chunks:
                exact = _key_chunks == key_chunks
                self.indices.setdefault(_key_chunks, []).append((index, exact))
                waiter_keys.append((True, _key_chunks))
            for waiter_key in waiter_keys:
                try:
                    waiter = self.waiters.pop(waiter_key)
                except KeyError:
                    pass
                else:
                    waiter.set(result_without_nodes)
        return result

    def compare(self, node, prev_value=None, prev_index=None):
        if prev_value is not None and node.value != prev_value or \
           prev_index is not None and node.index != prev_index:
            raise TestFailed(index=self.index)

    def get(self, key, recursive=False, sorted=False, quorum=False,
            wait=False, wait_index=None, timeout=None):
        key_chunks = split_key(key)
        if not wait:
            try:
                node = reduce(MockNode.get_node, key_chunks, self.root)
            except KeyError:
                raise KeyNotFound(index=self.index)
            return self.make_result(Got, node, remember=False, sorted=sorted)
        # Wait...
        if wait_index is not None:
            indices = self.indices.get(key_chunks, ())
            x = bisect.bisect_left(indices, (wait_index, None))
            for index, exact in indices[x:]:
                if recursive or exact:
                    # Matched past result found.
                    return self.history[index]
        # Register a waiter and wait...
        waiter_key = (recursive, key_chunks)
        waiter = self.waiters.setdefault(waiter_key, Waiter())
        return waiter.get(timeout)

    def set(self, key, value=None, dir=False, ttl=None,
            prev_value=None, prev_index=None, prev_exist=None, timeout=None):
        expiration = ttl and (datetime.utcnow() + timedelta(ttl))
        key_chunks = split_key(key)
        index = self.next_index()
        should_test = prev_value is not None or prev_index is not None
        parent_node = reduce(MockNode.get_node, key_chunks[:-1], self.root)
        try:
            node = parent_node.get_node(key_chunks[-1])
        except KeyError:
            if prev_exist or should_test:
                raise KeyNotFound(index=self.index)
            node = MockNode(key, index, value, dir, ttl, expiration)
            parent_node.add_node(node)
        else:
            if prev_exist is not None and not prev_exist:
                raise NodeExist(index=self.index)
            self.compare(node, prev_value, prev_index)
            node.set(index, value, dir, ttl, expiration)
        return self.make_result(Updated if prev_exist or should_test else Set,
                                node, key_chunks=key_chunks)

    def append(self, key, value=None, dir=False, ttl=None, timeout=None):
        expiration = ttl and (datetime.utcnow() + timedelta(ttl))
        key_chunks = split_key(key)
        parent_node = reduce(MockNode.get_node, key_chunks, self.root)
        for x in itertools.count(len(parent_node.nodes)):
            item_key = '%020d' % x
            if not parent_node.has_node(item_key):
                break
        key = os.path.join(key, item_key)
        index = self.next_index()
        node = MockNode(key, index, value, dir, ttl, expiration)
        parent_node.add_node(node)
        return self.make_result(Created, node, key_chunks=key_chunks)

    def delete(self, key, dir=False, recursive=False,
               prev_value=None, prev_index=None, timeout=None):
        key_chunks = split_key(key)
        parent_node = reduce(MockNode.get_node, key_chunks[:-1], self.root)
        try:
            node = parent_node.get_node(key_chunks[-1])
        except KeyError:
            raise KeyNotFound(index=self.index)
        self.compare(node, prev_value, prev_index)
        parent_node.pop_node(key_chunks[-1])
        return self.make_result(Deleted, prev_node=node, key_chunks=key_chunks)
