# -*- coding: utf-8 -*-
"""
    flaskext.cache
    ~~~~~~~~~~~~~~

    Adds cache support to your application.

    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details
"""
from functools import wraps

from werkzeug import import_string
from werkzeug.contrib.cache import BaseCache, NullCache
from flask import request, current_app


#: Cache Object
################

class Cache(object):
    """
    This class is used to control the cache objects.

    If TESTING is True it will use NullCache.
    """

    def __init__(self, app=None):
        self.cache = None

        if app is not None:
            self.init_app(app)
        else:
            self.app = None
            
        self._memoized = []

    def init_app(self, app):
        "This is used to initialize cache with your app object"

        app.config.setdefault('CACHE_DEFAULT_TIMEOUT', 300)
        app.config.setdefault('CACHE_THRESHOLD', 500)
        app.config.setdefault('CACHE_KEY_PREFIX', None)
        app.config.setdefault('CACHE_MEMCACHED_SERVERS', None)
        app.config.setdefault('CACHE_DIR', None)
        app.config.setdefault('CACHE_OPTIONS', None)
        app.config.setdefault('CACHE_ARGS', [])
        app.config.setdefault('CACHE_TYPE', 'null')

        self.app = app

        self._set_cache()

    def _set_cache(self):
        if self.app.config['TESTING']:
            self.cache = NullCache()
        else:
            import_me = self.app.config['CACHE_TYPE']
            if '.' not in import_me:
                import_me = 'flaskext.cache.backends.' + \
                            import_me
            
            cache_obj = import_string(import_me)
            cache_args = self.app.config['CACHE_ARGS'][:]
            cache_options = dict(default_timeout= \
                                 self.app.config['CACHE_DEFAULT_TIMEOUT'])
            
            if self.app.config['CACHE_OPTIONS']:
                cache_options.update(self.app.config['CACHE_OPTIONS'])
            
            self.cache = cache_obj(self.app, cache_args, cache_options)
            
            if not isinstance(self.cache, BaseCache):
                raise TypeError("Cache object must subclass "
                                "werkzeug.contrib.cache.BaseCache")

    def get(self, *args, **kwargs):
        "Proxy function for internal cache object."
        return self.cache.get(*args, **kwargs)

    def set(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.set(*args, **kwargs)

    def add(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.add(*args, **kwargs)

    def delete(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.delete(*args, **kwargs)

    def cached(self, timeout=None, key_prefix='view/%s', unless=None):
        """
        Decorator. Use this to cache a function. By default the cache key
        is `view/request.path`. You are able to use this decorator with any
        function by changing the `key_prefix`. If the token `%s` is located
        within the `key_prefix` then it will replace that with `request.path`

        Example::

            # An example view function
            @cache.cached(timeout=50)
            def big_foo():
                return big_bar_calc()

            # An example misc function to cache.
            @cache.cached(key_prefix='MyCachedList')
            def get_list():
                return [random.randrange(0, 1) for i in range(50000)]

        .. code-block:: pycon

            >>> my_list = get_list()
            
        .. note::
        
            You MUST have a request context to actually called any functions
            that are cached.

        :param timeout: Default None. If set to an integer, will cache for that
                        amount of time. Unit of time is in seconds.
        :param key_prefix: Default 'view/%(request.path)s'. Beginning key to .
                           use for the cache key.
        :param unless: Default None. Cache will *always* execute the caching
                       facilities unless this callable is true.
                       This will bypass the caching entirely.
        """

        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                #: Bypass the cache entirely.
                if callable(unless) and unless() is True:
                    return f(*args, **kwargs)

                if '%s' in key_prefix:
                    cache_key = key_prefix % request.path
                else:
                    cache_key = key_prefix
                
                rv = self.cache.get(cache_key)
                if rv is None:
                    rv = f(*args, **kwargs)
                    self.cache.set(cache_key, rv, timeout=timeout)
                return rv
            return decorated_function
        return decorator

    def memoize(self, timeout=None):
        """
        Use this to cache the result of a function, taking its arguments into
        account in the cache key.

        Information on
        `Memoization <http://en.wikipedia.org/wiki/Memoization>`_.

        Example::

            @cache.memoize(timeout=50)
            def big_foo(a, b):
                return a + b + random.randrange(0, 1000)

        .. code-block:: pycon

            >>> big_foo(5, 2)
            753
            >>> big_foo(5, 3)
            234
            >>> big_foo(5, 2)
            753

        :param timeout: Default None. If set to an integer, will cache for that
                        amount of time. Unit of time is in seconds.
        """

        def memoize(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = ('memoize', f.__name__, id(f), args, str(kwargs))
                                
                rv = self.cache.get(cache_key)
                if rv is None:
                    rv = f(*args, **kwargs)
                    self.cache.set(cache_key, rv, timeout=timeout)
                    if cache_key not in self._memoized:
                        self._memoized.append(cache_key)
                return rv
            return decorated_function
        return memoize
    
    def delete_memoized(self, *keys):
        """
        Deletes all of the cached functions that used Memoize for caching.
        
        Example::
        
            @cache.memoize(50)
            def random_func():
                return random.randrange(1, 50)
            
        .. code-block:: pycon
        
            >>> random_func()
            43
            >>> random_func()
            43
            >>> cache.delete_memoized('random_func')
            >>> random_func()
            16
            
        :param \*keys: A list of function names to clear from cache.
        """
        def deletes(item):
            if item[0] == 'memoize' and item[1] in keys:
                self.cache.delete(item)
                return True
            return False
        
        self._memoized[:] = [x for x in self._memoized if not deletes(x)]
        

