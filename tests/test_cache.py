from unittest.case import TestCase
from flask import Flask

from flask.ext.caching import Cache


class TestCustomKeyGeneration(TestCase):
    def setUp(self):

        app = Flask(__name__)
        cache = Cache(app, config={'CACHE_TYPE': 'simple'})

        class Test:

            _value = 1

            @cache.memoize(10**6, exclude_params=["notUsedParam"])
            def method(self, param, notUsedParam):
                return notUsedParam

            @cache.memoize(10**6)
            def not_exclude_method(self, param1, param2):
                return self._value

        self.Test = Test
        self.cache = cache

    def testCaching(self):

        ins = self.Test()

        self.assertEqual("1", ins.method("1", "1"))
        self.assertEqual("1", ins.method("1", "2"))
        self.assertEqual("2", ins.method("2", "2"))
        self.assertEqual("2", ins.method("2", "3"))

        self.cache.delete_memoized(self.Test.method)

        self.assertEqual("2", ins.method("1", "2"))
        self.assertEqual("3", ins.method("2", "3"))

    def testNotExcludeParam(self):

        ins = self.Test()

        self.assertEqual(1, ins.not_exclude_method("1", "2"))
        ins._value = 2
        self.assertEqual(1, ins.not_exclude_method("1", "2"))
        self.assertEqual(2, ins.not_exclude_method("2", "2"))

        ins._value = 3
        self.assertEqual(2, ins.not_exclude_method("2", "2"))

        self.cache.delete_memoized(self.Test.not_exclude_method)
        self.assertEqual(3, ins.not_exclude_method("2", "2"))


class TestMemoizeProperty(TestCase):

    def setUp(self):

        app = Flask(__name__)
        cache = Cache(app, config={'CACHE_TYPE': 'simple'})

        class TestClass:

            def __init__(self, value):
                self._value = value

            @property
            @cache.memoize(100)
            def value(self):
                return self._value

        self.TestClass = TestClass
        self.cache = cache
        self.app = app

    def test_can_delete_memoized_property(self):

        with self.app.app_context():

            ins = self.TestClass(10)

            self.assertEqual(ins.value, 10)
            ins._value = 1
            self.assertEqual(ins.value, 10)

            #delete memoized
            self.cache.delete_memoized(self.TestClass.value)

            self.assertEqual(ins.value, 1)

            #update value
            ins._value = 2
            self.assertEqual(ins.value, 1)


