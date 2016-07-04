# -*- encoding: utf-8 -*-
from __future__ import with_statement

import sys
import os
import time
import random
import string

from flask import Flask, render_template, render_template_string
from flask_caching import Cache, function_namespace, make_template_fragment_key

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class CacheTestCase(unittest.TestCase):
    def _set_app_config(self, app):
        app.config['CACHE_TYPE'] = 'simple'

    def setUp(self):
        app = Flask(__name__, template_folder=os.path.dirname(__file__))
        app.debug = True
        self._set_app_config(app)
        self.cache = Cache(app)
        self.app = app

    def tearDown(self):
        self.app = None
        self.cache = None
        self.tc = None

    def test_00_set(self):
        self.cache.set('hi', 'hello')

        assert self.cache.get('hi') == 'hello'

    def test_01_add(self):
        self.cache.add('hi', 'hello')
        assert self.cache.get('hi') == 'hello'

        self.cache.add('hi', 'foobar')
        assert self.cache.get('hi') == 'hello'

    def test_02_delete(self):
        self.cache.set('hi', 'hello')
        self.cache.delete('hi')
        assert self.cache.get('hi') is None

    def test_03_cached_view(self):
        @self.app.route('/')
        @self.cache.cached(5)
        def cached_view():
            return str(time.time())

        tc = self.app.test_client()

        rv = tc.get('/')
        the_time = rv.data.decode('utf-8')

        time.sleep(2)

        rv = tc.get('/')

        assert the_time == rv.data.decode('utf-8')

        time.sleep(5)

        rv = tc.get('/')
        assert the_time != rv.data.decode('utf-8')

    def test_04_cached_view_unless(self):
        @self.app.route('/a')
        @self.cache.cached(5, unless=lambda: True)
        def non_cached_view():
            return str(time.time())

        @self.app.route('/b')
        @self.cache.cached(5, unless=lambda: False)
        def cached_view():
            return str(time.time())

        tc = self.app.test_client()

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

    def test_05_cached_function(self):
        with self.app.test_request_context():
            @self.cache.cached(2, key_prefix='MyBits')
            def get_random_bits():
                return [random.randrange(0, 2) for i in range(50)]

            my_list = get_random_bits()
            his_list = get_random_bits()

            assert my_list == his_list

            time.sleep(4)

            his_list = get_random_bits()

            assert my_list != his_list

    def test_06_memoize(self):
        with self.app.test_request_context():
            @self.cache.memoize(5)
            def big_foo(a, b):
                return a + b + random.randrange(0, 100000)

            result = big_foo(5, 2)

            time.sleep(1)

            assert big_foo(5, 2) == result

            result2 = big_foo(5, 3)
            assert result2 != result

            time.sleep(6)

            assert big_foo(5, 2) != result

            time.sleep(1)

            assert big_foo(5, 3) != result2

    def test_06a_memoize(self):
        self.app.config['CACHE_DEFAULT_TIMEOUT'] = 1
        self.cache = Cache(self.app)

        with self.app.test_request_context():
            @self.cache.memoize(50)
            def big_foo(a, b):
                return a + b + random.randrange(0, 100000)

            result = big_foo(5, 2)

            time.sleep(2)

            assert big_foo(5, 2) == result

    def test_06b_memoize_annotated(self):
        if sys.version_info >= (3, 0):
            with self.app.test_request_context():
                @self.cache.memoize(50)
                def big_foo_annotated(a, b):
                    return a + b + random.randrange(0, 100000)
                big_foo_annotated.__annotations__ = {'a': int, 'b': int, 'return': int}

                result = big_foo_annotated(5, 2)

                time.sleep(2)

                assert big_foo_annotated(5, 2) == result

    def test_06c_memoize_utf8_arguments(self):
        with self.app.test_request_context():
            @self.cache.memoize()
            def big_foo(a, b):
                return "{}-{}".format(a, b)

            big_foo("æøå", "chars")

    def test_06d_memoize_unicode_arguments(self):
        with self.app.test_request_context():
            @self.cache.memoize()
            def big_foo(a, b):
                return u"{}-{}".format(a, b)

            big_foo(u"æøå", "chars")

    def test_07_delete_memoize(self):
        with self.app.test_request_context():
            @self.cache.memoize(5)
            def big_foo(a, b):
                return a + b + random.randrange(0, 100000)

            result = big_foo(5, 2)
            result2 = big_foo(5, 3)

            time.sleep(1)

            assert big_foo(5, 2) == result
            assert big_foo(5, 2) == result
            assert big_foo(5, 3) != result
            assert big_foo(5, 3) == result2

            self.cache.delete_memoized(big_foo)

            assert big_foo(5, 2) != result
            assert big_foo(5, 3) != result2

    def test_07b_delete_memoized_verhash(self):
        with self.app.test_request_context():
            @self.cache.memoize(5)
            def big_foo(a, b):
                return a + b + random.randrange(0, 100000)

            result = big_foo(5, 2)
            result2 = big_foo(5, 3)

            time.sleep(1)

            assert big_foo(5, 2) == result
            assert big_foo(5, 2) == result
            assert big_foo(5, 3) != result
            assert big_foo(5, 3) == result2

            self.cache.delete_memoized_verhash(big_foo)

            _fname, _fname_instance = function_namespace(big_foo)
            version_key = self.cache._memvname(_fname)
            assert self.cache.get(version_key) is None

            assert big_foo(5, 2) != result
            assert big_foo(5, 3) != result2

            assert self.cache.get(version_key) is not None

    def test_07c_delete_memoized_annotated(self):
            with self.app.test_request_context():
                @self.cache.memoize(5)
                def big_foo_annotated(a, b):
                    return a + b + random.randrange(0, 100000)

                big_foo_annotated.__annotations__ = {'a': int, 'b': int, 'return': int}

                result = big_foo_annotated(5, 2)
                result2 = big_foo_annotated(5, 3)

                time.sleep(1)

                assert big_foo_annotated(5, 2) == result
                assert big_foo_annotated(5, 2) == result
                assert big_foo_annotated(5, 3) != result
                assert big_foo_annotated(5, 3) == result2

                self.cache.delete_memoized_verhash(big_foo_annotated)

                _fname, _fname_instance = function_namespace(big_foo_annotated)
                version_key = self.cache._memvname(_fname)
                assert self.cache.get(version_key) is None

                assert big_foo_annotated(5, 2) != result
                assert big_foo_annotated(5, 3) != result2

                assert self.cache.get(version_key) is not None

    def test_08_delete_memoize(self):
        with self.app.test_request_context():
            @self.cache.memoize()
            def big_foo(a, b):
                return a + b + random.randrange(0, 100000)

            result_a = big_foo(5, 1)
            result_b = big_foo(5, 2)

            assert big_foo(5, 1) == result_a
            assert big_foo(5, 2) == result_b
            self.cache.delete_memoized(big_foo, 5, 2)

            assert big_foo(5, 1) == result_a
            assert big_foo(5, 2) != result_b

            # Cleanup bigfoo 5,1 5,2 or it might conflict with
            # following run if it also uses memecache
            self.cache.delete_memoized(big_foo, 5, 2)
            self.cache.delete_memoized(big_foo, 5, 1)

    def test_09_args_memoize(self):
        with self.app.test_request_context():
            @self.cache.memoize()
            def big_foo(a, b):
                return sum(a) + sum(b) + random.randrange(0, 100000)

            result_a = big_foo([5, 3, 2], [1])
            result_b = big_foo([3, 3], [3, 1])

            assert big_foo([5, 3, 2], [1]) == result_a
            assert big_foo([3, 3], [3, 1]) == result_b

            self.cache.delete_memoized(big_foo, [5, 3, 2], [1])

            assert big_foo([5, 3, 2], [1]) != result_a
            assert big_foo([3, 3], [3, 1]) == result_b

            # Cleanup bigfoo 5,1 5,2 or it might conflict with
            # following run if it also uses memecache
            self.cache.delete_memoized(big_foo, [5, 3, 2], [1])
            self.cache.delete_memoized(big_foo, [3, 3], [1])

    def test_10_kwargs_memoize(self):
        with self.app.test_request_context():
            @self.cache.memoize()
            def big_foo(a, b=None):
                return a + sum(b.values()) + random.randrange(0, 100000)

            result_a = big_foo(1, dict(one=1, two=2))
            result_b = big_foo(5, dict(three=3, four=4))

            assert big_foo(1, dict(one=1, two=2)) == result_a
            assert big_foo(5, dict(three=3, four=4)) == result_b

            self.cache.delete_memoized(big_foo, 1, dict(one=1, two=2))

            assert big_foo(1, dict(one=1, two=2)) != result_a
            assert big_foo(5, dict(three=3, four=4)) == result_b

    def test_10a_kwargonly_memoize(self):
        with self.app.test_request_context():
            @self.cache.memoize()
            def big_foo(a=None):
                if a is None:
                    a = 0
                return a + random.random()

            result_a = big_foo()
            result_b = big_foo(5)

            assert big_foo() == result_a
            assert big_foo() < 1
            assert big_foo(5) == result_b
            assert big_foo(5) >= 5 and big_foo(5) < 6

    def test_10a_arg_kwarg_memoize(self):
        with self.app.test_request_context():
            @self.cache.memoize()
            def f(a, b, c=1):
                return a + b + c + random.randrange(0, 100000)

            assert f(1, 2) == f(1, 2, c=1)
            assert f(1, 2) == f(1, 2, 1)
            assert f(1, 2) == f(1, 2)
            assert f(1, 2, 3) != f(1, 2)
            with self.assertRaises(TypeError):
                f(1)

    def test_10b_classarg_memoize(self):
        @self.cache.memoize()
        def bar(a):
            return a.value + random.random()

        class Adder(object):
            def __init__(self, value):
                self.value = value

        adder = Adder(15)
        adder2 = Adder(20)

        y = bar(adder)
        z = bar(adder2)

        assert y != z
        assert bar(adder) == y
        assert bar(adder) != z
        adder.value = 14
        assert bar(adder) == y
        assert bar(adder) != z

        assert bar(adder) != bar(adder2)
        assert bar(adder2) == z

    def test_10c_classfunc_memoize(self):
        class Adder(object):
            def __init__(self, initial):
                self.initial = initial

            @self.cache.memoize()
            def add(self, b):
                return self.initial + b

        adder1 = Adder(1)
        adder2 = Adder(2)

        x = adder1.add(3)
        assert adder1.add(3) == x
        assert adder1.add(4) != x
        assert adder1.add(3) != adder2.add(3)

    def test_10d_classfunc_memoize_delete(self):
        with self.app.test_request_context():
            class Adder(object):
                def __init__(self, initial):
                    self.initial = initial

                @self.cache.memoize()
                def add(self, b):
                    return self.initial + b + random.random()

            adder1 = Adder(1)
            adder2 = Adder(2)

            a1 = adder1.add(3)
            a2 = adder2.add(3)

            assert a1 != a2
            assert adder1.add(3) == a1
            assert adder2.add(3) == a2

            self.cache.delete_memoized(adder1.add)

            a3 = adder1.add(3)
            a4 = adder2.add(3)

            self.assertNotEqual(a1, a3)
            assert a1 != a3
            self.assertEqual(a2, a4)

            self.cache.delete_memoized(Adder.add)

            a5 = adder1.add(3)
            a6 = adder2.add(3)

            self.assertNotEqual(a5, a6)
            self.assertNotEqual(a3, a5)
            self.assertNotEqual(a4, a6)

    def test_10e_delete_memoize_classmethod(self):
        with self.app.test_request_context():
            class Mock(object):
                @classmethod
                @self.cache.memoize(5)
                def big_foo(cls, a, b):
                    return a + b + random.randrange(0, 100000)

            result = Mock.big_foo(5, 2)
            result2 = Mock.big_foo(5, 3)

            time.sleep(1)

            assert Mock.big_foo(5, 2) == result
            assert Mock.big_foo(5, 2) == result
            assert Mock.big_foo(5, 3) != result
            assert Mock.big_foo(5, 3) == result2

            self.cache.delete_memoized(Mock.big_foo)

            assert Mock.big_foo(5, 2) != result
            assert Mock.big_foo(5, 3) != result2

    def test_11_cache_key_property(self):
        @self.app.route('/')
        @self.cache.cached(5)
        def cached_view():
            return str(time.time())

        assert hasattr(cached_view, "make_cache_key")
        assert callable(cached_view.make_cache_key)

        tc = self.app.test_client()

        rv = tc.get('/')
        the_time = rv.data.decode('utf-8')

        with self.app.test_request_context():
            cache_data = self.cache.get(cached_view.make_cache_key())
            assert the_time == cache_data

    def test_12_make_cache_key_function_property(self):
        @self.app.route('/<foo>/<bar>')
        @self.cache.memoize(5)
        def cached_view(foo, bar):
            return str(time.time())

        assert hasattr(cached_view, "make_cache_key")
        assert callable(cached_view.make_cache_key)

        tc = self.app.test_client()

        rv = tc.get('/a/b')
        the_time = rv.data.decode('utf-8')

        cache_key = cached_view.make_cache_key(cached_view.uncached, foo=u"a", bar=u"b")
        cache_data = self.cache.get(cache_key)
        assert the_time == cache_data

        different_key = cached_view.make_cache_key(cached_view.uncached, foo=u"b", bar=u"a")
        different_data = self.cache.get(different_key)
        assert the_time != different_data

    def test_13_cache_timeout_property(self):
        @self.app.route('/')
        @self.cache.memoize(5)
        def cached_view1():
            return str(time.time())

        @self.app.route('/<foo>/<bar>')
        @self.cache.memoize(10)
        def cached_view2(foo, bar):
            return str(time.time())

        assert hasattr(cached_view1, "cache_timeout")
        assert hasattr(cached_view2, "cache_timeout")
        assert cached_view1.cache_timeout == 5
        assert cached_view2.cache_timeout == 10

        # test that this is a read-write property
        cached_view1.cache_timeout = 15
        cached_view2.cache_timeout = 30

        assert cached_view1.cache_timeout == 15
        assert cached_view2.cache_timeout == 30

        tc = self.app.test_client()

        rv1 = tc.get('/')
        time1 = rv1.data.decode('utf-8')
        time.sleep(1)
        rv2 = tc.get('/a/b')
        time2 = rv2.data.decode('utf-8')

        # VIEW1
        # it's been 1 second, cache is still active
        assert time1 == tc.get('/').data.decode('utf-8')
        time.sleep(16)
        # it's been >15 seconds, cache is not still active
        assert time1 != tc.get('/').data.decode('utf-8')

        # VIEW2
        # it's been >17 seconds, cache is still active
        self.assertEqual(time2, tc.get('/a/b').data.decode('utf-8'))
        time.sleep(30)
        # it's been >30 seconds, cache is not still active
        assert time2 != tc.get('/a/b').data.decode('utf-8')

    def test_14_memoized_multiple_arg_kwarg_calls(self):
        with self.app.test_request_context():
            @self.cache.memoize()
            def big_foo(a, b, c=[1, 1], d=[1, 1]):
                return sum(a) + sum(b) + sum(c) + sum(d) + random.randrange(0, 100000)

            result_a = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])

            assert big_foo([5, 3, 2], [1], d=[3, 3], c=[3, 3]) == result_a
            assert big_foo(b=[1], a=[5, 3, 2], c=[3, 3], d=[3, 3]) == result_a
            assert big_foo([5, 3, 2], [1], [3, 3], [3, 3]) == result_a

    def test_15_memoize_multiple_arg_kwarg_delete(self):
        with self.app.test_request_context():
            @self.cache.memoize()
            def big_foo(a, b, c=[1, 1], d=[1, 1]):
                return sum(a) + sum(b) + sum(c) + sum(d) + random.randrange(0, 100000)

            result_a = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
            self.cache.delete_memoized(big_foo, [5, 3, 2], [1], [3, 3], [3, 3])
            result_b = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
            assert result_a != result_b

            self.cache.delete_memoized(big_foo, [5, 3, 2], b=[1], c=[3, 3], d=[3, 3])
            result_b = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
            assert result_a != result_b

            self.cache.delete_memoized(big_foo, [5, 3, 2], [1], c=[3, 3], d=[3, 3])
            result_a = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
            assert result_a != result_b

            self.cache.delete_memoized(big_foo, [5, 3, 2], b=[1], c=[3, 3], d=[3, 3])
            result_a = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
            assert result_a != result_b

            self.cache.delete_memoized(big_foo, [5, 3, 2], [1], c=[3, 3], d=[3, 3])
            result_b = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
            assert result_a != result_b

            self.cache.delete_memoized(big_foo, [5, 3, 2], [1], [3, 3], [3, 3])
            result_a = big_foo([5, 3, 2], [1], c=[3, 3], d=[3, 3])
            assert result_a != result_b

    def test_16_memoize_kwargs_to_args(self):
        with self.app.test_request_context():
            def big_foo(a, b, c=None, d=None):
                return sum(a) + sum(b) + random.randrange(0, 100000)

            expected = (1, 2, 'foo', 'bar')

            args, kwargs = self.cache._memoize_kwargs_to_args(big_foo, 1, 2, 'foo', 'bar')
            assert (args == expected)
            args, kwargs = self.cache._memoize_kwargs_to_args(big_foo, 2, 'foo', 'bar', a=1)
            assert (args == expected)
            args, kwargs = self.cache._memoize_kwargs_to_args(big_foo, a=1, b=2, c='foo', d='bar')
            assert (args == expected)
            args, kwargs = self.cache._memoize_kwargs_to_args(big_foo, d='bar', b=2, a=1, c='foo')
            assert (args == expected)
            args, kwargs = self.cache._memoize_kwargs_to_args(big_foo, 1, 2, d='bar', c='foo')
            assert (args == expected)

    def test_17_dict_config(self):
        cache = Cache(config={'CACHE_TYPE': 'simple'})
        cache.init_app(self.app)

        assert cache.config['CACHE_TYPE'] == 'simple'

    def test_18_dict_config_initapp(self):
        cache = Cache()
        cache.init_app(self.app, config={'CACHE_TYPE': 'simple'})
        from werkzeug.contrib.cache import SimpleCache
        assert isinstance(self.app.extensions['cache'][cache], SimpleCache)

    def test_19_dict_config_both(self):
        cache = Cache(config={'CACHE_TYPE': 'null'})
        cache.init_app(self.app, config={'CACHE_TYPE': 'simple'})
        from werkzeug.contrib.cache import SimpleCache
        assert isinstance(self.app.extensions['cache'][cache], SimpleCache)

    def test_20_jinja2ext_cache(self):
        somevar = ''.join([random.choice(string.ascii_letters) for x in range(6)])

        testkeys = [
            make_template_fragment_key("fragment1"),
            make_template_fragment_key("fragment1", vary_on=["key1"]),
            make_template_fragment_key("fragment1", vary_on=["key1", somevar]),
        ]
        delkey = make_template_fragment_key("fragment2")

        with self.app.test_request_context():
            #: Test if elements are cached
            render_template("test_template.html", somevar=somevar, timeout=60)
            for k in testkeys:
                assert self.cache.get(k) == somevar
            assert self.cache.get(delkey) == somevar

            #: Test timeout=del to delete key
            render_template("test_template.html", somevar=somevar, timeout="del")
            for k in testkeys:
                assert self.cache.get(k) == somevar
            assert self.cache.get(delkey) is None

            #: Test rendering templates from strings
            output = render_template_string(
                """{% cache 60, "fragment3" %}{{somevar}}{% endcache %}""",
                somevar=somevar
            )
            assert self.cache.get(make_template_fragment_key("fragment3")) == somevar
            assert output == somevar

            #: Test backwards compatibility
            output = render_template_string(
                """{% cache 30 %}{{somevar}}{% endcache %}""",
                somevar=somevar)
            assert self.cache.get(make_template_fragment_key("None1")) == somevar
            assert output == somevar

            output = render_template_string(
                """{% cache 30, "fragment4", "fragment5"%}{{somevar}}{% endcache %}""",
                somevar=somevar)
            k = make_template_fragment_key("fragment4", vary_on=["fragment5"])
            assert self.cache.get(k) == somevar
            assert output == somevar

    def test_21_init_app_sets_app_attribute(self):
        cache = Cache()
        cache.init_app(self.app)
        assert cache.app == self.app

    def test_22_cached_view_forced_update(self):
        forced_update = False

        def forced_update_fn():
            return forced_update

        @self.app.route('/a')
        @self.cache.cached(5, forced_update=lambda: forced_update)
        def view():
            return str(time.time())

        tc = self.app.test_client()

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

    def test_23_memoize_forced_update(self):
        with self.app.test_request_context():
            forced_update = False

            @self.cache.memoize(5, forced_update=lambda: forced_update)
            def big_foo(a, b):
                return a + b + random.randrange(0, 100000)

            result = big_foo(5, 2)
            time.sleep(1)
            assert big_foo(5, 2) == result

            forced_update = True
            new_result = big_foo(5, 2)
            assert new_result != result

            forced_update = False
            time.sleep(1)
            assert big_foo(5, 2) == new_result

    def test_24_generate_cache_key_from_different_view(self):
        @self.app.route('/cake/<flavor>')
        @self.cache.cached()
        def view_cake(flavor):
            # What's the cache key for apple cake? thanks for making me hungry
            view_cake.cake_cache_key = view_cake.make_cache_key('apple')
            # print view_cake.cake_cache_key

            return str(time.time())
        view_cake.cake_cache_key = ''

        @self.app.route('/pie/<flavor>')
        @self.cache.cached()
        def view_pie(flavor):
            # What's the cache key for apple cake?
            view_pie.cake_cache_key = view_cake.make_cache_key('apple')
            # print view_pie.cake_cache_key

            return str(time.time())
        view_pie.cake_cache_key = ''

        tc = self.app.test_client()
        rv1 = tc.get('/cake/chocolate')
        rv2 = tc.get('/pie/chocolate')

        # print view_cake.cake_cache_key
        # print view_pie.cake_cache_key
        assert view_cake.cake_cache_key == view_pie.cake_cache_key

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

