# -*- coding: utf-8 -*-
"""
   etc.results
   ~~~~~~~~~~~
"""
from __future__ import absolute_import

from six import with_metaclass

from .helpers import registry


__all__ = ['ComparedThenDeleted', 'ComparedThenSwapped', 'Created', 'Deleted',
           'Directory', 'Expired', 'Got', 'Node', 'Result', 'Set',
           'Updated', 'Value']


class Node(object):

    __slots__ = ('key', 'modified_index', 'created_index', 'ttl', 'expiration')

    def __init__(self, key, modified_index=None, created_index=None,
                 ttl=None, expiration=None):
        self.key = key
        self.modified_index = modified_index
        self.created_index = created_index
        self.ttl = ttl
        self.expiration = expiration

    @property
    def index(self):
        return self.modified_index

    @property
    def expires_at(self):
        return self.expiration


class Value(Node):

    __slots__ = Node.__slots__ + ('value',)

    def __init__(self, key, value, *args, **kwargs):
        super(Value, self).__init__(key, *args, **kwargs)
        self.value = value


class Directory(Node):

    __slots__ = Node.__slots__ + ('nodes',)

    def __init__(self, key, nodes=(), *args, **kwargs):
        super(Directory, self).__init__(key, *args, **kwargs)
        self.nodes = nodes


class Result(with_metaclass(registry('action'))):

    __slots__ = ('node', 'prev_node', 'etcd_index', 'raft_index', 'raft_term')

    action = NotImplemented

    def __init__(self, node, prev_node=None,
                 etcd_index=None, raft_index=None, raft_term=None):
        self.node = node
        self.prev_node = prev_node
        self.etcd_index = etcd_index
        self.raft_index = raft_index
        self.raft_term = raft_term

    # Node accessors.
    key = property(lambda x: x.node.key)
    modified_index = property(lambda x: x.node.modified_index)
    created_index = property(lambda x: x.node.created_index)
    ttl = property(lambda x: x.node.ttl)
    expiration = property(lambda x: x.node.expiration)
    index = property(lambda x: x.node.index)
    expires_at = property(lambda x: x.node.expires_at)
    value = property(lambda x: x.node.value)
    nodes = property(lambda x: x.node.nodes)


def def_(name, action=NotImplemented, base=Result):
    return type(name, (base,), {'action': action})

Got = def_('Got', 'get')
Set = def_('Set', 'set')
Deleted = def_('Deleted', 'delete')

Updated = def_('Updated', 'update', Set)
Created = def_('Created', 'create', Set)
Expired = def_('Expired', 'expire', Deleted)

ComparedThenSwapped = def_('ComparedThenSwapped', 'compareAndSwap', Set)
ComparedThenDeleted = def_('ComparedThenDeleted', 'compareAndDelete', Deleted)
