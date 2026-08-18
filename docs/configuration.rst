.. _configuring-flask-caching:

Configuration
-------------

The following configuration values exist for Flask-Caching:

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|


================================== ==================================================================
``CACHE_TYPE``                     Specifies which type of caching object to
                                   use. This is an import string that will
                                   be imported and instantiated. It is
                                   assumed that the import object is a
                                   function that will return a cache
                                   object that adheres to the cache API.

                                   For flask_caching.backends.cache objects, you
                                   do not need to specify the entire
                                   import string, just one of the following
                                   names.

                                   Built-in cache types:

                                   * :ref:`NullCache <nullcache>` (default)
                                   * :ref:`SimpleCache <simplecache>`
                                   * :ref:`FileSystemCache <filesystemcache>`
                                   * :ref:`RedisCache <rediscache>` (redis
                                     required)
                                   * :ref:`RedisSentinelCache
                                     <redissentinelcache>` (redis required)
                                   * :ref:`RedisClusterCache
                                     <redisclustercache>` (redis required)
                                   * :ref:`MemcachedCache <memcachedcache>`
                                     (pylibmc or memcache required)
                                   * :ref:`SASLMemcachedCache
                                     <saslmemcachedcache>` (pylibmc required)
                                   * :ref:`SpreadSASLMemcachedCache
                                     <spreadsaslmemcachedcache>` (pylibmc
                                     required)

                                   User contributed cache types:

                                   * :ref:`GoogleCloudStorageCache
                                     <googlecloudstoragecache>`
                                     (google-cloud-storage required)
                                   * :ref:`UWSGICache <uwsgicache>` (uwsgi
                                     required)

``CACHE_NO_NULL_WARNING``          Silence the warning message when using
                                   cache type of 'NullCache'.
``CACHE_ARGS``                     Optional list to unpack and pass during
                                   the cache class instantiation.
``CACHE_OPTIONS``                  Optional dictionary to pass during the
                                   cache class instantiation.
``CACHE_DEFAULT_TIMEOUT``          The timeout that is used if no other
                                   timeout is specified. Unit of time is
                                   seconds. Defaults to ``300``.
``CACHE_IGNORE_ERRORS``            If set to any errors that occurred during the
                                   deletion process will be ignored. However, if
                                   it is set to ``False`` it will stop on the
                                   first error. This option is only relevant for
                                   the backends **FileSystemCache** and
                                   **SimpleCache**. Defaults to ``False``.
``CACHE_THRESHOLD``                The maximum number of items the cache
                                   will store before it starts deleting
                                   some. Used only for SimpleCache and
                                   FileSystemCache. Defaults to ``500``.
``CACHE_KEY_PREFIX``               A prefix that is added before all keys.
                                   This makes it possible to use the same
                                   memcached server for different apps.
                                   Used only for RedisCache and MemcachedCache.
                                   Defaults to ``flask_cache_``.
``CACHE_SOURCE_CHECK``             The default condition applied to function
                                   decorators which controls if the source code of
                                   the function should be included when forming the
                                   hash which is used as the cache key. This
                                   ensures that if the source code changes, the
                                   cached value will not be returned when the new
                                   function is called even if the arguments are the
                                   same. Defaults to ``False``. See
                                   :ref:`source_check <source-check>`.
``CACHE_HASH_METHOD``              hash_method used for hashing cache keys. Defaults to
                                   ``hashlib.sha256``. Changing it invalidates all
                                   existing cache entries.
``CACHE_SERIALIZER``               The serializer the backend uses to serializer the values.
                                   If ``None`` or not set, it uses the default serializer from
                                   the backend. See :ref:`serializers` for more information.
``CACHE_ENABLE_SIGNALS``           Send Flask Signals for :meth:`~Cache.cached` and
                                   :meth:`~Cache.memoize` cache hits and misses.
``CACHE_UWSGI_NAME``               The name of the uwsgi caching instance to
                                   connect to, for example: mycache@localhost:3031,
                                   defaults to an empty string, which means uWSGI
                                   will cache in the local instance. If the cache
                                   is in the same instance as the werkzeug app,
                                   you only have to provide the name of the cache.
