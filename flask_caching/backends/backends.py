# -*- coding: utf-8 -*-
"""
    flask_caching.backends
    ~~~~~~~~~~~~~~~~~~~~~~

    Various caching backends.

    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details.
"""
from werkzeug.contrib.cache import (NullCache, SimpleCache, MemcachedCache,
                                    GAEMemcachedCache, FileSystemCache,
                                    RedisCache, UWSGICache)
from .clients import SASLMemcachedCache, SpreadSASLMemcachedCache

__all__ = ('null', 'simple', 'filesystem', 'redis', 'uwsgi', 'memcached',
           'saslmemcached', 'gaememcached', 'spreadsaslmemcached')


def null(app, config, args, kwargs):
    return NullCache()


def simple(app, config, args, kwargs):
    kwargs.update(dict(threshold=config['CACHE_THRESHOLD']))
    return SimpleCache(*args, **kwargs)


def filesystem(app, config, args, kwargs):
    args.insert(0, config['CACHE_DIR'])
    kwargs.update(dict(threshold=config['CACHE_THRESHOLD']))
    return FileSystemCache(*args, **kwargs)


def redis(app, config, args, kwargs):
    try:
        from redis import from_url as redis_from_url
    except ImportError:
        raise RuntimeError('no redis module found')

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


def uwsgi(app, config, args, kwargs):
    # The name of the caching instance to connect to, for
    # example: mycache@localhost:3031, defaults to an empty string, which
    # means uWSGI will cache in the local instance. If the cache is in the
    # same instance as the werkzeug app, you only have to provide the name of
    # the cache.
    uwsgi_cache_name = config.get('CACHE_UWSGI_NAME', '')
    kwargs.update(dict(cache=uwsgi_cache_name))
    return UWSGICache(*args, **kwargs)


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


def spreadsaslmemcached(app, config, args, kwargs):
    args.append(config['CACHE_MEMCACHED_SERVERS'])
    kwargs.update(dict(username=config.get('CACHE_MEMCACHED_USERNAME'),
                       password=config.get('CACHE_MEMCACHED_PASSWORD'),
                       key_prefix=config.get('CACHE_KEY_PREFIX')))

    return SpreadSASLMemcachedCache(*args, **kwargs)
