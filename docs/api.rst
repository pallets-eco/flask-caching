API
===

This section contains the API documentation of the Flask-Caching extension and
lists the backends which are supported out of the box via cachelib.
The :ref:`Configuration <configuring-flask-caching>` section explains
how the backends can be used.


.. currentmodule:: flask_caching


Cache API
---------
.. module:: flask_caching
.. autoclass:: Cache
   :members: cache, init_app, get, set, add, delete, get_many, set_many,
             delete_many, get_dict, unlink, has, clear, cached, memoize,
             delete_memoized, delete_memoized_verhash


.. autoclass:: CachedResponse


.. autofunction:: make_template_fragment_key


Signals
-------

The following signals are supported:

.. data:: cache_view_hit

   Sent when a view decorated with :meth:`~Cache.cached` is served from the
   cache. It is passed ``cache``, the :class:`Cache` instance, ``cache_key``,
   the key the response was found under, and ``args`` and ``kwargs``, the
   arguments the view was called with.

.. data:: cache_view_miss

   Sent when a view decorated with :meth:`~Cache.cached` is not found in the
   cache and has to be called. It is passed the same arguments as
   :data:`cache_view_hit`.

.. data:: cache_memoize_hit

   Sent when a function decorated with :meth:`~Cache.memoize` is served from
   the cache. In addition to the arguments passed to :data:`cache_view_hit`,
   it is passed ``f``, the undecorated function.

.. data:: cache_memoize_miss

   Sent when a function decorated with :meth:`~Cache.memoize` is not found in
   the cache and has to be called. It is passed the same arguments as
   :data:`cache_memoize_hit`.

By default, signals are disabled. To enable sending signals set
``CACHE_ENABLE_SIGNALS`` to ``True``.

See the `Flask documentation on signals`_ for information on how to use these
signals in your code.


.. _Flask documentation on signals: https://flask.palletsprojects.com/en/latest/signals/
