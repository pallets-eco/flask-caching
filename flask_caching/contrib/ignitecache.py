# -*- coding: utf-8 -*-
"""
    flask_caching.contrib.ignite
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The Apache Ignite caching backend.

    :copyright: (c) 2021 by Stephen Darlington, GridGain System.
    :license: BSD, see LICENSE for more details.
"""
import platform

from flask_caching.backends.base import BaseCache

try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle  # type: ignore

try:
    from pyignite import Client
except ImportError:
    raise RuntimeError("no pyignite module found")


class IgniteCache(BaseCache):
    """Implements the cache using Apache Ignite.

    :param default_timeout: The default timeout in seconds.
    :param cache: The name of the caching to create or connect to, defaults to FLASK_CACHE
    :param hosts: host and port to connect to, defaults to localhost:10800
    """

    def __init__(self, default_timeout=300, cache="FLASK_CACHE", hosts="localhost:10800"):
        super(IgniteCache, self).__init__(default_timeout)

        self.client = Client()
        host_components = hosts.split(':')
        self.client.connect(host_components[0], int(host_components[1]))
        self.cache = self.client.get_or_create_cache(cache)

    @classmethod
    def factory(cls, app, config, args, kwargs):
        ignite_hosts = config.get("IGNITE_HOSTS","localhost:10800")
        ignite_cache_name = config.get("CACHE_IGNITE_NAME", "FLASK_CACHE")
        kwargs.update(dict(cache=ignite_cache_name, hosts=ignite_hosts))
        return cls(*args, **kwargs)

    def get(self, key):
        rv = self.cache.get(key)
        if rv is None:
            return
        return pickle.loads(rv)

    def delete(self, key):
        return self.cache.remove_key(key)

    def set(self, key, value, timeout=None):
        if timeout is None:
          cache = self.cache
        else:
          cache = self.cache.with_expire_policy(access=timeout)
        cache.put(
            key,
            pickle.dumps(value),
        )

    def add(self, key, value, timeout=None):
        if timeout is None:
          cache = self.cache
        else:
          cache = self.cache.with_expire_policy(access=timeout)
        cache.put(
            key,
            pickle.dumps(value),
        )

    def clear(self):
        return self.cache.remove_all()

    def has(self, key):
        return self.cache.contains_key(key)
