etc
===

:mod:`etc` is an `etcd`_ Python client library.  It provides all etcd options
as `snake_case`.  There's no `camelCase` confusion.  Also :mod:`etc` provides
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
