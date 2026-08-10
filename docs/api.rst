API
===

This section contains the API documentation of the Flask-Caching extension and
lists the backends which are supported out of the box via cachelib.
The :ref:`Configuration <configuring-flask-caching>` section explains
how the backends can be used.


.. module:: flask_caching


Cache API
---------

.. autoclass:: Cache
   :members: cache, init_app, get, set, add, delete, get_many, set_many,
             delete_many, get_dict, unlink, has, clear, cached, memoize,
             delete_memoized, delete_memoized_verhash


.. autoclass:: CachedResponse


.. autofunction:: make_template_fragment_key


Backends
--------

.. versionchanged::  1.11.0
   flask-caching now uses cachelib as backend. See `cachelib API`_ for further details.


.. _cachelib API: https://cachelib.readthedocs.io/en/stable/
