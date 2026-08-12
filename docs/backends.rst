Built-in Cache Backends
-----------------------

.. _basecache:

BaseCache
`````````

.. currentmodule:: flask_caching.backends.base
.. py:class:: BaseCache
   :no-index-entry:

Baseclass for all the cache backends listed below. It isn't meant to be
used directly, but you can subclass it to implement your own
:ref:`custom cache backend <custom-cache-backends>`.


.. _nullcache:

NullCache
`````````

.. currentmodule:: flask_caching.backends.nullcache
.. py:class:: NullCache
   :no-index-entry:

Set ``CACHE_TYPE`` to ``NullCache`` to use this type.

Cache that doesn't cache

- CACHE_DEFAULT_TIMEOUT

.. versionchanged::  2.5.0
   Removed the deprecated old name in favour of just using the class name.


.. _simplecache:

SimpleCache
```````````

.. currentmodule:: flask_caching.backends.simplecache
.. py:class:: SimpleCache
   :no-index-entry:

Set ``CACHE_TYPE`` to ``SimpleCache`` to use this type.

Uses a local python dictionary for caching. All operations are protected by
a lock, making it thread-safe.

Relevant configuration values

- CACHE_DEFAULT_TIMEOUT
- CACHE_IGNORE_ERRORS
- CACHE_THRESHOLD

.. versionchanged::  2.5.0
   Removed the deprecated old name in favour of just using the class name.


.. _filesystemcache:

FileSystemCache
```````````````

.. currentmodule:: flask_caching.backends.filesystemcache
.. py:class:: FileSystemCache
   :no-index-entry:

Set ``CACHE_TYPE`` to ``FileSystemCache`` to use this type.

Uses the filesystem to store cached values

- CACHE_DEFAULT_TIMEOUT
- CACHE_IGNORE_ERRORS
- CACHE_DIR
- CACHE_THRESHOLD
- CACHE_OPTIONS

There is a single valid entry in CACHE_OPTIONS: *mode*, which should be a 3 digit
linux-style permissions octal mode.

.. versionchanged::  2.5.0
   Removed the deprecated old name in favour of just using the class name.


.. _rediscache:

RedisCache
``````````

.. currentmodule:: flask_caching.backends.rediscache
.. py:class:: RedisCache
   :no-index-entry:

Set ``CACHE_TYPE`` to ``RedisCache`` to use this type.

- CACHE_DEFAULT_TIMEOUT
- CACHE_KEY_PREFIX
- CACHE_OPTIONS
- CACHE_REDIS_HOST
- CACHE_REDIS_PORT
- CACHE_REDIS_PASSWORD
- CACHE_REDIS_DB
- CACHE_REDIS_URL

Entries in CACHE_OPTIONS are passed to the redis client as ``**kwargs``

.. versionchanged::  2.5.0
   Removed the deprecated old name in favour of just using the class name.


.. _redissentinelcache:

RedisSentinelCache
``````````````````

.. py:class:: RedisSentinelCache
   :no-index-entry:

Set ``CACHE_TYPE`` to ``RedisSentinel`` to use this type.

- CACHE_KEY_PREFIX
- CACHE_REDIS_SENTINELS
- CACHE_REDIS_SENTINEL_MASTER
- CACHE_REDIS_PASSWORD
- CACHE_REDIS_SENTINEL_PASSWORD
- CACHE_REDIS_DB

Entries in CACHE_OPTIONS are passed to the redis client as ``**kwargs``

.. versionchanged::  2.5.0
   Removed the deprecated old name in favour of just using the class name.


.. _redisclustercache:

RedisClusterCache
``````````````````

.. py:class:: RedisClusterCache
   :no-index-entry:

Set ``CACHE_TYPE`` to ``RedisClusterCache`` to use this type.

- CACHE_KEY_PREFIX
- CACHE_REDIS_CLUSTER
- CACHE_REDIS_PASSWORD
- CACHE_REDIS_URL

Entries in CACHE_OPTIONS are passed to the redis client as ``**kwargs``

.. versionchanged::  2.5.0
   Removed the deprecated old name in favour of just using the class name.


.. _memcachedcache:

MemcachedCache
``````````````

.. currentmodule:: flask_caching.backends.memcache
.. py:class:: MemcachedCache
   :no-index-entry:

Set ``CACHE_TYPE`` to ``MemcachedCache`` to use this type.

Uses a memcached server as a backend. Supports either pylibmc or memcache or
google app engine memcache library.

Relevant configuration values

- CACHE_DEFAULT_TIMEOUT
- CACHE_KEY_PREFIX
- CACHE_MEMCACHED_SERVERS


.. note:: Flask-Caching does not pass additional configuration options
   to memcached backends. To add additional configuration to these caches,
   directly set the configuration options on the object after instantiation::

       from flask_caching import Cache
       cache = Cache()

       # Can't configure the client yet...
       cache.init_app(flask_app, {"CACHE_TYPE": "MemcachedCache"})

       # Break convention and set options on the _client object
       # directly. For pylibmc behaviors:
       cache.cache._client.behaviors({"tcp_nodelay": True})

   Alternatively, see :ref:`Custom Cache Backends <custom-cache-backends>`.

.. versionchanged::  2.5.0
   Removed the deprecated old name in favour of just using the class name.


.. _saslmemcachedcache:

SASLMemcachedCache
``````````````````

.. py:class:: SASLMemcachedCache
   :no-index-entry:

Set ``CACHE_TYPE`` to ``SASLMemcachedCache`` to use this type.

Uses a memcached server as a backend. Intended to be used with a SASL enabled
connection to the memcached server. pylibmc is required and SASL must be supported
by libmemcached.

Relevant configuration values

- CACHE_DEFAULT_TIMEOUT
- CACHE_KEY_PREFIX
- CACHE_OPTIONS
- CACHE_MEMCACHED_SERVERS
- CACHE_MEMCACHED_USERNAME
- CACHE_MEMCACHED_PASSWORD

.. note:: Unlike MemcachedCache, SASLMemcachedCache can be configured with
          CACHE_OPTIONS.

.. versionadded:: 0.10

.. versionchanged::  2.5.0
   Removed the deprecated old name in favour of just using the class name.


.. _spreadsaslmemcachedcache:

SpreadSASLMemcachedCache
````````````````````````

.. py:class:: SpreadSASLMemcachedCache
   :no-index-entry:

Set ``CACHE_TYPE`` to ``SpreadSASLMemcachedCache`` to use this type.

Same as SASLMemcachedCache however, it has the ability to spread value across
multiple keys if it is bigger than the memcached threshold which by
default is 1M. Uses pickle.

.. versionadded:: 0.11

.. versionchanged::  1.1.0
    Renamed ``spreadsaslmemcachedcache`` to ``spreadsaslmemcached`` for
    the sake of consistency.

.. versionchanged::  2.5.0
   Removed the deprecated old name in favour of just using the class name.
