# -*- coding: utf-8 -*-
from datetime import datetime
import os
import socket
import threading
import time

import pytest
from six import b, u

import etc


ETC_TEST_ETCD_URL = os.getenv('ETC_TEST_ETCD_URL', 'http://127.0.0.1:2379')


def node_keys(nodes):
    return [n.key for n in nodes]


def node_values(nodes):
    return [n.value for n in nodes]


@pytest.fixture(params=['etcd', 'mock'])
def etcd(request):
    mode = request.param
    mark = request.node.get_marker('etcd')
    if mark and mode in mark.kwargs.get('skip', ()):
        pytest.skip('%s skips for %s' % (request.node.name, mode))
    if mode == 'etcd':
        etcd = etc.etcd(ETC_TEST_ETCD_URL)
    elif mode == 'mock':
        etcd = etc.etcd(mock=True)
    else:
        raise AssertionError
    result = etcd.get('/', recursive=True)
    for node in result.nodes:
        dir_ = isinstance(node, etc.Directory)
        etcd.delete(node.key, dir=dir_, recursive=True)
    return etcd


@pytest.fixture
def spawn(request):
    def spawn_f(f, *args, **kwargs):
        thread = threading.Thread(target=f, args=args, kwargs=kwargs)
        thread.start()
        request.addfinalizer(thread.join)
    return spawn_f


@pytest.fixture
def spawn_later(request):
    spawn_f = spawn(request)
    def spawn_later_f(seconds, f, *args, **kwargs):
        def delay(*args, **kwargs):
            time.sleep(seconds)
            return f(*args, **kwargs)
        return spawn_f(delay, *args, **kwargs)
    return spawn_later_f


def test_etcd():
    e = etc.etcd()
    assert isinstance(e, etc.Client)


def test_default_address():
    assert etc.etcd().url == 'http://127.0.0.1:4001'
    # assert etc.etcd('http://10.10.10.10').url == 'http://10.10.10.10:4001'


def test_set_only_unicode(etcd):
    with pytest.raises(TypeError):
        etcd.set('/etc', 42)
    with pytest.raises(TypeError):
        etcd.set('/etc', b('42'))
    assert etcd.set('/etc', u('42')).value == u('42')


def test_get_set_delete(etcd):
    r1 = etcd.set('/etc', u('Hello, world'))
    assert r1.__class__ is etc.Set
    r2 = etcd.get('/etc')
    assert r2.__class__ is etc.Got
    assert r2.value == u('Hello, world')
    assert r1.etcd_index == r2.modified_index
    r3 = etcd.delete('/etc')
    assert r3.__class__ is etc.Deleted
    with pytest.raises(etc.KeyNotFound):
        etcd.get('/etc')


def test_wait(etcd, spawn_later):
    etcd.set('/etc', u('one'))
    spawn_later(0.1, etcd.set, '/etc', u('two'))
    r = etcd.get('/etc')
    assert r.__class__ is etc.Got
    assert r.value == u('one')
    r = etcd.wait('/etc', r.index + 1)
    assert r.__class__ is etc.Set
    assert r.value == u('two')
    spawn_later(0.1, etcd.set, '/etc', u('three'))
    spawn_later(0.2, etcd.set, '/etc', u('four'))
    r = etcd.wait('/etc', r.index + 1)
    assert r.__class__ is etc.Set
    assert r.value == u('three')
    r = etcd.wait('/etc', r.index + 1)
    assert r.__class__ is etc.Set
    assert r.value == u('four')


def test_recursive_wait(etcd, spawn_later):
    r = etcd.set('/etc', dir=True)
    assert r.__class__ is etc.Set
    assert isinstance(r.node, etc.Directory)
    spawn_later(0.1, etcd.set, '/etc/1', u('one'))
    spawn_later(0.2, etcd.set, '/etc/2', u('two'))
    spawn_later(0.3, etcd.update, '/etc', dir=True, ttl=10)
    r = etcd.wait('/etc', r.index + 1, recursive=True)
    assert r.__class__ is etc.Set
    assert r.key == '/etc/1'
    r = etcd.wait('/etc', r.index + 1, recursive=True)
    assert r.__class__ is etc.Set
    assert r.key == '/etc/2'
    r = etcd.wait('/etc', r.index + 1, recursive=True)
    assert r.__class__ is etc.Updated
    assert r.key == '/etc'
    r = etcd.set('/etc/3', u'three')
    r = etcd.wait('/etc', r.index, recursive=True)
    assert r.__class__ is etc.Set
    assert r.key == '/etc/3'


