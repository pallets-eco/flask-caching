.. currentmodule:: flask_caching

Usage
=====

Caching View Functions
----------------------

To cache view functions you will use the :meth:`~Cache.cached` decorator.
This decorator will use request.path by default for the cache_key::

    @app.route("/")
    @cache.cached(timeout=50)
    def index():
        return render_template('index.html')

The cached decorator has another optional argument called ``unless``. This
argument accepts a callable that returns True or False. If ``unless`` returns
``True`` then it will bypass the caching mechanism entirely.

To dynamically determine the timeout within the view, you can return `CachedResponse`,
a subclass of `flask.Response`::

    @app.route("/")
    @cache.cached()
    def index():
        return CachedResponse(
            response=make_response(render_template('index.html')),
            timeout=50,
        )

.. warning::

    When using ``cached`` on a view, take care to put it between Flask's
    ``@route`` decorator and your function definition. Example::

        @app.route('/')
        @cache.cached(timeout=50)
        def index():
            return 'Cached for 50s'

    If you reverse both decorators, what will be cached is the result of
    ``@route`` decorator, and not the result of your view function.


Deleting Cached Views
`````````````````````

When you want to remove the value of a cached view you can use :meth:`~Cache.delete_cached`
instead of :meth:`~Cache.delete`. :meth:`~Cache.delete_cached`. builds the key of the
decorated view and deletes the cache in one go::

    @app.route("/user/<name>")
    @cache.cached(timeout=50)
    def user(name):
        return render_template("user.html", name=name)

    cache.delete_cached(user, "/user/Fred")

Outside of a request context the view doesn't know which request was used to build
the cache key. So to make it work outside of a request context you have to pass the
``path``. You can also use the view function and the named arguments of the view
in which case the path is built using ``url_for()``::

    cache.delete_cached(user, name="bob")

When you cache views with ``query_string=True`` you also have to pass the query string/args
because otherwise the cache key cannot be built::

    @app.route("/works")
    @cache.cached(timeout=50, query_string=True)
    def works():
        return do_search(request.args)

    cache.delete_cached(works, "/works", "limit=15&mock=true")

You can use either pass the query string as a string, a mapping or an iterable of
``(key, value)`` pairs::

    cache.delete_cached(works, "/works", {"limit": 15, "mock": "true"})

Additionally, ``path`` and ``query_args`` are also supported by the views ``make_cache_key()``::

    key = works.make_cache_key(path="/works", query_args={"limit": 15})

.. note::

    If you view has arguments named ``path`` or ``query_args`` you have to build the key
    from via the request context!


Caching Pluggable View Classes
------------------------------

Flask's pluggable view classes are also supported. To cache them, use the same
:meth:`~Cache.cached` decorator on the ``dispatch_request`` method::

    from flask.views import View

    class MyView(View):
        @cache.cached(timeout=50)
        def dispatch_request(self):
            return 'Cached for 50s'


Caching Other Functions
-----------------------

Using the same ``@cached`` decorator you are able to cache the result of other
non-view related functions. The only stipulation is that you replace the
``key_prefix``, otherwise it will use the request.path cache_key.
Keys control what should be fetched from the cache. If, for example, a key
does not exist in the cache, a new key-value entry will be created in the
cache. Otherwise the value (i.e. the cached result) of the key will be
returned::

    @cache.cached(timeout=50, key_prefix='all_comments')
    def get_all_comments():
        comments = do_serious_dbio()
        return [x.author for x in comments]

    cached_comments = get_all_comments()

Make Custom `Cache Key`
-----------------------

Sometimes you want to define your cache key for each route. Using the same ``@cached``
decorator you are able to specify how this key is generated. This might be useful when
the key for cache should not be just the default key_prefix, but has to be derived
from other parameters in a request. An example usecase would be for caching POST routes,
where the cache key should be derived from the data in that request, rather than just the
route/view itself.

``make_cache_key`` can be used to specify such a function. The function should return a
string which should act like the key to the required value that is being cached::

   def make_key():
      """A function which is called to derive the key for a computed value.
         The key in this case is the concat value of all the json request
         parameters. Other strategy could to use any hashing function.
      :returns: unique string for which the value should be cached.
      """
      user_data = request.get_json()
      return ",".join([f"{key}={value}" for key, value in user_data.items()])

   @app.route("/hello", methods=["POST"])
   @cache.cached(timeout=60, make_cache_key=make_key)
   def some_func():
      ....


Memoization
-----------

See :meth:`~Cache.memoize`

In memoization, the functions arguments are also included into the cache_key.

.. note::

    With functions that do not receive arguments, :meth:`~Cache.cached` and
    :meth:`~Cache.memoize` are effectively the same.

Memoize is also designed for methods, since it will take into account
the identity of the ``self`` or ``cls`` argument as part of the cache
key. By default this identity is derived from ``repr(obj)`` (or
``obj.__caching_id__()`` if the object provides one). It is **not**
based on Python's built-in :func:`id`, so two distinct instances that
share the same ``repr`` (for example two ORM objects loaded for the
same row) will share a memoize cache entry.

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

    On a ``staticmethod`` or a ``classmethod``, ``@staticmethod`` or
    ``@classmethod`` the route decorator must be applied at the top of the decorator stack
    (visually first, logically last) following the same logic as ``@route`` and ``@cached``
    above::

        class Person(db.Model):
            @staticmethod
            @cache.memoize(50)
            def calc_budget():
                return do_serious_dbio()


.. warning::

    Using mutable objects (classes, etc) as part of the cache key can become
    tricky. It is suggested to not pass in an object instance into a memoized
    function. However, the memoize does perform a repr() on the passed in arguments
    so that if the object has a __repr__ function that returns a uniquely
    identifying string for that object, that will be used as part of the
    cache key.

    For example, an sqlalchemy person object that returns the database id as
    part of the unique identifier::

        class Person(db.Model):
            def __repr__(self):
                return "%s(%s)" % (self.__class__.__name__, self.id)



Deleting Memoize Cache
``````````````````````

.. versionadded:: 0.2

You might need to delete the cache on a per-function basis. Using the above
example, lets say you change the user's permissions and assign them to a role,
but now you need to re-calculate if they have certain memberships or not.
You can do this with the :meth:`~Cache.delete_memoized` function::

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

.. warning::

  If a classmethod is memoized, you must provide the ``class`` as the first
  ``*args`` argument.

  .. code-block:: python

    class Foobar(object):
        @classmethod
        @cache.memoize(5)
        def big_foo(cls, a, b):
            return a + b + random.randrange(0, 100000)

    cache.delete_memoized(Foobar.big_foo, Foobar, 5, 2)

Memoized methods are stored per instance, so how much is deleted depends on
whether the method is reached through an instance or through the class:

.. code-block:: python

    class Adder(object):
        @cache.memoize(5)
        def add(self, b):
            return b + random.random()

    adder1 = Adder()
    adder2 = Adder()

    # only the calls made on adder1, adder2 keeps its cache
    cache.delete_memoized(adder1.add)

    # every instance
    cache.delete_memoized(Adder.add)

    # only ``adder1.add(3)``
    cache.delete_memoized(adder1.add, 3)

Instances are told apart by their ``repr()``, which can be overridden by
defining a ``__caching_id__`` method, for example to key on a user id.

.. warning::

  A method reached through the class does not know which instance to delete
  the cache for, so the instance has to be passed as the first ``*args``
  argument, the same way a ``class`` is passed for a ``classmethod``:

  .. code-block:: python

    cache.delete_memoized(Adder.add, adder1, 3)

.. note::

  The :meth:`~Cache.delete_memoized` attribute that
  :meth:`~Cache.memoize` puts on the decorated function takes no arguments
  and always clears every instance, even when it is called through one:

  .. code-block:: python

    adder1.add.delete_memoized()  # same as cache.delete_memoized(Adder.add)


Decorator Options
-----------------

:meth:`~Cache.cached` and :meth:`~Cache.memoize` share most of their optional
arguments. ``query_string`` and ``response_hit_indication`` are accepted by
:meth:`~Cache.cached` only, ``make_name`` and ``args_to_ignore`` by
:meth:`~Cache.memoize` only.


unless
``````

A callable that bypasses the cache entirely while it returns ``True``. The
decorated function runs and its result is returned without the cache being
read or written::

    @app.route("/")
    @cache.cached(timeout=50, unless=lambda: current_user.is_authenticated)
    def index():
        return render_template('index.html')

If the callable accepts arguments it is called with the decorated function
followed by the call's own arguments, otherwise it is called with none.


forced_update
`````````````

