import re

# -*- coding: utf-8 -*-
"""
    flask_caching.backends.memcache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The memcache caching backend.

    :copyright: (c) 2018 by Peter Justin.
    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details.
"""
from time import time

from flask_caching.backends.base import BaseCache, iteritems_wrapper

try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle  # type: ignore


_test_memcached_key = re.compile(r"[^\x00-\x21\xff]{1,250}$").match


class MemcachedCache(BaseCache):

    """A cache that uses memcached as backend.

    The first argument can either be an object that resembles the API of a
    :class:`memcache.Client` or a tuple/list of server addresses. In the
    event that a tuple/list is passed, Werkzeug tries to import the best
    available memcache library.

    This cache looks into the following packages/modules to find bindings for
    memcached:

        - ``pylibmc``
        - ``google.appengine.api.memcached``
        - ``memcached``
        - ``libmc``

    Implementation notes:  This cache backend works around some limitations in
    memcached to simplify the interface.  For example unicode keys are encoded
    to utf-8 on the fly.  Methods such as :meth:`~BaseCache.get_dict` return
    the keys in the same format as passed.  Furthermore all get methods
    silently ignore key errors to not cause problems when untrusted user data
    is passed to the get methods which is often the case in web applications.

    :param servers: a list or tuple of server addresses or alternatively
                    a :class:`memcache.Client` or a compatible client.
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`. A timeout of
                            0 indicates that the cache never expires.
    :param key_prefix: a prefix that is added before all keys.  This makes it
                       possible to use the same memcached server for different
                       applications.  Keep in mind that
                       :meth:`~BaseCache.clear` will also clear keys with a
                       different prefix.
    """

    def __init__(self, servers=None, default_timeout=300, key_prefix=None):
        super().__init__(default_timeout)
        if servers is None or isinstance(servers, (list, tuple)):
            if servers is None:
                servers = ["127.0.0.1:11211"]
            self._client = self.import_preferred_memcache_lib(servers)
            if self._client is None:
                raise RuntimeError("no memcache module found")
        else:
            # NOTE: servers is actually an already initialized memcache
            # client.
            self._client = servers

        self.key_prefix = key_prefix or None

    @classmethod
    def factory(cls, app, config, args, kwargs):
        args.append(config["CACHE_MEMCACHED_SERVERS"])
        kwargs.update(dict(key_prefix=config["CACHE_KEY_PREFIX"]))
        return cls(*args, **kwargs)

    def _normalize_key(self, key):
        key = str(key)
        if self.key_prefix:
            key = self.key_prefix + key
        return key

    def _normalize_timeout(self, timeout):
        timeout = BaseCache._normalize_timeout(self, timeout)
        if timeout > 0:
            # NOTE: pylibmc expect the timeout as delta time up to
            # 2592000 seconds (30 days)
            if not hasattr(self, "mc_library"):
                try:
                    import pylibmc  # noqa
                except ImportError:
                    self.mc_library = None
                else:
                    self.mc_library = "pylibmc"

            if self.mc_library != "pylibmc":
                timeout = int(time()) + timeout
            elif timeout > 2592000:
                timeout = 0

        return timeout

    def get(self, key):
        key = self._normalize_key(key)
        # memcached doesn't support keys longer than that.  Because often
        # checks for so long keys can occur because it's tested from user
        # submitted data etc we fail silently for getting.
        if _test_memcached_key(key):
            return self._client.get(key)

    def get_dict(self, *keys):
        key_mapping = {}
        have_encoded_keys = False
        for key in keys:
            encoded_key = self._normalize_key(key)
            if not isinstance(key, str):
                have_encoded_keys = True
            if _test_memcached_key(key):
                key_mapping[encoded_key] = key
        _keys = list(key_mapping)
        d = rv = self._client.get_multi(_keys)
        if have_encoded_keys or self.key_prefix:
            rv = {}
            for key, value in d.items():
                rv[key_mapping[key]] = value
        if len(rv) < len(keys):
            for key in keys:
                if key not in rv:
                    rv[key] = None
        return rv

    def add(self, key, value, timeout=None):
        key = self._normalize_key(key)
        timeout = self._normalize_timeout(timeout)
        return self._client.add(key, value, timeout)

    def set(self, key, value, timeout=None):
        key = self._normalize_key(key)
        timeout = self._normalize_timeout(timeout)
        return self._client.set(key, value, timeout)

    def get_many(self, *keys):
        d = self.get_dict(*keys)
        return [d[key] for key in keys]

    def set_many(self, mapping, timeout=None):
        new_mapping = {}
        for key, value in iteritems_wrapper(mapping):
            key = self._normalize_key(key)
            new_mapping[key] = value

        timeout = self._normalize_timeout(timeout)
        failed_keys = self._client.set_multi(new_mapping, timeout)
        return not failed_keys

    def delete(self, key):
        key = self._normalize_key(key)
        if _test_memcached_key(key):
            return self._client.delete(key)

    def delete_many(self, *keys):
        new_keys = []
        for key in keys:
            key = self._normalize_key(key)
            if _test_memcached_key(key):
                new_keys.append(key)
        return self._client.delete_multi(new_keys)

    def has(self, key):
        key = self._normalize_key(key)
        if _test_memcached_key(key):
            try:
                return self._client.append(key, "")
            except AttributeError:
                # GAEMemecache has no 'append' function
                return True if self._client.get(key) is not None else False
        return False

    def clear(self):
        return self._client.flush_all()

    def inc(self, key, delta=1):
        key = self._normalize_key(key)
        return self._client.incr(key, delta)

    def dec(self, key, delta=1):
        key = self._normalize_key(key)
        return self._client.decr(key, delta)

    def import_preferred_memcache_lib(self, servers):
        """Returns an initialized memcache client.  Used by the constructor."""
        try:
            import pylibmc
        except ImportError:
            pass
        else:
            self.mc_library = "pylibmc"
            return pylibmc.Client(servers)

        try:
            from google.appengine.api import memcache
        except ImportError:
            pass
        else:
            self.mc_library = "google.appengine.api"
            return memcache.Client()

        try:
            import memcache
        except ImportError:
            pass
        else:
            self.mc_library = "memcache"
            return memcache.Client(servers)

        try:
            import libmc
        except ImportError:
            pass
        else:
            self.mc_library = "libmc"
            return libmc.Client(servers)


