# -*- coding: utf-8 -*-
"""
    flask_caching.backends
    ~~~~~~~~~~~~~~~~~~~~~~

    Various caching backends.

    :copyright: (c) 2018 by Peter Justin.
    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details.
"""
from typing import Callable

from flask_caching.backends.filesystemcache import FileSystemCache
from flask_caching.backends.memcache import (
    MemcachedCache,
    SASLMemcachedCache,
    SpreadSASLMemcachedCache,
)
from flask_caching.backends.nullcache import NullCache
# TODO: Rename to "redis" when python2 support is removed
from flask_caching.backends.rediscache import (
    RedisCache,
    RedisSentinelCache,
    RedisClusterCache,
)
from flask_caching.backends.simplecache import SimpleCache
from flask_caching.backends.uwsgicache import UWSGICache


class CacheFactory:
    _cache_loaders = {}

    @classmethod
    def register(cls, cache_function: Callable):
        cls._cache_loaders[cache_function.__name__] = cache_function

        def decorator(*args, **kwargs):
            return cache_function(*args, **kwargs)

        return decorator

    @classmethod
    def get(cls, cache_type: str):
        return cls._cache_loaders.get(cache_type)


@CacheFactory.register
def null(app, config, args, kwargs):
    return NullCache.factory(app, config, args, kwargs)


@CacheFactory.register
def simple(app, config, args, kwargs):
    return SimpleCache.factory(app, config, args, kwargs)


@CacheFactory.register
def filesystem(app, config, args, kwargs):
    return FileSystemCache.factory(app, config, args, kwargs)


@CacheFactory.register
def redis(app, config, args, kwargs):
    return RedisCache.factory(app, config, args, kwargs)


@CacheFactory.register
def redissentinel(app, config, args, kwargs):
    return RedisSentinelCache.factory(app, config, args, kwargs)


@CacheFactory.register
def rediscluster(app, config, args, kwargs):
    return RedisClusterCache.factory(app, config, args, kwargs)


@CacheFactory.register
def uwsgi(app, config, args, kwargs):
    return UWSGICache.factory(app, config, args, kwargs)


@CacheFactory.register
def memcached(app, config, args, kwargs):
    return MemcachedCache.factory(app, config, args, kwargs)


@CacheFactory.register
def gaememcached(app, config, args, kwargs):
    return memcached(app, config, args, kwargs)


@CacheFactory.register
def saslmemcached(app, config, args, kwargs):
    return SASLMemcachedCache.factory(app, config, args, kwargs)


@CacheFactory.register
def spreadsaslmemcached(app, config, args, kwargs):
    return SpreadSASLMemcachedCache.factory(app, config, args, kwargs)