A callable that refreshes the cached value while it returns ``True``, even if
the entry has not expired yet. Useful for background renewal::

    @app.route("/")
    @cache.cached(timeout=50, forced_update=lambda: feature_flags["fresh"])
    def index():
        return render_template('index.html')

If the callable accepts arguments it is called with the call's own arguments,
otherwise it is called with none. Unlike ``unless``, the result is still
written to the cache.


response_filter
```````````````

A callable invoked with the return value after the decorated function has run.
If it returns ``False`` the value is not stored. Use it to keep failures out
of the cache::

    def only_success(response):
        return response.status_code == 200

    @app.route("/")
    @cache.cached(timeout=50, response_filter=only_success)
    def index():
        return render_template('index.html')


cache_none
``````````

A cached ``None`` is indistinguishable from a cache miss, so by default the
decorated function runs again on every call. Set ``cache_none`` to ``True`` to
store ``None`` and use an extra key existence check to tell the two apart.

.. warning::

    This adds a second round trip to the backend, and can still return
    ``None`` wrongly if a concurrent call writes the key between the two
    calls. Returning a sentinel value instead is usually the better option.


.. _source-check:

source_check
````````````

Include the decorated function's source code in the cache key, so that editing
the body invalidates values cached by the previous version even when the
arguments are unchanged::

    @cache.memoize(timeout=50, source_check=True)
    def add(a, b):
        return a + b

Defaults to the ``CACHE_SOURCE_CHECK`` configuration value, which is ``False``.
This is meant for development, where a stale value from an older revision of a
function is confusing. It calls :func:`inspect.getsource` on every call, so
leave it off in production.


.. _hash-method:

hash_method
```````````

