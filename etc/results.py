# -*- coding: utf-8 -*-
"""
   etc.results
   ~~~~~~~~~~~
"""
from __future__ import absolute_import

from six import with_metaclass


__all__ = ['CompareAndDeleteResult', 'CompareAndSwapResult', 'CreateResult',
           'DeleteResult', 'DirectoryNode', 'ExpireResult', 'GetResult',
           'Node', 'Result', 'SetResult', 'UpdateResult', 'ValueNode']


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


class ValueNode(Node):

    __slots__ = Node.__slots__ + ('value',)

    def __init__(self, key, value, *args, **kwargs):
        super(ValueNode, self).__init__(key, *args, **kwargs)
        self.value = value


class DirectoryNode(Node):

    __slots__ = Node.__slots__ + ('nodes',)

    def __init__(self, key, nodes=(), *args, **kwargs):
        super(DirectoryNode, self).__init__(key, *args, **kwargs)
        self.nodes = nodes


class ResultMeta(type):

    def __init__(cls, name, bases, attrs):
        super(ResultMeta, cls).__init__(name, bases, attrs)
        if cls.action is not NotImplemented:
            assert cls.action not in cls.__registry__
            cls.__registry__[cls.action] = cls


class Result(with_metaclass(ResultMeta)):

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

    __registry__ = {}

    @classmethod
    def make(cls, action, *args, **kwargs):
        try:
            sub_cls = cls.__registry__[action]
        except KeyError:
            raise ValueError('Unknown action: %s' % action)
        else:
            return sub_cls(*args, **kwargs)


class GetResult(Result):

    action = 'get'


class SetResult(Result):

    action = 'set'


class UpdateResult(Result):

    action = 'update'


class CreateResult(Result):

    action = 'create'


class ExpireResult(Result):

    action = 'expire'


class DeleteResult(Result):

    action = 'delete'


class CompareAndSwapResult(Result):

    action = 'compareAndSwap'


class CompareAndDeleteResult(Result):

    action = 'compareAndDelete'
