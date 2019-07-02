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


def test_cache_forced_update(app, cache):
    from collections import Counter

    with app.test_request_context():
        need_update = False
        call_counter = Counter()

        @cache.cached(1, forced_update=lambda: need_update)
        def cached_function(param):
            call_counter[param] += 1

            return 1

        cached_function(1)
        assert call_counter[1] == 1

        assert cached_function(1) == 1
        assert call_counter[1] == 1

        need_update = True

        assert cached_function(1) == 1
        assert call_counter[1] == 2


def test_cache_forced_update_params(app, cache):
    from collections import Counter

    with app.test_request_context():
        cached_call_counter = Counter()
        call_counter = Counter()
        call_params = {}

        def need_update(param):
            """This helper function returns True if it has been called with
            the same params for more than 2 times
            """

            call_counter[param] += 1
            call_params[call_counter[param] - 1] = (param,)

            return call_counter[param] > 2

        @cache.cached(1, forced_update=need_update)
        def cached_function(param):
            cached_call_counter[param] += 1

            return 1

        assert cached_function(1) == 1
        # need_update should have been called once
        assert call_counter[1] == 1
        # the parameters used to call need_update should be the same as the
        # parameters used to call cached_function
        assert call_params[0] == (1,)
        # the cached function should have been called once
        assert cached_call_counter[1] == 1

        assert cached_function(1) == 1
        # need_update should have been called twice by now as forced_update
        # should be called regardless of the arguments
        assert call_counter[1] == 2
        # the parameters used to call need_update should be the same as the
        # parameters used to call cached_function
        assert call_params[1] == (1,)
        # this time the forced_update should have returned False, so
        # cached_function should not have been called again
        assert cached_call_counter[1] == 1

        assert cached_function(1) == 1
        # need_update should have been called thrice by now as forced_update
        # should be called regardless of the arguments
        assert call_counter[1] == 3
        # the parameters used to call need_update should be the same as the
        # parameters used to call cached_function
        assert call_params[1] == (1,)
        # this time the forced_update should have returned True, so
        # cached_function should have been called again
        assert cached_call_counter[1] == 2
