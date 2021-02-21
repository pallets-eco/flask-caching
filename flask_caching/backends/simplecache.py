# -*- coding: utf-8 -*-
"""
    flask_caching.backends.simple
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The simple cache backend.

    :copyright: (c) 2018 by Peter Justin.
    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details.
"""
import logging
from time import time

from flask_caching.backends.base import BaseCache

try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle  # type: ignore


logger = logging.getLogger(__name__)


class SimpleCache(BaseCache):
    """Simple memory cache for single process environments.  This class exists
    mainly for the development server and is not 100% thread safe.  It tries
    to use as many atomic operations as possible and no locks for simplicity
    but it could happen under heavy load that keys are added multiple times.

    :param threshold: the maximum number of items the cache stores before
                      it starts deleting some.
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`. A timeout of
                            0 indicates that the cache never expires.
    :param ignore_errors: If set to ``True`` the :meth:`~BaseCache.delete_many`
                          method will ignore any errors that occurred during
                          the deletion process. However, if it is set to
                          ``False`` it will stop on the first error. Defaults
                          to ``False``.
    """

    def __init__(self, threshold=500, default_timeout=300, ignore_errors=False):
        super(SimpleCache, self).__init__(default_timeout)
        self._cache = {}
        self.clear = self._cache.clear
        self._threshold = threshold
        self.ignore_errors = ignore_errors

    @classmethod
    def factory(cls, app, config, args, kwargs):
        kwargs.update(
            dict(
                threshold=config["CACHE_THRESHOLD"],
                ignore_errors=config["CACHE_IGNORE_ERRORS"],
            )
        )
        return cls(*args, **kwargs)

    def _prune(self):
        if len(self._cache) > self._threshold:
            now = time()
            toremove = []
            for idx, (key, (expires, _)) in enumerate(self._cache.items()):
                if (expires != 0 and expires <= now) or idx % 3 == 0:
                    toremove.append(key)
            for key in toremove:
                self._cache.pop(key, None)
            logger.debug("evicted %d key(s): %r", len(toremove), toremove)

    def _normalize_timeout(self, timeout):
        timeout = BaseCache._normalize_timeout(self, timeout)
        if timeout > 0:
            timeout = time() + timeout
        return timeout

    def get(self, key):
        result = None
        expired = False
        hit_or_miss = "miss"
        try:
            expires, value = self._cache[key]
        except KeyError:
            pass
        else:
            expired = expires != 0 and expires <= time()
            if not expired:
                hit_or_miss = "hit"
                try:
                    result = pickle.loads(value)
                except Exception as exc:
                    logger.error("get key %r -> %s", key, exc)
        expiredstr = "(expired)" if expired else ""
        logger.debug("get key %r -> %s %s", key, hit_or_miss, expiredstr)
        return result

    def set(self, key, value, timeout=None):
        expires = self._normalize_timeout(timeout)
        self._prune()
        item = (expires, pickle.dumps(value, pickle.HIGHEST_PROTOCOL))
        self._cache[key] = item
        logger.debug("set key %r", key)
        return True

    def add(self, key, value, timeout=None):
        expires = self._normalize_timeout(timeout)
        self._prune()
        item = (expires, pickle.dumps(value, pickle.HIGHEST_PROTOCOL))
        updated = False
        should_add = key not in self._cache
        if should_add:
            updated = self._cache.setdefault(key, item) != item
        updatedstr = "updated" if updated else "not updated"
        logger.debug("add key %r -> %s", key, updatedstr)
        return should_add

    def delete(self, key):
        deleted = self._cache.pop(key, None) is not None
        deletedstr = "deleted" if deleted else "not deleted"
        logger.debug("delete key %r -> %s", key, deletedstr)
        return deleted

    def has(self, key):
        result = False
        expired = False
        try:
            expires, value = self._cache[key]
        except KeyError:
            pass
        else:
            result = expires == 0 or expires > time()
            expired = not result
        expiredstr = "(expired)" if expired else ""
        logger.debug("has key %r -> %s %s", key, result, expiredstr)
        return result
