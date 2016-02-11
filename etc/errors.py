# -*- coding: utf-8 -*-
"""
   etc.errors
   ~~~~~~~~~~
"""
from __future__ import absolute_import

import socket

import six

from .helpers import gen_repr, registry


__all__ = ['ConnectionError', 'ConnectionRefused', 'DirNotEmpty', 'EtcdError',
           'EtcException', 'EventIndexCleared', 'ExistingPeerAddr', 'IndexNaN',
           'IndexOrValueRequired', 'IndexValueMutex', 'InvalidActiveSize',
           'InvalidField', 'InvalidForm', 'InvalidRemoveDelay',
           'KeyIsPreserved', 'KeyNotFound', 'LeaderElect', 'NameRequired',
           'NodeExist', 'NoMorePeer', 'NotDir', 'NotFile', 'PrevValueRequired',
           'RaftInternal', 'RootROnly', 'StandbyInternal', 'TestFailed',
           'TimedOut', 'TimeoutNaN', 'TTLNaN', 'Unauthorized',
           'ValueOrTTLRequired', 'ValueRequired', 'WatcherCleared']


class EtcException(Exception):
    """A base exception for all exceptions in :mod:`etc`."""

    pass


class EtcdError(six.with_metaclass(registry('errno'), EtcException)):
    """A failed etcd result."""

    __slots__ = ('message', 'cause', 'index')

    errno = NotImplemented

    def __init__(self, message=None, cause=None, index=None):
        self.message = message
        self.cause = cause
        self.index = index

    @property
    def args(self):
        return (self.message, self.cause, self.index)

    @property
    def etcd_index(self):
        return self.index

    def __unicode__(self):
        return u'[%d] %s (%s)' % (self.errno, self.message, self.cause)

    def __str__(self):
        return unicode(self).encode()

    def __repr__(self):
        return gen_repr(self.__class__, u'{0}', self, dense=True)


def def_etcd_error(name, errno=NotImplemented, base=EtcdError):
    return type(name, (base,), {'errno': errno})


# Command related errors.
KeyNotFound = def_etcd_error('KeyNotFound', 100)
TestFailed = def_etcd_error('TestFailed', 101)
NotFile = def_etcd_error('NotFile', 102)
NoMorePeer = def_etcd_error('NoMorePeer', 103)  # private
NotDir = def_etcd_error('NotDir', 104)
NodeExist = def_etcd_error('NodeExist', 105)
KeyIsPreserved = def_etcd_error('KeyIsPreserved', 106)  # private
RootROnly = def_etcd_error('RootROnly', 107)
DirNotEmpty = def_etcd_error('DirNotEmpty', 108)
ExistingPeerAddr = def_etcd_error('ExistingPeerAddr', 109)  # private
Unauthorized = def_etcd_error('Unauthorized', 110)


# POST form related errors.
ValueRequired = def_etcd_error('ValueRequired', 200)  # private
PrevValueRequired = def_etcd_error('PrevValueRequired', 201)
TTLNaN = def_etcd_error('TTLNaN', 202)
IndexNaN = def_etcd_error('IndexNaN', 203)
ValueOrTTLRequired = def_etcd_error('ValueOrTTLRequired', 204)  # private
TimeoutNaN = def_etcd_error('TimeoutNaN', 205)  # private
NameRequired = def_etcd_error('NameRequired', 206)  # private
IndexOrValueRequired = def_etcd_error('IndexOrValueRequired', 207)  # private
IndexValueMutex = def_etcd_error('IndexValueMutex', 208)  # private
InvalidField = def_etcd_error('InvalidField', 209)
InvalidForm = def_etcd_error('InvalidForm', 210)


# Raft related errors.
RaftInternal = def_etcd_error('RaftInternal', 300)
LeaderElect = def_etcd_error('LeaderElect', 301)


# etcd related errors.
WatcherCleared = def_etcd_error('WatcherCleared', 400)
EventIndexCleared = def_etcd_error('EventIndexCleared', 401)
StandbyInternal = def_etcd_error('StandbyInternal', 402)  # private
InvalidActiveSize = def_etcd_error('InvalidActiveSize', 403)  # private
InvalidRemoveDelay = def_etcd_error('InvalidRemoveDelay', 404)  # private


class ConnectionError(EtcException, socket.error):
    """A TCP connection related error."""

    pass


class TimedOut(ConnectionError):
    """A request timed out."""

    pass


class ConnectionRefused(ConnectionError):
    """The etcd server refused the connection."""

    pass
