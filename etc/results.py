# -*- coding: utf-8 -*-
"""
   etc.results
   ~~~~~~~~~~~
"""
from __future__ import absolute_import

import six

from .helpers import gen_repr, registry


__all__ = ['ComparedThenDeleted', 'ComparedThenSwapped', 'Created', 'Deleted',
           'Directory', 'EtcdResult', 'Expired', 'Got', 'Node', 'Set',
           'Updated', 'Value']


def __eq__(self, other):
    """Common `__eq__` implementation for classes which has `__slots__`."""
    if self.__class__ is not other.__class__:
        return False
    return all(getattr(self, attr) == getattr(other, attr)
               for attr in self.__slots__)


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
        """Alias for `modified_index`."""
        return self.modified_index

    @property
    def expires_at(self):
        """Alias for `expiration`."""
        return self.expiration

    __eq__ = __eq__


class Value(Node):
    """An etcd value Node."""

    __slots__ = Node.__slots__ + ('value',)

    def __init__(self, key, value, *args, **kwargs):
        super(Value, self).__init__(key, *args, **kwargs)
        self.value = value

    def __repr__(self):
        options = [('modified_index', self.modified_index),
                   ('created_index', self.created_index),
                   ('ttl', self.ttl),
                   ('expiration', self.expiration)]
        return gen_repr(self.__class__, u'{0}={1}',
                        self.key, self.value, options=options)


class Directory(Node):
    """An etcd directory Node."""

    __slots__ = Node.__slots__ + ('nodes',)

    def __init__(self, key, nodes=(), *args, **kwargs):
        super(Directory, self).__init__(key, *args, **kwargs)
        self.nodes = nodes

    @property
    def values(self):
        return [node.value for node in self.nodes]

    def __repr__(self):
        key = self.key
        if not key.endswith(u'/'):
            key += u'/'
        return gen_repr(self.__class__, u'{0}[{1}]',
                        self.key, len(self.nodes), short=True)


class EtcdResult(six.with_metaclass(registry('action'))):
    """A successful etcd result.

    Don't use this class directly.  There're specific sub classes to be used
    instead.

    """

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
    values = property(lambda x: x.node.values)

    def __repr__(self):
        return gen_repr(self.__class__, u'{0}', self.node, options=[
            ('prev_node', self.prev_node),
            ('etcd_index', self.etcd_index),
            ('raft_index', self.raft_index),
            ('raft_term', self.raft_term),
        ])

    __eq__ = __eq__


def def_(name, action=NotImplemented, base=EtcdResult):
    return type(name, (base,), {'action': action})


Got = def_('Got', 'get')
Set = def_('Set', 'set')
Deleted = def_('Deleted', 'delete')

Updated = def_('Updated', 'update', Set)
Created = def_('Created', 'create', Set)
Expired = def_('Expired', 'expire', Deleted)

ComparedThenSwapped = def_('ComparedThenSwapped', 'compareAndSwap', Set)
ComparedThenDeleted = def_('ComparedThenDeleted', 'compareAndDelete', Deleted)
