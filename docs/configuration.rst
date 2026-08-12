.. _configuring-flask-caching:

Configuring Flask-Caching
-------------------------

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
