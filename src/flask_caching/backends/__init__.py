"""
flask_caching.backends
~~~~~~~~~~~~~~~~~~~~~~

Various caching backends.

:copyright: (c) 2018 by Peter Justin.
:copyright: (c) 2010 by Thadeus Burgess.
:license: BSD, see LICENSE for more details.
"""

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
    "BaseCache",
    "NullCache",
    "SimpleCache",
    "FileSystemCache",
    "RedisCache",
    "RedisSentinelCache",
    "RedisClusterCache",
    "UWSGICache",
    "MemcachedCache",
    "SASLMemcachedCache",
    "SpreadSASLMemcachedCache",
)
