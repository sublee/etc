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
    CommandError, DirNotEmpty, Error, EtcdError, EventIndexCleared, IndexNaN,
    InvalidField, InvalidForm, KeyNotFound, LeaderElect, NodeExist, NotDir,
    NotFile, PostFormError, PrevValueRequired, RaftError, RaftInternal,
    RootROnly, TestFailed, TimedOut, TTLNaN, WatcherCleared)
from .results import (
    ComparedThenDeleted, ComparedThenSwapped, Created, Deleted, Directory,
    Expired, Got, Node, Result, Set, Updated, Value)
# from .errors import


__all__ = [
    # etc
    'etcd',
    # etc.client
    'Client',
    # etc.errors
    'CommandError', 'DirNotEmpty', 'Error', 'EtcdError', 'EventIndexCleared',
    'IndexNaN', 'InvalidField', 'InvalidForm', 'KeyNotFound', 'LeaderElect',
    'NodeExist', 'NotDir', 'NotFile', 'PostFormError', 'PrevValueRequired',
    'RaftError', 'RaftInternal', 'RootROnly', 'TestFailed', 'TimedOut',
    'TTLNaN', 'WatcherCleared',
    # etc.results
    'ComparedThenDeleted', 'ComparedThenSwapped', 'Created', 'Deleted',
    'Directory', 'Expired', 'Got', 'Node', 'Result', 'Set', 'Updated', 'Value',
]


#: An alias for :class:`Client`.
etcd = Client
