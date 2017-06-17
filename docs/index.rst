Flask-Caching
=============

.. module:: flask_caching

Flask-Caching is an extension to `Flask`_ that adds caching support for
various backends to any Flask application. Besides providing support for all
of `werkzeug`_'s supported caching backends through a uniformed API,
it is also possible to develop your own caching backend by subclassing
:class:`werkzeug.contrib.cache.BaseCache` class.


Installation
------------

Install the extension with one of the following commands::

    $ easy_install Flask-Caching

or alternatively if you have pip installed::

    $ pip install Flask-Caching


Set Up
------

Cache is managed through a ``Cache`` instance::

    from flask import Flask
    from flask_caching import Cache

    app = Flask(__name__)
    # Check Configuring Flask-Caching section for more details
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

You may also set up your ``Cache`` instance later at configuration time using
**init_app** method::

    cache = Cache(config={'CACHE_TYPE': 'simple'})

    app = Flask(__name__)
    cache.init_app(app)

You may also provide an alternate configuration dictionary, useful if there will
be multiple ``Cache`` instances each with a different backend.::

    #: Method A: During instantiation of class
    cache = Cache(config={'CACHE_TYPE': 'simple'})
    #: Method B: During init_app call
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})

.. versionadded:: 0.7


Caching View Functions
----------------------

To cache view functions you will use the :meth:`~Cache.cached` decorator.
This decorator will use request.path by default for the cache_key.::

    @app.route("/")
    @cache.cached(timeout=50)
    def index():
        return render_template('index.html')

The cached decorator has another optional argument called ``unless``. This
argument accepts a callable that returns True or False. If ``unless`` returns
``True`` then it will bypass the caching mechanism entirely.

.. warning::

    When using ``cached`` on a view, take care to put it between Flask's
    ``@route`` decorator and your function definition. Example::

        @app.route('/')
        @cache.cached(timeout=50)
        def index():
            return 'Cached for 50s'

    If you reverse both decorator, what will be cached is the result of
    ``@route`` decorator, and not the result of your view function.


Caching Other Functions
-----------------------

Using the same ``@cached`` decorator you are able to cache the result of other
non-view related functions. The only stipulation is that you replace the
``key_prefix``, otherwise it will use the request.path cache_key.::

    @cache.cached(timeout=50, key_prefix='all_comments')
    def get_all_comments():
        comments = do_serious_dbio()
        return [x.author for x in comments]

    cached_comments = get_all_comments()


Memoization
-----------

See :meth:`~Cache.memoize`

In memoization, the functions arguments are also included into the cache_key.

.. note::

    With functions that do not receive arguments, :meth:`~Cache.cached` and
    :meth:`~Cache.memoize` are effectively the same.

Memoize is also designed for methods, since it will take into account
the `identity <http://docs.python.org/library/functions.html#id>`_. of the
'self' or 'cls' argument as part of the cache key.

The theory behind memoization is that if you have a function you need
to call several times in one request, it would only be calculated the first
time that function is called with those arguments. For example, an sqlalchemy
object that determines if a user has a role. You might need to call this
function many times during a single request. To keep from hitting the database
every time this information is needed you might do something like the following::

    class Person(db.Model):
        @cache.memoize(50)
        def has_membership(self, role_id):
            return Group.query.filter_by(user=self, role_id=role_id).count() >= 1


.. warning::

    Using mutable objects (classes, etc) as part of the cache key can become
    tricky. It is suggested to not pass in an object instance into a memoized
    function. However, the memoize does perform a repr() on the passed in arguments
    so that if the object has a __repr__ function that returns a uniquely
    identifying string for that object, that will be used as part of the
    cache key.

    For example, an sqlalchemy person object that returns the database id as
    part of the unique identifier.::

        class Person(db.Model):
            def __repr__(self):
                return "%s(%s)" % (self.__class__.__name__, self.id)


Deleting memoize cache
``````````````````````

.. versionadded:: 0.2

You might need to delete the cache on a per-function bases. Using the above
example, lets say you change the users permissions and assign them to a role,
but now you need to re-calculate if they have certain memberships or not.
You can do this with the :meth:`~Cache.delete_memoized` function.::

    cache.delete_memoized(user_has_membership)

.. note::

  If only the function name is given as parameter, all the memoized versions
  of it will be invalidated. However, you can delete specific cache by
  providing the same parameter values as when caching. In following
  example only the ``user``-role cache is deleted:

  .. code-block:: python

     user_has_membership('demo', 'admin')
     user_has_membership('demo', 'user')

     cache.delete_memoized(user_has_membership, 'demo', 'user')


Caching Jinja2 Snippets
-----------------------

Usage::

    {% cache [timeout [,[key1, [key2, ...]]]] %}
    ...
    {% endcache %}

