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
