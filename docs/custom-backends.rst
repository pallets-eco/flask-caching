.. _custom-cache-backends:

Custom Cache Backends
---------------------

You are able to easily add your own custom cache backends by exposing a
function that can instantiate and return a cache object. ``CACHE_TYPE`` will be
the import string to your custom cache type. If not a subclass of
:class:`flask_caching.backends.cache.BaseCache`, Flask-Caching will call it
with three arguments:

* ``app``, the Flask application object the cache is being initialized for
* ``args``, the value of the CACHE_ARGS configuration option
* ``kwargs``, the value of the CACHE_OPTIONS configuration option

.. note:: ``args`` and ``kwargs`` are not expanded when instantiating the cache
   object, i.e. they are not passed in as ``*args`` and ``**kwargs``, but they
   are the exact value of the CACHE_ARGS and CACHE_OPTIONS configuration
   options (CACHE_ARGS, however, is converted to a list).

Your custom cache should, however, subclass the
:class:`flask_caching.backends.cache.BaseCache` class so it provides all the
necessary methods to be usable.

.. versionchanged:: 1.9.1 If your custom cache type *is* a subclass of
   :class:`flask_caching.backends.cache.BaseCache`, Flask-Caching will, instead
   of directly instantiating the class, call its ``factory`` class method with
   the same args as listed above.  Unless overridden, ``BaseCache.factory``
   simply instantiates the object without passing any arguments to it.
   Built-in cache classes have overridden this to mimic the old, function based
   cache isntantiation, so if you subclassed something that is not
   :class:`flask_caching.backends.cache.BaseCache`, you may want to consult the
   source code to see if your class is still compatible.

An example implementation::

    #: the_app/custom.py
    class RedisCache(BaseCache):
        def __init__(self, servers, default_timeout=500):
            pass

        @classmethod
        def factory(cls, app, args, kwargs):
            args.append(app.config['REDIS_SERVERS'])

            return cls(*args, **kwargs)

With this example, your ``CACHE_TYPE`` might be ``the_app.custom.RedisCache``

CACHE_TYPE doesn’t have to directly point to a cache class, though.  An example
PylibMC cache implementation to change binary setting and provide
username/password if SASL is enabled on the library::

    #: the_app/custom.py
    def pylibmccache(app, config, args, kwargs):
        return pylibmc.Client(servers=config['CACHE_MEMCACHED_SERVERS'],
                              username=config['CACHE_MEMCACHED_USERNAME'],
                              password=config['CACHE_MEMCACHED_PASSWORD'],
                              binary=True)

With this example, your ``CACHE_TYPE`` might be ``the_app.custom.pylibmccache``