By default the value of "path to template file" + "block start line" is used as cache key.
Also key name can be set manually. Keys are concated together into a single string.
that can be used to avoid the same block evaluating in different templates.

Set the timeout to None for no timeout, but with custom keys::

    {% cache None "key" %}...

Set timeout to "del" to delete cached value::

    {% cache 'del' %}...

If keys are provided, you may easily generate the template fragment key and
delete it from outside of the template context::

    from flask_caching import make_template_fragment_key
    key = make_template_fragment_key("key1", vary_on=["key2", "key3"])
    cache.delete(key)

Example::

    Considering we have render_form_field and render_submit macroses.
    {% cache 60*5 %}
    <div>
        <form>
        {% render_form_field form.username %}
        {% render_submit %}
        </form>
    </div>
    {% endcache %}


Clearing Cache
--------------

See :meth:`~Cache.clear`.

Here's an example script to empty your application's cache:

.. code-block:: python

    from flask_caching import Cache

    from yourapp import app, your_cache_config

    cache = Cache()


    def main():
        cache.init_app(app, config=your_cache_config)

        with app.app_context():
            cache.clear()

    if __name__ == '__main__':
        main()


.. warning::

    Some backend implementations do not support completely clearing the cache.
    Also, if you're not using a key prefix, some implementations (e.g. Redis)
    will flush the whole database. Make sure you're not storing any other
    data in your caching database.


Configuring Flask-Caching
-------------------------

The following configuration values exist for Flask-Caching:

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|


=============================== ==================================================================
``CACHE_TYPE``                  Specifies which type of caching object to
                                use. This is an import string that will
                                be imported and instantiated. It is
                                assumed that the import object is a
                                function that will return a cache
                                object that adheres to the werkzeug cache
                                API.

                                For werkzeug.contrib.cache objects, you
                                do not need to specify the entire
                                import string, just one of the following
                                names.

                                Built-in cache types:

                                * **null**: NullCache (default)
                                * **simple**: SimpleCache
                                * **filesystem**: FileSystemCache
                                * **redis**: RedisCache (Werkzeug >= 0.7 and redis required)
                                * **uwsgi**: UWSGICache (Werkzeug >= 0.12 and uwsgi required)
                                * **memcached**: MemcachedCache (pylibmc or memcache required)
                                * **gaememcached**: GAEMemcachedCache
                                * **saslmemcached**: SASLMemcachedCache (pylibmc required)
                                * **spreadsaslmemcached**: SpreadSASLMemcachedCache (pylibmc required)

``CACHE_NO_NULL_WARNING``       Silents the warning message when using
                                cache type of 'null'.
``CACHE_ARGS``                  Optional list to unpack and pass during
                                the cache class instantiation.
``CACHE_OPTIONS``               Optional dictionary to pass during the
                                cache class instantiation.
``CACHE_DEFAULT_TIMEOUT``       The default timeout that is used if no
                                timeout is specified. Unit of time is
                                seconds.
``CACHE_THRESHOLD``             The maximum number of items the cache
                                will store before it starts deleting
                                some. Used only for SimpleCache and
                                FileSystemCache
``CACHE_KEY_PREFIX``            A prefix that is added before all keys.
                                This makes it possible to use the same
                                memcached server for different apps.
                                Used only for RedisCache, MemcachedCache and
                                GAEMemcachedCache.
``CACHE_UWSGI_NAME``            The name of the uwsgi caching instance to
                                connect to, for example: mycache@localhost:3031,
                                defaults to an empty string, which means uWSGI
                                will cache in the local instance. If the cache
                                is in the same instance as the werkzeug app,
                                you only have to provide the name of the cache.
``CACHE_MEMCACHED_SERVERS``     A list or a tuple of server addresses.
                                Used only for MemcachedCache
``CACHE_MEMCACHED_USERNAME``    Username for SASL authentication with memcached.
                                Used only for SASLMemcachedCache
``CACHE_MEMCACHED_PASSWORD``    Password for SASL authentication with memcached.
                                Used only for SASLMemcachedCache
``CACHE_REDIS_HOST``            A Redis server host. Used only for RedisCache.
``CACHE_REDIS_PORT``            A Redis server port. Default is 6379.
                                Used only for RedisCache.
``CACHE_REDIS_PASSWORD``        A Redis password for server. Used only for RedisCache.
``CACHE_REDIS_DB``              A Redis db (zero-based number index). Default is 0.
                                Used only for RedisCache.
``CACHE_DIR``                   Directory to store cache. Used only for
                                FileSystemCache.
``CACHE_REDIS_URL``             URL to connect to Redis server.
                                Example ``redis://user:password@localhost:6379/2``.
                                Used only for RedisCache.
=============================== ==================================================================


In addition the standard Flask ``TESTING`` configuration option is used. If this
is True then **Flask-Caching** will use NullCache only.


Built-in Cache Backends
-----------------------


NullCache
`````````

Set ``CACHE_TYPE`` to ``null`` to use this type.

Cache that doesn't cache

- CACHE_ARGS
- CACHE_OPTIONS


SimpleCache
```````````

Set ``CACHE_TYPE`` to ``simple`` to use this type.

Uses a local python dictionary for caching. This is not really thread safe.

Relevant configuration values

- CACHE_DEFAULT_TIMEOUT
- CACHE_THRESHOLD
- CACHE_ARGS
- CACHE_OPTIONS


FileSystemCache
```````````````

Set ``CACHE_TYPE`` to ``filesystem`` to use this type.

Uses the filesystem to store cached values

- CACHE_DEFAULT_TIMEOUT
- CACHE_DIR
- CACHE_THRESHOLD
- CACHE_ARGS
- CACHE_OPTIONS


RedisCache
``````````

Set ``CACHE_TYPE`` to ``redis`` to use this type.

- CACHE_DEFAULT_TIMEOUT
- CACHE_KEY_PREFIX
- CACHE_REDIS_HOST
- CACHE_REDIS_PORT
- CACHE_REDIS_PASSWORD
- CACHE_REDIS_DB
- CACHE_ARGS
- CACHE_OPTIONS
- CACHE_REDIS_URL


MemcachedCache
``````````````

Set ``CACHE_TYPE`` to ``memcached`` to use this type.

Uses a memcached server as a backend. Supports either pylibmc or memcache or
google app engine memcache library.

Relevant configuration values

- CACHE_DEFAULT_TIMEOUT
- CACHE_KEY_PREFIX
- CACHE_MEMCACHED_SERVERS
- CACHE_ARGS
- CACHE_OPTIONS


GAEMemcachedCache
`````````````````

Set ``CACHE_TYPE`` to ``gaememcached`` to use this type.

Is MemcachedCache under a different name


SASLMemcachedCache
``````````````````

Set ``CACHE_TYPE`` to ``saslmemcached`` to use this type.

Uses a memcached server as a backend. Intended to be used with a SASL enabled
connection to the memcached server. pylibmc is required and SASL must be supported
by libmemcached.

Relevant configuration values

- CACHE_DEFAULT_TIMEOUT
- CACHE_KEY_PREFIX
- CACHE_MEMCACHED_SERVERS
- CACHE_MEMCACHED_USERNAME
- CACHE_MEMCACHED_PASSWORD
- CACHE_ARGS
- CACHE_OPTIONS

.. versionadded:: 0.10


SpreadSASLMemcachedCache
````````````````````````

Set ``CACHE_TYPE`` to ``spreadsaslmemcached`` to use this type.

Same as SASLMemcachedCache however, it has the ablity to spread value across
multiple keys if it is bigger than the memcached treshold which by
default is 1M. Uses pickle.

.. versionadded:: 0.11

.. versionchanged::  1.1.0
    Renamed ``spreadsaslmemcachedcache`` to ``spreadsaslmemcached`` for
    the sake of consistency.


Custom Cache Backends
---------------------

You are able to easily add your own custom cache backends by exposing a function
that can instantiate and return a cache object. ``CACHE_TYPE`` will be the
import string to your custom function. It should expect to receive three
arguments.

* ``app``
* ``args``
* ``kwargs``

Your custom cache object must also subclass the
:class:`werkzeug.contrib.cache.BaseCache` class. Flask-Caching will make sure
that ``threshold`` is already included in the kwargs options dictionary since
it is common to all BaseCache classes.

An example Redis cache implementation::

    #: the_app/custom.py
    class RedisCache(BaseCache):
        def __init__(self, servers, default_timeout=500):
            pass

    def redis(app, config, args, kwargs):
       args.append(app.config['REDIS_SERVERS'])
       return RedisCache(*args, **kwargs)

With this example, your ``CACHE_TYPE`` might be ``the_app.custom.redis``

An example PylibMC cache implementation to change binary setting and provide
username/password if SASL is enabled on the library::

    #: the_app/custom.py
    def pylibmccache(app, config, args, kwargs):
        return pylibmc.Client(servers=config['CACHE_MEMCACHED_SERVERS'],
                              username=config['CACHE_MEMCACHED_USERNAME'],
                              password=config['CACHE_MEMCACHED_PASSWORD'],
                              binary=True)

With this example, your ``CACHE_TYPE`` might be ``the_app.custom.pylibmccache``


API
---

.. autoclass:: Cache
   :members: init_app,
             get, set, add, delete, get_many, set_many, delete_many, clear,
             cached, memoize, delete_memoized, delete_memoized_verhash


Additional Information
----------------------

.. toctree::
   :maxdepth: 2

   changelog
   license

* :ref:`search`


.. _Flask: http://flask.pocoo.org/
.. _werkzeug: http://werkzeug.pocoo.org/
