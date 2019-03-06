API
===

This section contains the API documentation of the Flask-Caching extension and
lists the backends which are supported out of the box.
The `Configuration <index.html#configuring-flask-caching>`_ section explains
how the backends can be used.


.. module:: flask_caching

Cache API
---------

.. autoclass:: Cache
   :members: init_app, get, set, add, delete, get_many, set_many, delete_many,
             clear, cached, memoize, delete_memoized, delete_memoized_verhash


Backends
--------

.. module:: flask_caching.backends

BaseCache
`````````

.. autoclass:: flask_caching.backends.base.BaseCache
   :members:

NullCache
`````````

.. autoclass:: NullCache
   :members:

SimpleCache
```````````

.. autoclass:: SimpleCache
   :members:

FileSystemCache
```````````````

.. autoclass:: FileSystemCache
   :members:

RedisCache
``````````

.. autoclass:: RedisCache
   :members:

RedisSentinelCache
``````````````````

.. autoclass:: RedisSentinelCache
   :members:

UWSGICache
``````````

.. autoclass:: UWSGICache
   :members:

MemcachedCache
``````````````

.. autoclass:: MemcachedCache
   :members:

SASLMemcachedCache
``````````````````

.. autoclass:: SASLMemcachedCache
   :members:

SpreadSASLMemcachedCache
````````````````````````

.. autoclass:: SpreadSASLMemcachedCache
   :members:
