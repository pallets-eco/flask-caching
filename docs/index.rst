Flask-Cache
================

.. module:: flaskext.cache

Installation
------------

Install the extension with one of the following commands::

    $ easy_install Flask-Cache

or alternatively if you have pip installed::

    $ pip install Flask-Cache


Configuring Flask-Cache
-----------------------

The following configuration values exist for Flask-SQLAlchemy:

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

=============================== =========================================
``CACHE_TYPE``                  Specifies which type of caching object to
                                use. This is one of
                                
                                * **Null**: Do not use cache.
                                * **Simple**: Uses SimpleCache
                                * **Memcached**: Uses MemcachedCache
                                * **GAE**: Uses GAEMemcachedCache
                                * **FileSystem**: Uses FileSysteCache
``CACHE_DEFAULT_TIMEOUT``       The default timeout that is used if no
                                timeout is specified.
``CACHE_THRESHOLD``             The maximum number of items the cache
                                will store before it starts deleting
                                some
``CACHE_KEY_PREFIX``            A prefix that is added before all keys.
                                This makes it possible to use the same
                                memcached server for different apps.
``CACHE_MEMCACHED_SERVERS``     A list or a tuple of server addresses.
``CACHE_DIR``     Specifies the connection timeout for the
                                pool.  Defaults to 10.
=============================== =========================================

In addition the standard Flask ``TESTING`` configuration option is used. If this
is True then **Flask-Cache** will use NullCache only.

Set Up
------

Cache is managed through a ``Cache`` instance::

    from flask import Flask
    from flaskext.cache import Cache
    
    app = Flask(__name__)
    cache = Cache(app)
    
You may also set up your ``Cache`` instance later at configuration time using
**init_app** method::

    cache = Cache()
    
    app = Flask(__name__)
    cache.init_app(app)
    
.. warning::

    If you are using an application factory, make sure your app is instantiated
    **BEFORE** you use the cache object in a view.
    
    Set up the app with your Cache object first **THEN** import your views.
    
    Otherwise Flask-Cache will have the un-intended side-effect of not being
    initalised properly and will use NullCache for your view functions.
    
Caching View Functions
----------------------

To cache view functions you will use the :meth:`~Cache.cached` decorator. 
This decorator will use request.path by default for the cache_key.::

    @cache.cached(timeout=50)
    def index():
        return render_template('index.html')
        
The cached decorator has another optional argument called ``unless``. This
argument accepts a callable that returns True or False. If ``unless`` returns
``True`` then it will bypass the caching mechanism entirely.
    
Caching Other Functions
-----------------------

Using the same ``@cached`` decorator you are able to cache the result of other 
non-view related functions. The only stipulation is that you replace the
``key_prefix``, otherwise it will use the request.path cache_key.::

    @cache.cached(timeout=50, key_prefix='all_comments')
    def get_all_comments():
        comments = do_serious_dbio()
        return list([x.author for x in comments])
        
    cached_comments = get_all_comments()

Memoization
-----------

See :meth:`~Cache.memoize`
    
API
---

.. autoclass:: Cache
   :members: get, set, add, delete, cached, memoize

.. include:: ../CHANGES