if sys.version_info <= (2, 7):
    class CacheMemcachedTestCase(CacheTestCase):
        def _set_app_config(self, app):
            app.config['CACHE_TYPE'] = 'memcached'

    class SpreadCacheMemcachedTestCase(CacheTestCase):
        def _set_app_config(self, app):
            app.config['CACHE_TYPE'] = 'spreadsaslmemcachedcache'


class CacheRedisTestCase(CacheTestCase):
    def _set_app_config(self, app):
        app.config['CACHE_TYPE'] = 'redis'

    @unittest.skipUnless(HAS_REDIS, "requires Redis")
    def test_20_redis_url_default_db(self):
        config = {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': 'redis://localhost:6379',
        }
        cache = Cache()
        cache.init_app(self.app, config=config)
        from werkzeug.contrib.cache import RedisCache
        assert isinstance(self.app.extensions['cache'][cache], RedisCache)
        rconn = self.app.extensions['cache'][cache] \
                    ._client.connection_pool.get_connection('foo')
        assert rconn.db == 0

    @unittest.skipUnless(HAS_REDIS, "requires Redis")
    def test_21_redis_url_custom_db(self):
        config = {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': 'redis://localhost:6379/2',
        }
        cache = Cache()
        cache.init_app(self.app, config=config)
        rconn = self.app.extensions['cache'][cache] \
                    ._client.connection_pool.get_connection('foo')
        assert rconn.db == 2

    @unittest.skipUnless(HAS_REDIS, "requires Redis")
    def test_22_redis_url_explicit_db_arg(self):
        config = {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': 'redis://localhost:6379',
            'CACHE_REDIS_DB': 1,
        }
        cache = Cache()
        cache.init_app(self.app, config=config)
        rconn = self.app.extensions['cache'][cache] \
                    ._client.connection_pool.get_connection('foo')
        assert rconn.db == 1


class CacheFilesystemTestCase(CacheTestCase):
    def _set_app_config(self, app):
        app.config['CACHE_TYPE'] = 'filesystem'
        app.config['CACHE_DIR'] = '/tmp'


if __name__ == '__main__':
    unittest.main()