``CACHE_GCS_BUCKET``               The name of the Google Cloud Storage bucket to
                                   use. The bucket must already exist. Used only
                                   for :ref:`GoogleCloudStorageCache
                                   <googlecloudstoragecache>`.
``CACHE_MEMCACHED_SERVERS``        A list or a tuple of server addresses.
                                   Used only for MemcachedCache
``CACHE_MEMCACHED_USERNAME``       Username for SASL authentication with memcached.
                                   Used only for SASLMemcachedCache
``CACHE_MEMCACHED_PASSWORD``       Password for SASL authentication with memcached.
                                   Used only for SASLMemcachedCache
``CACHE_REDIS_HOST``               A Redis server host. Used only for RedisCache.
                                   May also be an already created Redis client, see
                                   :ref:`sharing-a-redis-client`.
                                   Ignored if ``CACHE_REDIS_URL`` is set.
``CACHE_REDIS_PORT``               A Redis server port. Default is 6379.
                                   Used only for RedisCache.
                                   Ignored if ``CACHE_REDIS_URL`` is set.
``CACHE_REDIS_PASSWORD``           A Redis password for server. Used only for RedisCache and
                                   RedisSentinelCache.
                                   Ignored if ``CACHE_REDIS_URL`` is set.
``CACHE_REDIS_DB``                 A Redis db (zero-based number index). Default is 0.
                                   Used only for RedisCache and RedisSentinelCache.
                                   Ignored if ``CACHE_REDIS_URL`` already contains a
                                   database, e.g. ``redis://localhost:6379/2``.
``CACHE_REDIS_SENTINELS``          A list or a tuple of Redis sentinel addresses. Used only for
                                   RedisSentinelCache.
``CACHE_REDIS_SENTINEL_MASTER``    The name of the master server in a sentinel configuration. Used
                                   only for RedisSentinelCache.
``CACHE_REDIS_SENTINEL_PASSWORD``
                                   A password for authenticating with the sentinel
                                   servers themselves, as opposed to
                                   ``CACHE_REDIS_PASSWORD`` which authenticates
                                   with the master. Used only for
                                   RedisSentinelCache.
``CACHE_REDIS_CLUSTER``            A string of comma-separated Redis cluster node addresses.
                                   e.g. host1:port1,host2:port2,host3:port3 . Used only for RedisClusterCache.
``CACHE_FILE_HASH_METHOD``         hash_method used for hashing the file names of cached
                                   entries. Defaults to ``hashlib.sha256``.
``CACHE_DIR``                      Directory to store cache. Used only for
                                   FileSystemCache.
``CACHE_REDIS_URL``                URL to connect to Redis server.
                                   Example ``redis://user:password@localhost:6379/2``. Supports
                                   protocols ``redis://``, ``rediss://`` (redis over TLS) and
                                   ``unix://``. See more info about URL support
                                   `here <http://redis-py.readthedocs.io/en/latest/index.html#redis.ConnectionPool.from_url>`_.
                                   Used only for RedisCache and RedisClusterCache. Takes
                                   precedence over the individual connection settings.
================================== ==================================================================


Flask-Caching will always use the `CACHE_<BACKEND>_URL` (if available) if a complete connection
URI is provided.

For example, ``CACHE_REDIS_URL`` and the individual connection settings are two alternative
ways of describing the same connection. They are not merged: if ``CACHE_REDIS_URL`` is set,
the connection is built from the URL alone and ``CACHE_REDIS_HOST``, ``CACHE_REDIS_PORT`` and
``CACHE_REDIS_PASSWORD`` are silently ignored. This is intended behaviour, not a bug.

For example, this configuration connects without a password, because the URL contains
a database (``/0``)::

    config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_URL": "redis://localhost:6379/0",
        "CACHE_REDIS_PASSWORD": "hunter2",  # ignored
    }

Put the credentials in the URL instead::

    config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_URL": "redis://:hunter2@localhost:6379/0",
    }

