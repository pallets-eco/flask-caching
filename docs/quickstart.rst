.. currentmodule:: flask_caching

Quickstart
==========

Cache is managed through a ``Cache`` instance::

    from flask import Flask
    from flask_caching import Cache

    config = {
        "DEBUG": True,                # some Flask specific configs
        "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
        "CACHE_DEFAULT_TIMEOUT": 300
    }
    app = Flask(__name__)
    # tell Flask to use the above defined config
    app.config.from_mapping(config)
    cache = Cache(app)

The configuration can also be passed straight to the ``Cache`` instance,
without going through ``app.config``::

    app = Flask(__name__)
    cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

You may also set up your ``Cache`` instance later at configuration time using
**init_app** method::

    cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

    app = Flask(__name__)
    cache.init_app(app)

You may also provide an alternate configuration dictionary, useful if there
will be multiple ``Cache`` instances each with a different backend::

    #: Method A: During instantiation of class
    cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
    #: Method B: During init_app call
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})

.. versionadded:: 0.7
   Multiple cache objects can be instantiated with different configuration
   values.

.. warning::

    ``CACHE_TYPE`` defaults to ``NullCache``, which does not cache anything.
    A warning is emitted if it is left unset. Set ``CACHE_NO_NULL_WARNING``
    to ``True`` to silence it. The available types/caching backends are listed under
    :ref:`CACHE_TYPE <configuring-flask-caching>`.


Caching a View
--------------

With the cache set up, the :meth:`~Cache.cached` decorator caches the return
value of a view::

    @app.route("/")
    @cache.cached(timeout=50)
    def index():
        return "This response is cached for 50 seconds"


Caching Data
------------

Values can also be stored and read back directly. The proxy methods need an
application context::

    with app.app_context():
        cache.set("answer", 42)
        cache.get("answer")  # 42


Next Steps
----------

* :doc:`usage` covers view functions, memoization and template fragments.
* :doc:`configuration` describes the configuration
* :doc:`backends` describes the built-in cache backends.