class SASLMemcachedCache(MemcachedCache):
    def __init__(
        self,
        servers=None,
        default_timeout=300,
        key_prefix=None,
        username=None,
        password=None,
        **kwargs,
    ):
        super().__init__(default_timeout=default_timeout)

        if servers is None:
            servers = ["127.0.0.1:11211"]

        import pylibmc

        self._client = pylibmc.Client(
            servers, username=username, password=password, binary=True, **kwargs
        )

        self.key_prefix = key_prefix

    @classmethod
    def factory(cls, app, config, args, kwargs):
        args.append(config["CACHE_MEMCACHED_SERVERS"])
        kwargs.update(
            dict(
                username=config["CACHE_MEMCACHED_USERNAME"],
                password=config["CACHE_MEMCACHED_PASSWORD"],
                key_prefix=config["CACHE_KEY_PREFIX"],
            )
        )
        return cls(*args, **kwargs)


class SpreadSASLMemcachedCache(SASLMemcachedCache):
    """Simple Subclass of SASLMemcached client that will spread the value
    across multiple keys if they are bigger than a given threshold.

    Spreading requires using pickle to store the value, which can significantly
    impact the performance.
    """

    def __init__(self, *args, **kwargs):
        """
        Kwargs:
            chunksize (int): max length of a pickled object that can fit in
                memcached (memcache has an upper limit of 1MB for values,
                default: 1048448)
        """
        self.chunksize = kwargs.get("chunksize", 1048448)
        self.maxchunk = kwargs.get("maxchunk", 32)
        super().__init__(*args, **kwargs)

    @classmethod
    def factory(cls, app, config, args, kwargs):
        args.append(config["CACHE_MEMCACHED_SERVERS"])
        kwargs.update(
            dict(
                username=config.get("CACHE_MEMCACHED_USERNAME"),
                password=config.get("CACHE_MEMCACHED_PASSWORD"),
                key_prefix=config.get("CACHE_KEY_PREFIX"),
            )
        )

        return cls(*args, **kwargs)

    def delete(self, key):
        for skey in self._genkeys(key):
            super().delete(skey)

    def set(self, key, value, timeout=None, chunk=True):
        """Set a value in cache, potentially spreading it across multiple key.

        :param key: The cache key.
        :param value: The value to cache.
        :param timeout: The timeout after which the cache will be invalidated.
        :param chunk: If set to `False`, then spreading across multiple keys
                      is disabled. This can be faster, but it will fail if
                      the value is bigger than the chunks. It requires you
                      to get back the object by specifying that it is not
                      spread.
        """
        if chunk:
            return self._set(key, value, timeout=timeout)
        else:
            return super().set(key, value, timeout=timeout)

    def _set(self, key, value, timeout=None):
        # pickling/unpickling add an overhead,
        # I didn't found a good way to avoid pickling/unpickling if
        # key is smaller than chunksize, because in case or <werkzeug.requests>
        # getting the length consume the data iterator.
        serialized = pickle.dumps(value, 2)
        values = {}
        len_ser = len(serialized)
        chks = range(0, len_ser, self.chunksize)

        if len(chks) > self.maxchunk:
            raise ValueError("Cannot store value in less than %s keys" % self.maxchunk)

        for i in chks:
            values[f"{key}.{i // self.chunksize}"] = serialized[i : i + self.chunksize]

        super().set_many(values, timeout)

    def get(self, key, chunk=True):
        """Get a cached value.

        :param chunk: If set to ``False``, it will return a cached value
                      that is spread across multiple keys.
        """
        if chunk:
            return self._get(key)
        else:
            return super().get(key)

    def _genkeys(self, key):
        return [f"{key}.{i}" for i in range(self.maxchunk)]

    def _get(self, key):
        to_get = [f"{key}.{i}" for i in range(self.maxchunk)]
        result = super().get_many(*to_get)
        serialized = b"".join(v for v in result if v is not None)

        if not serialized:
            return None

        return pickle.loads(serialized)
