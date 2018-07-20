# -*- coding: utf-8 -*-
import time
from flask import request


def test_cached_view(app, cache):
    @app.route('/')
    @cache.cached(2)
    def cached_view():
        return str(time.time())

    tc = app.test_client()

    rv = tc.get('/')
    the_time = rv.data.decode('utf-8')

    time.sleep(1)

    rv = tc.get('/')

    assert the_time == rv.data.decode('utf-8')

    time.sleep(1)

    rv = tc.get('/')
    assert the_time != rv.data.decode('utf-8')


def test_cached_view_unless(app, cache):
    @app.route('/a')
    @cache.cached(5, unless=lambda: True)
    def non_cached_view():
        return str(time.time())

    @app.route('/b')
    @cache.cached(5, unless=lambda: False)
    def cached_view():
        return str(time.time())

    tc = app.test_client()

    rv = tc.get('/a')
    the_time = rv.data.decode('utf-8')

    time.sleep(1)

    rv = tc.get('/a')
    assert the_time != rv.data.decode('utf-8')

    rv = tc.get('/b')
    the_time = rv.data.decode('utf-8')

    time.sleep(1)
    rv = tc.get('/b')

    assert the_time == rv.data.decode('utf-8')


def test_cached_view_forced_update(app, cache):
    forced_update = False

    @app.route('/a')
    @cache.cached(5, forced_update=lambda: forced_update)
    def view():
        return str(time.time())

    tc = app.test_client()

    rv = tc.get('/a')
    the_time = rv.data.decode('utf-8')
    time.sleep(1)
    rv = tc.get('/a')
    assert the_time == rv.data.decode('utf-8')

    forced_update = True
    rv = tc.get('/a')
    new_time = rv.data.decode('utf-8')
    assert new_time != the_time

    forced_update = False
    time.sleep(1)
    rv = tc.get('/a')
    assert new_time == rv.data.decode('utf-8')


def test_generate_cache_key_from_different_view(app, cache):
    @app.route('/cake/<flavor>')
    @cache.cached()
    def view_cake(flavor):
        # What's the cache key for apple cake? thanks for making me hungry
        view_cake.cake_cache_key = view_cake.make_cache_key('apple')
        # print view_cake.cake_cache_key

        return str(time.time())
    view_cake.cake_cache_key = ''

    @app.route('/pie/<flavor>')
    @cache.cached()
    def view_pie(flavor):
        # What's the cache key for apple cake?
        view_pie.cake_cache_key = view_cake.make_cache_key('apple')
        # print view_pie.cake_cache_key

        return str(time.time())
    view_pie.cake_cache_key = ''

    tc = app.test_client()
    rv1 = tc.get('/cake/chocolate')
    rv2 = tc.get('/pie/chocolate')

    # print view_cake.cake_cache_key
    # print view_pie.cake_cache_key
    assert view_cake.cake_cache_key == view_pie.cake_cache_key


# rename/move to seperate module?
def test_cache_key_property(app, cache):
    @app.route('/')
    @cache.cached(5)
    def cached_view():
        return str(time.time())

    assert hasattr(cached_view, "make_cache_key")
    assert callable(cached_view.make_cache_key)

    tc = app.test_client()

    rv = tc.get('/')
    the_time = rv.data.decode('utf-8')

    with app.test_request_context():
        cache_data = cache.get(cached_view.make_cache_key())
        assert the_time == cache_data


def test_make_cache_key_function_property(app, cache):
    @app.route('/<foo>/<bar>')
    @cache.memoize(5)
    def cached_view(foo, bar):
        return str(time.time())

    assert hasattr(cached_view, "make_cache_key")
    assert callable(cached_view.make_cache_key)

    tc = app.test_client()

    rv = tc.get('/a/b')
    the_time = rv.data.decode('utf-8')

    cache_key = cached_view.make_cache_key(cached_view.uncached, foo=u"a", bar=u"b")
    cache_data = cache.get(cache_key)
    assert the_time == cache_data

    different_key = cached_view.make_cache_key(cached_view.uncached, foo=u"b", bar=u"a")
    different_data = cache.get(different_key)
    assert the_time != different_data


