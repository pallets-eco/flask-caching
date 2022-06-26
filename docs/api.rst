API
===

This section contains the API documentation of the Flask-Caching extension and
lists the backends which are supported out of the box via cachelib.
The `Configuration <index.html#configuring-flask-caching>`_ section explains
how the backends can be used.


.. module:: flask_caching


Cache API
---------

.. autoclass:: Cache
   :members: init_app, get, set, add, delete, get_many, set_many, delete_many,
             has, clear, cached, memoize, delete_memoized, delete_memoized_verhash


Backends
--------

.. versionchanged::  1.11.0
   flask-caching now uses cachelib as backend. See `cachelib API`_ for further details.


.. _cachelib API: https://cachelib.readthedocs.io/en/stable/