Or drop the URL and use the individual settings only::

    config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_HOST": "localhost",
        "CACHE_REDIS_PORT": 6379,
        "CACHE_REDIS_DB": 0,
        "CACHE_REDIS_PASSWORD": "hunter2",
    }


.. _sharing-a-redis-client:

Sharing a Redis client or connection pool
`````````````````````````````````````````

``CACHE_REDIS_HOST`` does not have to be a host name. If it is set to anything
other than a string, that object is used as the Redis client as-is. That makes
it possible to hand ``RedisCache`` a client that was created elsewhere, so a
single connection pool is shared with the rest of the application instead of
every extension opening a pool of its own::

    import redis
    from flask import Flask
    from flask_caching import Cache

    pool = redis.ConnectionPool(
        host="localhost", port=6379, db=0, max_connections=20
    )
    redis_client = redis.Redis(connection_pool=pool)

    app = Flask(__name__)
    app.config.from_mapping(
        {
            "CACHE_TYPE": "RedisCache",
            "CACHE_REDIS_HOST": redis_client,
            "CACHE_KEY_PREFIX": "myapp_",
        }
    )
    cache = Cache(app)

The same client, or the pool it was built from, can then be passed to other
extensions such as Flask-Limiter or Flask-Session and be used by the
application directly, instead of each of them connecting on its own.

Any object with a `redis-py`_ compatible API is accepted, not only
``redis.Redis`` instances. A client returned by
``redis.sentinel.Sentinel.master_for()`` works as well.

A few things to keep in mind when passing in a client:

- Do not set ``CACHE_REDIS_URL``. It takes precedence and builds a new client
  from the URL, which silently discards the one that was passed in.
- ``CACHE_REDIS_PORT``, ``CACHE_REDIS_DB``, ``CACHE_REDIS_PASSWORD`` and
  ``CACHE_OPTIONS`` are only used to build a client from a host name. They are
  ignored here; configure them on the client instead. ``CACHE_KEY_PREFIX`` and
  ``CACHE_DEFAULT_TIMEOUT`` still apply, they are handled by the cache itself.
- The client must not be created with ``decode_responses=True``. Cached values
  are pickled bytes and reading them back through a decoding client raises a
  ``TypeError``. That option is only rejected with an explicit error when
  Flask-Caching creates the client itself.
- Flask-Caching does not take ownership of the client. It never closes it or
  its connection pool, so its lifetime is up to the application.
- This applies to ``RedisCache`` only. ``RedisSentinelCache`` and
  ``RedisClusterCache`` always create their own clients from the configuration
  values.


Using a cachelib backend directly
`````````````````````````````````

The built-in backends subclass their `cachelib`_ counterparts, so ``CACHE_TYPE``
can also be an import string pointing straight at a cachelib class. This is the
way to use a backend that cachelib ships but Flask-Caching does not wrap, such
as ``MongoDbCache``, ``DynamoDbCache`` or ``ValkeyCache``.

For example, a MongoDbCache can look like this::

    config = {
        "CACHE_TYPE": "cachelib.MongoDbCache",
        "CACHE_ARGS": ["mongodb://localhost:27017"],
        "CACHE_OPTIONS": {"db": "myapp", "collection": "cache"},
    }

and a ValkeyCache config like this::

  config = {
      "CACHE_TYPE": "cachelib.valkey.ValkeyCache",
      "CACHE_OPTIONS": {
          "host": "localhost",
          "port": 6379,
          "db": 0,
          "key_prefix": "myapp",
      },
  }

The class is then instantiated directly: ``CACHE_ARGS`` is passed as positional
arguments and ``CACHE_OPTIONS`` as keyword arguments, together with
``CACHE_DEFAULT_TIMEOUT``. The other ``CACHE_*`` options (``CACHE_DIR``,
``CACHE_THRESHOLD``, ``CACHE_KEY_PREFIX``, the ``CACHE_REDIS_*`` settings, ...)
are only read by the built-in backends and are ignored here. Pass the
equivalent cachelib arguments through ``CACHE_OPTIONS`` instead.

.. _cachelib: https://github.com/pallets/cachelib
.. _redis-py: https://redis.readthedocs.io/
