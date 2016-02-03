# -*- coding: utf-8 -*-
"""
   etc
   ~~~

   An etcd client library for humans.

   - Don't mix "camelCase" on your Python code.
   - Test without real etcd by mockup clients.
   - Proper options for actions.
   - Sugars for most cases.

   :copyright: (c) 2016 by Heungsub Lee
   :license: BSD, see LICENSE for more details.

"""
from __future__ import absolute_import

from .__about__ import __version__  # noqa
from .client import Client
from .errors import (
    ConnectionError, ConnectionRefused, DirNotEmpty, EtcdError, EtcException,
    EventIndexCleared, ExistingPeerAddr, IndexNaN, IndexOrValueRequired,
    IndexValueMutex, InvalidActiveSize, InvalidField, InvalidForm,
    InvalidRemoveDelay, KeyIsPreserved, KeyNotFound, LeaderElect, NameRequired,
    NodeExist, NoMorePeer, NotDir, NotFile, PrevValueRequired, RaftInternal,
    RootROnly, StandbyInternal, TestFailed, TimedOut, TimeoutNaN, TTLNaN,
    Unauthorized, ValueOrTTLRequired, ValueRequired, WatcherCleared)
from .results import (
    ComparedThenDeleted, ComparedThenSwapped, Created, Deleted, Directory,
    EtcdResult, Expired, Got, Node, Set, Updated, Value)
# from .errors import


__all__ = [
    # etc
    'etcd',
    # etc.client
    'Client',
    # etc.errors
    'ConnectionError', 'ConnectionRefused', 'DirNotEmpty', 'EtcdError',
    'EtcException', 'EventIndexCleared', 'ExistingPeerAddr', 'IndexNaN',
    'IndexOrValueRequired', 'IndexValueMutex', 'InvalidActiveSize',
    'InvalidField', 'InvalidForm', 'InvalidRemoveDelay', 'KeyIsPreserved',
    'KeyNotFound', 'LeaderElect', 'NameRequired', 'NodeExist', 'NoMorePeer',
    'NotDir', 'NotFile', 'PrevValueRequired', 'RaftInternal', 'RootROnly',
    'StandbyInternal', 'TestFailed', 'TimedOut', 'TimeoutNaN', 'TTLNaN',
    'Unauthorized', 'ValueOrTTLRequired', 'ValueRequired', 'WatcherCleared',
    # etc.results
    'ComparedThenDeleted', 'ComparedThenSwapped', 'Created', 'Deleted',
    'Directory', 'EtcdResult', 'Expired', 'Got', 'Node', 'Set', 'Updated',
    'Value',
]


#: An alias for :class:`Client`.
etcd = Client
