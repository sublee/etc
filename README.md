# etc

An etcd Python client library for humans.

[![Build Status]
(https://img.shields.io/travis/sublee/etc.svg)]
(https://travis-ci.org/sublee/etc)
[![Coverage Status]
(https://img.shields.io/coveralls/sublee/etc.svg)]
(https://coveralls.io/r/sublee/etc)

```python
>>> import etc
>>> etcd = etc.etcd('http://127.0.0.1:4001')

>>> etcd.set('/etc/foo', u'1')
<etc.Set <etc.Value /etc/foo=1 ...> ...>
>>> etcd.set('/etc/bar', u'2', ttl=3)
<etc.Set <etc.Value /etc/bar=2 ttl=3 ...> ...>

>>> etcd.get('/etc/foo')
<etc.Got <etc.Value /etc/foo=1 ...> ...>
>>> etcd.get('/etc')
<etc.Got <etc.Directory /etc[2] ...> ...>

>>> etcd.append('/etc', u'etc')
<etc.Created <etc.Value /etc/00000000000000000042=etc ...> ...>

>>> etcd.wait('/etc', recursive=True)
<etc.Created <etc.Value /etc/00000000000000000043=what ...> ...>
```
