"""
flask_caching.backends
~~~~~~~~~~~~~~~~~~~~~~

Various caching backends.

:copyright: (c) 2018 by Peter Justin.
:copyright: (c) 2010 by Thadeus Burgess.
:license: BSD, see LICENSE for more details.
"""

from typing import Any

from flask import Flask

from flask_caching.backends.base import BaseCache
from flask_caching.backends.filesystemcache import FileSystemCache
from flask_caching.backends.memcache import MemcachedCache
from flask_caching.backends.memcache import SASLMemcachedCache
from flask_caching.backends.memcache import SpreadSASLMemcachedCache
from flask_caching.backends.nullcache import NullCache
from flask_caching.backends.rediscache import RedisCache
from flask_caching.backends.rediscache import RedisClusterCache
from flask_caching.backends.rediscache import RedisSentinelCache
from flask_caching.backends.simplecache import SimpleCache
from flask_caching.backends.uwsgicache import UWSGICache

__all__ = (
    "null",
    "simple",
    "filesystem",
    "redis",
    "redissentinel",
    "rediscluster",
    "uwsgi",
    "memcached",
    "gaememcached",
    "saslmemcached",
    "spreadsaslmemcached",
)


def null(
    app: Flask, config: dict[str, Any], args: list[Any], kwargs: dict[str, Any]
) -> BaseCache:
    return NullCache.factory(app, config, args, kwargs)


def simple(
    app: Flask, config: dict[str, Any], args: list[Any], kwargs: dict[str, Any]
) -> SimpleCache:
    return SimpleCache.factory(app, config, args, kwargs)


def filesystem(
    app: Flask, config: dict[str, Any], args: list[Any], kwargs: dict[str, Any]
) -> FileSystemCache:
    return FileSystemCache.factory(app, config, args, kwargs)


def redis(
    app: Flask, config: dict[str, Any], args: list[Any], kwargs: dict[str, Any]
) -> RedisCache:
    return RedisCache.factory(app, config, args, kwargs)


def redissentinel(
    app: Flask, config: dict[str, Any], args: list[Any], kwargs: dict[str, Any]
) -> RedisSentinelCache:
    return RedisSentinelCache.factory(app, config, args, kwargs)


def rediscluster(
    app: Flask, config: dict[str, Any], args: list[Any], kwargs: dict[str, Any]
) -> RedisClusterCache:
    return RedisClusterCache.factory(app, config, args, kwargs)


def uwsgi(
    app: Flask, config: dict[str, Any], args: list[Any], kwargs: dict[str, Any]
) -> BaseCache:
    return UWSGICache.factory(app, config, args, kwargs)


def memcached(
    app: Flask, config: dict[str, Any], args: list[Any], kwargs: dict[str, Any]
) -> MemcachedCache:
    return MemcachedCache.factory(app, config, args, kwargs)


def gaememcached(
    app: Flask, config: dict[str, Any], args: list[Any], kwargs: dict[str, Any]
) -> MemcachedCache:
    return memcached(app, config, args, kwargs)


def saslmemcached(
    app: Flask, config: dict[str, Any], args: list[Any], kwargs: dict[str, Any]
) -> SASLMemcachedCache:
    return SASLMemcachedCache.factory(app, config, args, kwargs)


def spreadsaslmemcached(
    app: Flask, config: dict[str, Any], args: list[Any], kwargs: dict[str, Any]
) -> SpreadSASLMemcachedCache:
    return SpreadSASLMemcachedCache.factory(app, config, args, kwargs)
