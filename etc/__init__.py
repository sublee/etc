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
from .results import (
    CompareAndDeleteResult, CompareAndSwapResult, CreateResult, DeleteResult,
    DirectoryNode, ExpireResult, GetResult, Node, Result, SetResult,
    UpdateResult, ValueNode)
# from .errors import


__all__ = ['Client', 'CompareAndDeleteResult', 'CompareAndSwapResult',
           'CreateResult', 'DeleteResult', 'DirectoryNode', 'etcd',
           'ExpireResult', 'GetResult', 'Node', 'Result', 'SetResult',
           'UpdateResult', 'ValueNode']


#: An alias for :class:`Client`.
etcd = Client
