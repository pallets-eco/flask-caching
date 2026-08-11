Flask-Caching
=============

.. module:: flask_caching
   :noindex:

Flask-Caching is an extension to `Flask`_ that adds caching support for
various backends to any Flask application. By running on top of `cachelib`_
it supports all of `werkzeug`_'s original caching backends through a uniformed
API. It is also possible to develop your own caching backend by subclassing
:class:`flask_caching.backends.base.BaseCache` class.

.. code-block:: python

    from flask import Flask
    from flask_caching import Cache

    app = Flask(__name__)
    cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})

    @app.route("/")
    @cache.cached(timeout=50)
    def index():
        return "This response is cached for 50 seconds"


Installation
------------

Install the extension with the following command::

    $ pip install Flask-Caching

or alternatively with uv::

    $ uv add Flask-Caching

Flask-Caching 2.5.0 supports Python 3.11+.


Content
-------

.. toctree::
   :maxdepth: 2

   quickstart
   usage
   configuration
   backends
   contrib-backends
   serializers
   custom-backends


API
---

.. toctree::
   :maxdepth: 2

   api


Additional Information
----------------------

.. toctree::
   :maxdepth: 2

   changelog
   license

* :ref:`search`


.. _Flask: http://flask.pocoo.org/
.. _werkzeug: http://werkzeug.pocoo.org/
.. _cachelib: https://github.com/pallets/cachelib
