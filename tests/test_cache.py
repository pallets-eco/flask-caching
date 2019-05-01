# -*- coding: utf-8 -*-
import random
import time

from flask_caching import Cache


def test_cache_set(app, cache):
    cache.set("hi", "hello")

    assert cache.get("hi") == "hello"


def test_cache_add(app, cache):
    cache.add("hi", "hello")
    assert cache.get("hi") == "hello"

    cache.add("hi", "foobar")
    assert cache.get("hi") == "hello"


def test_cache_delete(app, cache):
    cache.set("hi", "hello")
    cache.delete("hi")
    assert cache.get("hi") is None


def test_cache_delete_many(app, cache):
    cache.set("hi", "hello")
    cache.delete_many("ho", "hi")
    assert cache.get("hi") is not None


def test_cache_delete_many_ignored(app):
    cache = Cache(config={"CACHE_TYPE": "simple", "CACHE_IGNORE_ERRORS": True})
    cache.init_app(app)

    cache.set("hi", "hello")
    assert cache.get("hi") == "hello"
    cache.delete_many("ho", "hi")
    assert cache.get("hi") is None


def test_cache_cached_function(app, cache):
    with app.test_request_context():

        @cache.cached(1, key_prefix="MyBits")
        def get_random_bits():
            return [random.randrange(0, 2) for i in range(50)]

        my_list = get_random_bits()
        his_list = get_random_bits()

        assert my_list == his_list

        time.sleep(2)

        his_list = get_random_bits()

        assert my_list != his_list


def test_cache_accepts_multiple_ciphers(app, cache, hash_method):
    with app.test_request_context():

        @cache.cached(1, key_prefix="MyBits", hash_method=hash_method)
        def get_random_bits():
            return [random.randrange(0, 2) for i in range(50)]

        my_list = get_random_bits()
        his_list = get_random_bits()

        assert my_list == his_list

        time.sleep(2)

        his_list = get_random_bits()

        assert my_list != his_list


def test_cached_none(app, cache):
    with app.test_request_context():
        from collections import Counter

        call_counter = Counter()

        @cache.cached()
        def cache_none(param):
            call_counter[param] += 1

            return None

        cache_none(1)

        assert call_counter[1] == 1
        assert cache_none(1) is None
        assert call_counter[1] == 1

        cache.clear()

        cache_none(1)
        assert call_counter[1] == 2
