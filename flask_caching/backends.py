# -*- coding: utf-8 -*-
"""
    flask_caching.backends
    ~~~~~~~~~~~~~~~~~~~~~~

    Various caching backends.

    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details.
"""
import pickle
from werkzeug.contrib.cache import (BaseCache, NullCache, SimpleCache,
                                    MemcachedCache, GAEMemcachedCache,
                                    FileSystemCache)
from ._compat import range_type


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


def null(app, config, args, kwargs):
    return NullCache()


def simple(app, config, args, kwargs):
    kwargs.update(dict(threshold=config['CACHE_THRESHOLD']))
    return SimpleCache(*args, **kwargs)


def memcached(app, config, args, kwargs):
    args.append(config['CACHE_MEMCACHED_SERVERS'])
    kwargs.update(dict(key_prefix=config['CACHE_KEY_PREFIX']))
    return MemcachedCache(*args, **kwargs)


def saslmemcached(app, config, args, kwargs):
    args.append(config['CACHE_MEMCACHED_SERVERS'])
    kwargs.update(dict(username=config['CACHE_MEMCACHED_USERNAME'],
                       password=config['CACHE_MEMCACHED_PASSWORD'],
                       key_prefix=config['CACHE_KEY_PREFIX']))
    return SASLMemcachedCache(*args, **kwargs)


def gaememcached(app, config, args, kwargs):
    kwargs.update(dict(key_prefix=config['CACHE_KEY_PREFIX']))
    return GAEMemcachedCache(*args, **kwargs)


def filesystem(app, config, args, kwargs):
    args.insert(0, config['CACHE_DIR'])
    kwargs.update(dict(threshold=config['CACHE_THRESHOLD']))
    return FileSystemCache(*args, **kwargs)

# RedisCache is supported since Werkzeug 0.7.
try:
    from werkzeug.contrib.cache import RedisCache
    from redis import from_url as redis_from_url
except ImportError:
    pass
else:
    def redis(app, config, args, kwargs):
        kwargs.update(dict(
            host=config.get('CACHE_REDIS_HOST', 'localhost'),
            port=config.get('CACHE_REDIS_PORT', 6379),
        ))
        password = config.get('CACHE_REDIS_PASSWORD')
        if password:
            kwargs['password'] = password

        key_prefix = config.get('CACHE_KEY_PREFIX')
        if key_prefix:
            kwargs['key_prefix'] = key_prefix

        db_number = config.get('CACHE_REDIS_DB')
        if db_number:
            kwargs['db'] = db_number

        redis_url = config.get('CACHE_REDIS_URL')
        if redis_url:
            kwargs['host'] = redis_from_url(
                redis_url,
                db=kwargs.pop('db', None),
            )

        return RedisCache(*args, **kwargs)


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


def spreadsaslmemcachedcache(app, config, args, kwargs):
    args.append(config['CACHE_MEMCACHED_SERVERS'])
    kwargs.update(dict(username=config.get('CACHE_MEMCACHED_USERNAME'),
                       password=config.get('CACHE_MEMCACHED_PASSWORD'),
                       key_prefix=config.get('CACHE_KEY_PREFIX')))

    return SpreadSASLMemcachedCache(*args, **kwargs)