def test_cache_timeout_property(app, cache):
    @app.route('/')
    @cache.memoize(2)
    def cached_view1():
        return str(time.time())

    @app.route('/<foo>/<bar>')
    @cache.memoize(4)
    def cached_view2(foo, bar):
        return str(time.time())

    assert hasattr(cached_view1, "cache_timeout")
    assert hasattr(cached_view2, "cache_timeout")
    assert cached_view1.cache_timeout == 2
    assert cached_view2.cache_timeout == 4

    # test that this is a read-write property
    cached_view1.cache_timeout = 5
    cached_view2.cache_timeout = 7

    assert cached_view1.cache_timeout == 5
    assert cached_view2.cache_timeout == 7
    tc = app.test_client()

    rv1 = tc.get('/')
    time1 = rv1.data.decode('utf-8')
    time.sleep(1)
    rv2 = tc.get('/a/b')
    time2 = rv2.data.decode('utf-8')

    # VIEW1
    # it's been 1 second, cache is still active
    assert time1 == tc.get('/').data.decode('utf-8')
    time.sleep(5)
    # it's been >5 seconds, cache is not still active
    assert time1 != tc.get('/').data.decode('utf-8')

    # VIEW2
    # it's been >17 seconds, cache is still active
    #self.assertEqual(time2, tc.get('/a/b').data.decode('utf-8'))
    assert time2 == tc.get('/a/b').data.decode('utf-8')
    time.sleep(3)
    # it's been >7 seconds, cache is not still active
    assert time2 != tc.get('/a/b').data.decode('utf-8')


def test_generate_cache_key_from_query_string(app, cache):
    """Test the _make_cache_key_query_string() cache key maker.

    Create three requests to verify that the same query string
    parameters (key/value) always reference the same cache,
    regardless of the order of parameters.

    Also test to make sure that the same cache isn't being used for
    any/all query string parameters.

    For example, these two requests should yield the same
    cache/cache key:

      * GET /v1/works?mock=true&offset=20&limit=15
      * GET /v1/works?limit=15&mock=true&offset=20

    Caching functionality is verified by a `@cached` route `/works` which
    produces a time in its response. The time in the response can verify that
    two requests with the same query string parameters/values, though
    differently ordered, produce responses with the same time.
    """

    @app.route('/works')
    @cache.cached(query_string=True)
    def view_works():
        return str(time.time())

    tc = app.test_client()

    # Make our first query...
    first_response = tc.get(
        '/works?mock=true&offset=20&limit=15'
    )
    first_time = first_response.get_data(as_text=True)

    # Make the second query...
    second_response = tc.get(
        '/works?limit=15&mock=true&offset=20'
    )
    second_time = second_response.get_data(as_text=True)

    # Now make sure the time for the first and second
    # query are the same!
    assert second_time == first_time

    # Last/third query with different parameters/values should
    # produce a different time.
    third_response = tc.get(
        '/v1/works?limit=20&mock=true&offset=60'
    )
    third_time = third_response.get_data(as_text=True)

    # ... making sure that different query parameter values
    # don't yield the same cache!
    assert not third_time == second_time

def test_generate_cache_key_from_query_string_repeated_paramaters(app, cache):
    """Test the _make_cache_key_query_string() cache key maker's support for
    repeated query paramaters

    URL params can be repeated with different values. Flask's MultiDict
    supports them
    """

    @app.route('/works')
    @cache.cached(query_string=True)
    def view_works():
        flatted_values = sum(request.args.listvalues(), [])
        return str(sorted(flatted_values)) + str(time.time())

    tc = app.test_client()

    # Make our first query...
    first_response = tc.get(
        '/works?mock=true&offset=20&limit=15&user[]=123&user[]=124'
    )
    first_time = first_response.get_data(as_text=True)

    # Make the second query...
    second_response = tc.get(
        '/works?mock=true&offset=20&limit=15&user[]=124&user[]=123'
    )
    second_time = second_response.get_data(as_text=True)

    # Now make sure the time for the first and second
    # query are the same!
    assert second_time == first_time

    # Last/third query with different parameters/values should
    # produce a different time.
    third_response = tc.get(
        '/works?mock=true&offset=20&limit=15&user[]=125&user[]=124'
    )
    third_time = third_response.get_data(as_text=True)

    # ... making sure that different query parameter values
    # don't yield the same cache!
    assert not third_time == second_time


def test_generate_cache_key_from_request_body(app, cache):
    """Test the _make_cache_key_request_body() cache key maker.

    Create three requests to verify that the same request body
    always reference the same cache

    Also test to make sure that the same cache isn't being used for
    any/all query string parameters.

    Caching functionality is verified by a `@cached` route `/works` which
    produces a time in its response. The time in the response can verify that
    two requests with the same request body produce responses with the same time.
    """

    @app.route('/works', methods=['POST'])
    @cache.cached(request_body=True)
    def view_works():
        return str(time.time()) + request.get_data().decode()

    tc = app.test_client()

    # Make our request...
    first_response = tc.post(
        '/works', data=dict(mock=True, value=1, test=2)
    )
    first_time = first_response.get_data(as_text=True)

    # Make the request...
    second_response = tc.post(
        '/works', data=dict(mock=True, value=1, test=2)
    )
    second_time = second_response.get_data(as_text=True)

    # Now make sure the time for the first and second
    # requests are the same!
    assert second_time == first_time

    # Last/third request with different body should
    # produce a different time.
    third_response = tc.get(
        '/v1/works', data=dict(mock=True, value=2, test=3)
    )
    third_time = third_response.get_data(as_text=True)

    # ... making sure that different request bodies
    # don't yield the same cache!
    assert not third_time == second_time