The hash constructor used when building cache keys. Defaults to the
``CACHE_HASH_METHOD`` configuration value, which is :func:`hashlib.sha256`.
Set it application wide::

    app.config["CACHE_HASH_METHOD"] = hashlib.sha512

or override it for a single decorator::

    @cache.memoize(timeout=50, hash_method=hashlib.sha512)
    def add(a, b):
        return a + b

.. warning::

    The cache key is derived from this hash, so changing it makes every
    existing cached entry unreachable. The stale entries are not deleted; they
    remain in the backend until they expire.

Do not confuse this with ``CACHE_FILE_HASH_METHOD``, which the FileSystemCache
backend uses to name the files it writes. The two are independent.


query_string
````````````

:meth:`~Cache.cached` only. Build the cache key from the request's query
string instead of ``key_prefix``. The arguments are sorted before hashing, so
``?limit=10&offset=20`` and ``?offset=20&limit=10`` share one entry::

    @app.route("/search")
    @cache.cached(timeout=50, query_string=True)
    def search():
        return do_search(request.args)

Deleting such an entry needs the query string as well, see
`Deleting cached views`_.


response_hit_indication
```````````````````````

:meth:`~Cache.cached` only. When ``True``, responses that were served from the
cache carry a ``hit_cache`` header. Responses produced by running the view do
not::

    @app.route("/")
    @cache.cached(timeout=50, response_hit_indication=True)
    def index():
        return render_template('index.html')

.. versionadded:: 2.3.0


make_name
`````````

:meth:`~Cache.memoize` only. A callable that receives the name of the
decorated function and returns the name to use in the cache key. Without it
the function name is used.


args_to_ignore
``````````````

:meth:`~Cache.memoize` only. Names of arguments to leave out of the cache key,
so that calls differing only in those arguments share an entry::

    @cache.memoize(timeout=50, args_to_ignore=["session"])
    def get_user(session, user_id):
        return session.query(User).get(user_id)

.. versionadded:: 1.10


Caching Jinja2 Snippets
-----------------------

Usage::

    {% cache [timeout [,[key1, [key2, ...]]]] %}
    ...
    {% endcache %}

By default, the value of "path to template file" + "block start line" is used as the cache key.
Also, the key name can be set manually. Keys are concatenated together into a single string, that
can be used to avoid the same block evaluating in different templates.

Set the timeout to ``None`` for no timeout, but with custom keys::

    {% cache None, "key" %}
    ...
    {% endcache %}

Set timeout to ``del`` to delete cached value::

    {% cache 'del', key1 %}
    ...
    {% endcache %}

If keys are provided, you may easily generate the template fragment key and
delete it from outside of the template context::

    from flask_caching import make_template_fragment_key
    key = make_template_fragment_key("key1", vary_on=["key2", "key3"])
    cache.delete(key)

Considering we have ``render_form_field`` and ``render_submit`` macros::

    {% cache 60*5 %}
    <div>
        <form>
        {% render_form_field(form.username) %}
        {% render_submit() %}
        </form>
    </div>
    {% endcache %}


Clearing Cache
--------------

See :meth:`~Cache.clear`. To delete the entry of a single view see
`Deleting cached views`_.

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


Explicitly Caching Data
-----------------------

Data can be cached explicitly by using the proxy methods like
:meth:`Cache.set`, and :meth:`Cache.get` directly. There are many other proxy
methods available via the :class:`Cache` class.

For example:

.. code-block:: python

    @app.route("/html")
    @app.route("/html/<foo>")
    def html(foo=None):
        if foo is not None:
            cache.set("foo", foo)
        bar = cache.get("foo")
        return render_template_string(
            "<html><body>foo cache: {{bar}}</body></html>", bar=bar
        )


Subclassing ``Cache``
---------------------

The proxy methods are the extension's own entry point to the backend, so
overriding them in a :class:`Cache` subclass also affects the caching done by
:meth:`~Cache.cached` and :meth:`~Cache.memoize`. This makes it possible to add
tracing, metrics or logging in one place and have it cover both explicit calls
and the decorators:

.. code-block:: python

    class InstrumentedCache(Cache):
        def get(self, *args, **kwargs):
            with tracer.trace("cache.get"):
                return super().get(*args, **kwargs)

        def set(self, *args, **kwargs):
            with tracer.trace("cache.set"):
                return super().set(*args, **kwargs)


    cache = InstrumentedCache(app, config={"CACHE_TYPE": "SimpleCache"})

Note that :meth:`~Cache.memoize` also uses :meth:`~Cache.get_many` and
:meth:`~Cache.set_many` for its internal version keys, so an override will see
that bookkeeping traffic as well. A cache miss makes two such round trips: one
to read the version before building the key, and one after the entry is written
to update the version keys expiry.

To reach backend specific functionality that :class:`Cache` does not proxy, use
the :attr:`Cache.cache` property instead of subclassing.