def test_append(etcd, spawn_later):
    r = etcd.set('/etc', dir=True)
    spawn_later(0.1, etcd.append, '/etc', u('one'))
    spawn_later(0.2, etcd.append, '/etc', u('two'))
    spawn_later(0.3, etcd.append, '/etc', u('three'))
    spawn_later(0.4, etcd.append, '/etc', u('four'))
    r = etcd.wait('/etc', r.index + 1, recursive=True)
    assert r.value == u('one')
    r = etcd.wait('/etc', r.index + 1, recursive=True)
    assert r.value == u('two')
    r = etcd.wait('/etc', r.index + 1, recursive=True)
    assert r.value == u('three')
    r = etcd.wait('/etc', r.index + 1, recursive=True)
    assert r.value == u('four')
    r = etcd.get('/etc', sorted=True)
    assert r.values == [u('one'), u('two'), u('three'), u('four')]


def test_timeout(etcd):
    with pytest.raises(etc.TimedOut):
        etcd.wait('/etc', timeout=0.1)


def test_history(etcd):
    r1 = etcd.set('/etc', dir=True, ttl=10)
    etcd.set('/etc/1', u'1')
    r2 = etcd.update('/etc', dir=True, ttl=20)
    etcd.set('/etc/2', u'2')
    r3 = etcd.wait('/etc', r1.index)
    assert r3.ttl == 10
    assert not r3.nodes  # wait() doesn't receive nodes.
    r4 = etcd.wait('/etc', r2.index)
    assert r4.ttl == 20
    assert not r4.nodes
    r5 = etcd.get('/etc', sorted=True)
    assert r5.ttl == 20
    assert node_keys(r5.nodes) == ['/etc/1', '/etc/2']


def test_recursive_wait_with_old_history(etcd):
    r = etcd.set('/etc', dir=True)
    etcd.set('/etc/xxx', u'1')
    etcd.set('/etc/xxx', u'2')
    etcd.update('/etc', dir=True, ttl=10)
    # Wait not recursively.
    r1 = etcd.wait('/etc', r.index + 1)
    assert r1.__class__ is etc.Updated
    assert r1.key == '/etc'
    assert r1.ttl == 10
    # Wait recursively.
    r2 = etcd.wait('/etc', r.index + 1, recursive=True)
    assert r2.__class__ is etc.Set
    assert r2.key == '/etc/xxx'
    assert r2.value == u'1'
    r3 = etcd.wait('/etc', r2.index + 1, recursive=True)
    assert r3.__class__ is etc.Set
    assert r3.key == '/etc/xxx'
    assert r3.value == u'2'
    r4 = etcd.wait('/etc', r3.index + 1, recursive=True)
    assert r1.node == r4.node


def test_compare(etcd):
    # prev_exist
    etcd.create('/etc', u'1')
    with pytest.raises(etc.NodeExist):
        etcd.create('/etc', u'2')
    etcd.set('/etc', u'3')
    etcd.update('/etc', u'4')
    with pytest.raises(etc.KeyNotFound):
        etcd.update('/xxx', u'---')
    # prev_value
    etcd.update('/etc', u'5', prev_value=u'4')
    with pytest.raises(etc.TestFailed):
        etcd.update('/etc', u'6', prev_value=u'4')
    # prev_index
    r = etcd.get('/etc')
    with pytest.raises(etc.TestFailed):
        etcd.update('/etc', u'7', prev_index=r.index * 2)
    etcd.update('/etc', u'8', prev_index=r.index)
    # delete
    with pytest.raises(etc.TestFailed):
        etcd.delete('/etc', prev_value=u'000')
    etcd.delete('/etc', prev_value=u'8')
    with pytest.raises(etc.KeyNotFound):
        etcd.delete('/etc', prev_value=u'8')
    with pytest.raises(etc.KeyNotFound):
        etcd.delete('/etc')


