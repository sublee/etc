# -*- coding: utf-8 -*-
import multiprocessing
import os
import time

import pytest
from six import b, u

import etc


@pytest.fixture
def etcd():
    etcd = etc.etcd(os.getenv('ETC_TEST_ETCD_URL', 'http://127.0.0.1:4001'))
    result = etcd.get('/', recursive=True)
    for node in result.nodes:
        dir_ = isinstance(node, etc.Directory)
        etcd.delete(node.key, dir=dir_, recursive=True)
    return etcd


@pytest.fixture
def spawn(request):
    def spawn_f(f, *args, **kwargs):
        proc = multiprocessing.Process(target=f, args=args, kwargs=kwargs)
        proc.start()
        request.addfinalizer(proc.terminate)
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
    assert isinstance(r1, etc.Set)
    r2 = etcd.get('/etc')
    assert isinstance(r2, etc.Got)
    assert r2.value == u('Hello, world')
    assert r1.etcd_index == r2.modified_index
    r3 = etcd.delete('/etc')
    assert isinstance(r3, etc.Deleted)
    with pytest.raises(etc.KeyNotFound):
        etcd.get('/etc')


def test_wait(etcd, spawn_later):
    etcd.set('/etc', u('one'))
    spawn_later(0.1, etcd.set, '/etc', u('two'))
    r = etcd.get('/etc')
    assert r.value == u('one')
    r = etcd.wait('/etc', r.index + 1)
    assert r.value == u('two')
    spawn_later(0.1, etcd.set, '/etc', u('three'))
    spawn_later(0.2, etcd.set, '/etc', u('four'))
    r = etcd.wait('/etc', r.index + 1)
    assert r.value == u('three')
    r = etcd.wait('/etc', r.index + 1)
    assert r.value == u('four')


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
