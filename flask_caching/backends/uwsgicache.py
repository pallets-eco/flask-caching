# -*- coding: utf-8 -*-
"""
    flask_caching.backends.uwsgicache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The uWSGI caching backend.

    :copyright: (c) 2018 by Peter Justin.
    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details.
"""
import platform

from flask_caching.backends.base import BaseCache

try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle  # type: ignore


class UWSGICache(BaseCache):
    """Implements the cache using uWSGI's caching framework.

    .. note::
        This class cannot be used when running under PyPy, because the uWSGI
        API implementation for PyPy is lacking the needed functionality.

    :param default_timeout: The default timeout in seconds.
    :param cache: The name of the caching instance to connect to, for
        example: mycache@localhost:3031, defaults to an empty string, which
        means uWSGI will use the first cache instance initialized.
        If the cache is in the same instance as the werkzeug app,
        you only have to provide the name of the cache.
    """

    def __init__(self, default_timeout=300, cache=""):
        super(UWSGICache, self).__init__(default_timeout)

        if platform.python_implementation() == "PyPy":
            raise RuntimeError(
                "uWSGI caching does not work under PyPy, see "
                "the docs for more details."
            )

        try:
            import uwsgi

            self._uwsgi = uwsgi
        except ImportError:
            raise RuntimeError(
                "uWSGI could not be imported, are you running under uWSGI?"
            )

        if "cache2" not in uwsgi.opt:
            raise RuntimeError(
                "You must enable cache2 in uWSGI configuration: "
                "https://uwsgi-docs.readthedocs.io/en/latest/Caching.html"
            )

        self.cache = cache

    @classmethod
    def factory(cls, app, config, args, kwargs):
        # The name of the caching instance to connect to, for
        # example: mycache@localhost:3031, defaults to an empty string, which
        # means uWSGI will cache in the local instance. If the cache is in the
        # same instance as the werkzeug app, you only have to provide the name
        # of the cache.
        uwsgi_cache_name = config.get("CACHE_UWSGI_NAME", "")
        kwargs.update(dict(cache=uwsgi_cache_name))
        return cls(*args, **kwargs)

    def get(self, key):
        rv = self._uwsgi.cache_get(key, self.cache)
        if rv is None:
            return
        return pickle.loads(rv)

    def delete(self, key):
        return self._uwsgi.cache_del(key, self.cache)

    def set(self, key, value, timeout=None):
        return self._uwsgi.cache_update(
            key,
            pickle.dumps(value),
            self._normalize_timeout(timeout),
            self.cache,
        )

    def add(self, key, value, timeout=None):
        return self._uwsgi.cache_set(
            key,
            pickle.dumps(value),
            self._normalize_timeout(timeout),
            self.cache,
        )

    def clear(self):
        return self._uwsgi.cache_clear(self.cache)

    def has(self, key):
        return self._uwsgi.cache_exists(key, self.cache) is not None