def test_expiration(etcd):
    r = etcd.set('/etc', u'etc', ttl=10)
    assert isinstance(r.expiration, datetime)


def test_chunked_encoding_error(spawn):
    server = socket.socket()
    server.bind(('', 0))
    server.listen(10)
    __, port = server.getsockname()
    def bad_web_server():
        header = '\r\n'.join([
            'HTTP/1.1 200 OK',
            'Content-Type: application/json',
            'X-Etcd-Cluster-Id: 42',
            'X-Etcd-Index: 42',
            'X-Raft-Index: 42',
            'X-Raft-Term: 42',
            'Transfer-Encoding: chunked'
        ]) + '\r\n\r\n'
        data = ('{"action":"set","node":{"key":"/etc","value":'
                '"ok","modifiedIndex":42,"createdIndex":42}}')
        # Bad response.
        conn, __ = server.accept()
        conn.send(header.encode())
        conn.close()
        # Good response.
        conn, __ = server.accept()
        response = header + '%x\r\n%s\r\n0\r\n\r\n' % (len(data), data)
        conn.send(response.encode())
        conn.close()
    spawn(bad_web_server)
    etcd = etc.etcd('http://127.0.0.1:%d' % port)
    r = etcd.wait('/etc')
    assert isinstance(r, etc.Set)
    assert r.modified_index == r.created_index == 42


def test_session(monkeypatch):
    etcd = etc.etcd(ETC_TEST_ETCD_URL)
    etcd.get('/')
    monkeypatch.setattr(socket.socket, 'connect', lambda *a, **k: 0 / 0)
    etcd.get('/')
    etcd.clear()
    with pytest.raises(ZeroDivisionError):
        etcd.get('/')


@pytest.mark.etcd(skip=['mock'])
def test_refresh(etcd, spawn):
    with pytest.raises(etc.KeyNotFound):
        # Key not set yet.
        etcd.set('/etc', ttl=1, refresh=True)
    r = etcd.set('/etc', u'etc')
    with pytest.raises(etc.RefreshValue):
        # To refresh TTL, don't pass value.
        etcd.set('/etc', u'etc', ttl=1, refresh=True)
    with pytest.raises(etc.TestFailed):
        etcd.set('/etc', ttl=1, refresh=True, prev_index=r.index - 1)
    r = etcd.set('/etc', ttl=1, refresh=True, prev_index=r.index)
    assert isinstance(r, etc.ComparedThenSwapped)
    r = etcd.set('/etc', ttl=1, refresh=True)
    assert isinstance(r, etc.Set)
    # Only for files.
    etcd.set('/dir', dir=True)
    with pytest.raises(etc.NotFile):
        etcd.set('/dir', ttl=1, refresh=True)
    # Don't wake up many times.
    t = time.time()
    etcd.set('/etc', u'etc', ttl=0)
    results = []
    spawn(lambda: results.append(etcd.set('/etc', ttl=1, refresh=True)))
    r = etcd.wait('/etc')
    assert results
    assert isinstance(r, etc.Expired)
    assert r.index > results[0].index
    assert time.time() - t >= 1


def test_503_service_unavailable(spawn):
    server = socket.socket()
    server.bind(('', 0))
    server.listen(10)
    __, port = server.getsockname()
    def dead_web_server():
        response = '\r\n'.join([
            'HTTP/1.1 503 Service Unavailable',
            'Content-Type: text/html; charset=UTF-8',
            'Connection: close',
        ]) + '\r\n\r\n'
        conn, __ = server.accept()
        conn.send(response.encode())
        conn.close()
    spawn(dead_web_server)
    etcd = etc.etcd('http://127.0.0.1:%d' % port)
    with pytest.raises(etc.HTTPError) as excinfo:
        etcd.get('/etc')
    assert excinfo.value.status_code == 503
