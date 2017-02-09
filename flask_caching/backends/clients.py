# -*- coding: utf-8 -*-
"""
    flask_caching.clients
    ~~~~~~~~~~~~~~~~~~~~~

    This module holds various caching backend clients for
    which werkzeug doesn't provide a class.

    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details.
"""
import pickle
from werkzeug.contrib.cache import BaseCache, MemcachedCache

from flask_caching._compat import range_type


class SASLMemcachedCache(MemcachedCache):
    def __init__(self, servers=None, default_timeout=300, key_prefix=None,
                 username=None, password=None):
        BaseCache.__init__(self, default_timeout)

        if servers is None:
            servers = ['127.0.0.1:11211']

        import pylibmc
        self._client = pylibmc.Client(servers,
                                      username=username,
                                      password=password,
                                      binary=True)

        self.key_prefix = key_prefix


class SpreadSASLMemcachedCache(SASLMemcachedCache):
    """Simple Subclass of SASLMemcached client that will spread the value
    across multiple keys if they are bigger than a given treshhold.

    Spreading requires using pickle to store the value, which can significantly
    impact the performance.
    """

    def __init__(self, *args, **kwargs):
        """
        chunksize : (int) max size in bytes of chunk stored in memcached
        """
        self.chunksize = kwargs.get('chunksize', 950000)
        self.maxchunk = kwargs.get('maxchunk', 32)
        super(SpreadSASLMemcachedCache, self).__init__(*args, **kwargs)

    def delete(self, key):
        for skey in self._genkeys(key):
            super(SpreadSASLMemcachedCache, self).delete(skey)

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
            return super(SpreadSASLMemcachedCache, self).set(key, value,
                                                             timeout=timeout)

    def _set(self, key, value, timeout=None):
        # pickling/unpickling add an overhead,
        # I didn't found a good way to avoid pickling/unpickling if
        # key is smaller than chunksize, because in case or <werkzeug.requests>
        # getting the length consume the data iterator.
        serialized = pickle.dumps(value, 2)
        values = {}
        len_ser = len(serialized)
        chks = range_type(0, len_ser, self.chunksize)

        if len(chks) > self.maxchunk:
            raise ValueError(
                'Cannot store value in less than %s keys' % self.maxchunk
            )

        for i in chks:
            values['%s.%s' % (key, i // self.chunksize)] = \
                serialized[i:i + self.chunksize]

        super(SpreadSASLMemcachedCache, self).set_many(values, timeout)

    def get(self, key, chunk=True):
        """Get a cached value.

        :param chunk: If set to ``False``, it will return a cached value
                      that is spread across multiple keys.
        """
        if chunk:
            return self._get(key)
        else:
            return super(SpreadSASLMemcachedCache, self).get(key)

    def _genkeys(self, key):
        return ['%s.%s' % (key, i) for i in range_type(self.maxchunk)]

    def _get(self, key):
        to_get = ['%s.%s' % (key, i) for i in range_type(self.maxchunk)]
        result = super(SpreadSASLMemcachedCache, self).get_many(*to_get)
        serialized = ''.join([v for v in result if v is not None])
        if not serialized:
            return None
        return pickle.loads(serialized)
