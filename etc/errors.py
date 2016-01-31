# -*- coding: utf-8 -*-
"""
   etc.errors
   ~~~~~~~~~~
"""
from __future__ import absolute_import

from six import with_metaclass

from .helpers import registry


__all__ = ['CommandError', 'DirNotEmpty', 'Error', 'EtcdError',
           'EventIndexCleared', 'IndexNaN', 'InvalidField', 'InvalidForm',
           'KeyNotFound', 'LeaderElect', 'NodeExist', 'NotDir', 'NotFile',
           'PostFormError', 'PrevValueRequired', 'RaftError', 'RaftInternal',
           'RootROnly', 'TestFailed', 'TTLNaN', 'WatcherCleared']


class Error(with_metaclass(registry('errno'), Exception)):

    __slots__ = ('index', 'message', 'cause')

    errno = NotImplemented

    def __init__(self, message=None, cause=None, index=None):
        self.messge = message
        self.cause = cause
        self.index = index

    __registry__ = {}

    @classmethod
    def make(cls, errno, *args, **kwargs):
        try:
            sub_cls = cls.__registry__[errno]
        except KeyError:
            raise ValueError('Unknown errno: %s' % errno)
        else:
            return sub_cls(*args, **kwargs)


def def_(name, errno=NotImplemented, base=Error):
    return type(name, (base,), {'errno': errno})

CommandError = def_('CommandError')
PostFormError = def_('PostFormError')
RaftError = def_('RaftError')
EtcdError = def_('EtcdError')

KeyNotFound = def_('KeyNotFound', 100, CommandError)
TestFailed = def_('TestFailed', 101, CommandError)
NotFile = def_('NotFile', 102, CommandError)
NotDir = def_('NotDir', 104, CommandError)
NodeExist = def_('NodeExist', 105, CommandError)
RootROnly = def_('RootROnly', 107, CommandError)
DirNotEmpty = def_('DirNotEmpty', 108, CommandError)

PrevValueRequired = def_('PrevValueRequired', 201, PostFormError)
TTLNaN = def_('TTLNaN', 202, PostFormError)
IndexNaN = def_('IndexNaN', 203, PostFormError)
InvalidField = def_('InvalidField', 209, PostFormError)
InvalidForm = def_('InvalidForm', 210, PostFormError)

RaftInternal = def_('RaftInternal', 300, RaftError)
LeaderElect = def_('LeaderElect', 301, RaftError)

WatcherCleared = def_('WatcherCleared', 400, EtcdError)
EventIndexCleared = def_('EventIndexCleared', 401, EtcdError)
