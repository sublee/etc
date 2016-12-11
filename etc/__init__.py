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

from etc.__about__ import __version__  # noqa
from etc.client import Client
from etc.errors import (
    ConnectionError, ConnectionRefused, DirNotEmpty, EtcdError, EtcException,
    EventIndexCleared, ExistingPeerAddr, IndexNaN, IndexOrValueRequired,
    IndexValueMutex, InvalidActiveSize, InvalidField, InvalidForm,
    InvalidRemoveDelay, KeyIsPreserved, KeyNotFound, LeaderElect, NameRequired,
    NodeExist, NoMorePeer, NotDir, NotFile, PrevValueRequired, RaftInternal,
    RefreshTTLRequired, RefreshValue, RootROnly, StandbyInternal, TestFailed,
    TimedOut, TimeoutNaN, TTLNaN, Unauthorized, ValueOrTTLRequired,
    ValueRequired, WatcherCleared)
from etc.results import (
    ComparedThenDeleted, ComparedThenSwapped, Created, Deleted, Directory,
    EtcdResult, Expired, Got, Node, Set, Updated, Value)


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
    'NotDir', 'NotFile', 'PrevValueRequired', 'RaftInternal',
    'RefreshTTLRequired', 'RefreshValue', 'RootROnly', 'StandbyInternal',
    'TestFailed', 'TimedOut', 'TimeoutNaN', 'TTLNaN', 'Unauthorized',
    'ValueOrTTLRequired', 'ValueRequired', 'WatcherCleared',
    # etc.results
    'ComparedThenDeleted', 'ComparedThenSwapped', 'Created', 'Deleted',
    'Directory', 'EtcdResult', 'Expired', 'Got', 'Node', 'Set', 'Updated',
    'Value',
]


DEFAULT_URL = 'http://127.0.0.1:4001'


def etcd(url=DEFAULT_URL, mock=False, **kwargs):
    """Creates an etcd client."""
    if mock:
        from etc.adapters.mock import MockAdapter
        adapter_class = MockAdapter
    else:
        from etc.adapters.etcd import EtcdAdapter
        adapter_class = EtcdAdapter
    return Client(adapter_class(url, **kwargs))
