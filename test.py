# -*- coding: utf-8 -*-
import os

import pytest

import etc


@pytest.fixture
def etcd():
    etcd = etc.etcd(os.getenv('ETC_TEST_ETCD_URL', 'http://localhost:4001'))
    etcd.delete('/', dir=True, recursive=True)
    return etcd


def test_get_set_delete(etcd):
    r1 = etcd.set('/foo', u'Hello, world')
    assert isinstance(r1, etc.SetResult)
    r2 = etcd.get('/foo')
    assert isinstance(r2, etc.GetResult)
    assert r2.value == u'Hello, world'
    assert r1.etcd_index == r2.modified_index
    r3 = etcd.delete('/foo')
    assert isinstance(r3, etc.DeleteResult)
    with pytest.raises(etc.KeyNotFound):
        etcd.get('/foo')
