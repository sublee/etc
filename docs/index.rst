etc
===

:mod:`etc` is an `etcd`_ Python client library.  It provides all etcd options
as `snake_case`.  So there's no `camelCase` confusion.  It also provides
several useful sugar functions such as :func:`etc.keep_node`::

   import etc

   etcd = etc.etcd('http://127.0.0.1:4001')

   try:
       etcd.set('/etc', u'what!', prev_value=u'what?', ttl=42)
   except etc.TestFailed:
       pass
   if isinstance(etcd.wait('/etc'), etc.Expired):
       print 'Expired'

.. _etcd: https://coreos.com/etcd/

Installation
~~~~~~~~~~~~

:mod:`etc` is not available in PyPI yet.  You should install via GitHub:

.. sourcecode:: bash

   $ pip install https://github.com/sublee/etc/archive/master.zip

Usage
~~~~~

First of all, create a client object with your etcd URL::

   import etc
   etcd = etc.etcd('http://127.0.0.1:4001')

All etcd methods are in the client.  :meth:`etc.Client.get`,
:meth:`etc.Client.set`, and :meth:`etc.Client.delete` are basic methods for
most cases::

   >>> etcd.set('/hello', u'Hello, world')
   <etc.Set <etc.Value /hello='Hello, world' ...> ...>
   >>> etcd.get('/hello')
   <etc.Got <etc.Value /hello='Hello, world' ...> ...>
   >>> etcd.delete('/hello')
   <etc.Deleted ... prev_node=<etc.Value /hello='Hello, world' ...> ...>
   >>> etcd.get('/hello')
   Traceback (most recent call last):
     ...
   etc.errors.KeyNotFound: [100] Key not found (/hello)

All etcd result types are mapped with subclasses of :class:`etc.EtcdResult`;
:class:`etc.Got`, :class:`etc.Set`, :class:`etc.Deleted`,
:class:`etc.Created`, :class:`etc.Updated`, :class:`etc.Expired`,
:class:`etc.ComparedThenSwapped`, :class:`etc.ComparedThenDeleted`.  A result
contains a node which is an instance of :class:`etc.Node`.  There're 2
subclasses; :class:`etc.Value` and :class:`etc.Directory`.  You will check
whether a node is a directory or not by :func:`isinstance`::

   isinstance(etcd.get('/etc').node, etc.Value)

A directory node can be defined by `dir` parameter::

   >>> etcd.set('/container', dir=True)
   <etc.Set <etc.Directory /container[0] ...> ...>

API
~~~

.. autofunction:: etc.etcd

.. autoclass:: etc.Client
   :members: get, wait, set, create, update, append, delete
   :member-order: bysource

etcd Results
------------

.. autoclass:: etc.Node
.. autoclass:: etc.Value
.. autoclass:: etc.Directory
.. autoclass:: etc.EtcdResult
.. autoclass:: etc.EtcdError

Licensing and Author
~~~~~~~~~~~~~~~~~~~~

This project is licensed under the BSD_ license.  See LICENSE_ for the details.

I'm `Heungsub Lee`_, a game server architect.  Any regarding questions or
patches are welcomed.

.. _BSD: http://en.wikipedia.org/wiki/BSD_licenses
.. _LICENSE: https://github.com/sublee/etc/blob/master/LICENSE
.. _Heungsub Lee: http://subl.ee/
