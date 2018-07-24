# -*- coding: utf-8 -*-
import hashlib
import os

import flask
import pytest

import flask_caching as fsc


"""
TODO: Tests missing

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
        from flask_caching.backends.cache import RedisCache
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
"""


@pytest.fixture
def app(request):
    app = flask.Flask(request.module.__name__,
                      template_folder=os.path.dirname(__file__))
    app.testing = True
    app.config["CACHE_TYPE"] = "simple"
    return app


@pytest.fixture
def cache(app):
    return fsc.Cache(app)

@pytest.fixture(params=[method for method in fsc.SUPPORTED_HASH_FUNCTIONS], ids=[method.__name__ for method in fsc.SUPPORTED_HASH_FUNCTIONS])
def hash_method(request):
    return request.param

