# -*- coding: utf-8 -*-
import random
import time


def test_cache_set(app, cache):
    cache.set('hi', 'hello')

    assert cache.get('hi') == 'hello'


def test_cache_add(app, cache):
    cache.add('hi', 'hello')
    assert cache.get('hi') == 'hello'

    cache.add('hi', 'foobar')
    assert cache.get('hi') == 'hello'


def test_cache_delete(app, cache):
    cache.set('hi', 'hello')
    cache.delete('hi')
    assert cache.get('hi') is None


def test_cache_cached_function(app, cache):
    with app.test_request_context():
        @cache.cached(2, key_prefix='MyBits')
        def get_random_bits():
            return [random.randrange(0, 2) for i in range(50)]

        my_list = get_random_bits()
        his_list = get_random_bits()

        assert my_list == his_list

        time.sleep(4)

        his_list = get_random_bits()

        assert my_list != his_list
