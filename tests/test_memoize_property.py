import unittest
from flask.app import Flask
from flask.ext.caching import Cache

__author__ = 'stas'

class TestMemoizeProperty(unittest.TestCase):

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


