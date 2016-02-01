# -*- coding: utf-8 -*-
"""
   etc.errors
   ~~~~~~~~~~
"""
from __future__ import absolute_import

from six import with_metaclass

from .helpers import gen_repr, registry


__all__ = ['CommandError', 'DirNotEmpty', 'Error', 'EtcdError',
           'EventIndexCleared', 'IndexNaN', 'InvalidField', 'InvalidForm',
           'KeyNotFound', 'LeaderElect', 'NodeExist', 'NotDir', 'NotFile',
           'PostFormError', 'PrevValueRequired', 'RaftError', 'RaftInternal',
           'RootROnly', 'TestFailed', 'TimedOut', 'TTLNaN', 'WatcherCleared']


class Error(with_metaclass(registry('errno'), Exception)):
    """A failed etcd result.  It is also can be raised as a Python exception.

    Don't use this class directly.  There're specific sub classes to be used
    instead.

    """

    __slots__ = ('message', 'cause', 'index')

    errno = NotImplemented

    def __init__(self, message=None, cause=None, index=None):
        self.message = message
        self.cause = cause
        self.index = index

    @property
    def args(self):
        return (self.message, self.cause, self.index)

    def __unicode__(self):
        return u'[%d] %s (%s)' % (self.errno, self.message, self.cause)

    def __str__(self):
        return unicode(self).encode()

    def __repr__(self):
        return gen_repr(self.__class__, u'{0}', self, dense=True)


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
