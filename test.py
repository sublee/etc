# -*- coding: utf-8 -*-
import os

import pytest

import etc


@pytest.fixture
def etcd():
    etcd = etc.etcd(os.getenv('ETC_TEST_ETCD_URL', 'http://localhost:4001'))
    result = etcd.get('/', recursive=True)
    for node in result.nodes:
        dir_ = isinstance(node, etc.Directory)
        print node.key, dir_
        etcd.delete(node.key, dir=dir_, recursive=True)
    return etcd


def test_get_set_delete(etcd):
    r1 = etcd.set('/foo', u'Hello, world')
    assert isinstance(r1, etc.Set)
    r2 = etcd.get('/foo')
    assert isinstance(r2, etc.Got)
    assert r2.value == u'Hello, world'
    assert r1.etcd_index == r2.modified_index
    r3 = etcd.delete('/foo')
    assert isinstance(r3, etc.Deleted)
    with pytest.raises(etc.KeyNotFound):
        etcd.get('/foo')
