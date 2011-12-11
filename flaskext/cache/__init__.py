# -*- coding: utf-8 -*-
"""
    flaskext.cache
    ~~~~~~~~~~~~~~

    Adds cache support to your application.

    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details
"""
import hashlib
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

            my_list = get_list()
            
        .. note::
        
            You MUST have a request context to actually called any functions
            that are cached.
            
        .. versionadded:: 0.4
            The returned decorated function now has three function attributes
            assigned to it. These attributes are readable/writable.
            
                **uncached**
                    The original undecorated function
                
                **cache_timeout**
                    The cache timeout value for this function. For a custom value
                    to take affect, this must be set before the function is called.
                    
                **make_cache_key**
                    A function used in generating the cache_key used.

        :param timeout: Default None. If set to an integer, will cache for that
                        amount of time. Unit of time is in seconds.
        :param key_prefix: Default 'view/%(request.path)s'. Beginning key to .
                           use for the cache key.
                           
                           .. versionadded:: 0.3.4                           
                               Can optionally be a callable which takes no arguments
                               but returns a string that will be used as the cache_key.
                               
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
                    
                cache_key = decorated_function.make_cache_key(*args, **kwargs)

                rv = self.cache.get(cache_key)
                if rv is None:
                    rv = f(*args, **kwargs)
                    self.cache.set(cache_key, rv, 
                                   timeout=decorated_function.cache_timeout)
                return rv

            def make_cache_key(*args, **kwargs):
                if '%s' in key_prefix:
                    cache_key = key_prefix % request.path
                elif callable(key_prefix):
                    cache_key = key_prefix()
                else:
                    cache_key = key_prefix
                    
                cache_key = cache_key.encode('utf-8')
                
                return cache_key
            
            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout
            decorated_function.make_cache_key = make_cache_key

            return decorated_function
        return decorator
        
    def get_memoize_names(self):
        """
        Returns all function names used for memoized functions.
        
        This *will* include multiple function names when the memoized function
        has been called with differing arguments.
        
        :return: set of function names
        """
        return set([item[0] for item in self._memoized])
        
    def get_memoize_keys(self):
        """
        Returns all cache_keys used for memoized functions.
        
        :return: list generator of cache_keys
        """    
        return [item[1] for item in self._memoized]

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
            
        .. versionadded:: 0.4
            The returned decorated function now has three function attributes
            assigned to it. These attributes are readable/writable.
            
                **uncached**
                    The original undecorated function
                
                **cache_timeout**
                    The cache timeout value for this function. For a custom value
                    to take affect, this must be set before the function is called.
                    
                **make_cache_key**
                    A function used in generating the cache_key used.

        :param timeout: Default None. If set to an integer, will cache for that
                        amount of time. Unit of time is in seconds.
        """

        def memoize(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = decorated_function.make_cache_key(*args, **kwargs)

                rv = self.cache.get(cache_key)
                if rv is None:
                    rv = f(*args, **kwargs)
                    self.cache.set(cache_key, rv, 
                                   timeout=decorated_function.cache_timeout)
                    self._memoized.append((f.__name__, cache_key))
                return rv

            def make_cache_key(*args, **kwargs):
                cache_key = hashlib.md5()

                try:
                    updated = "{0}{1}{2}".format(f.__name__, args, kwargs)
                except AttributeError:
                    updated = "%s%s%s" % (f.__name__, args, kwargs)

                cache_key.update(updated)
                cache_key = cache_key.digest().encode('base64')[:22]
                
                return cache_key

            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout
            decorated_function.make_cache_key = make_cache_key

            return decorated_function
        return memoize
    
    def delete_memoized(self, fname, *args, **kwargs):
        """
        Deletes the specified functions caches, based by given parameters.
        If parameters are given, only the functions that were memoized with them
        will be erased. Otherwise all the versions of the caches will be deleted.
        
        Example::
        
            @cache.memoize(50)
            def random_func():
                return random.randrange(1, 50)

            @cache.memoize()
            def param_func(a, b):
                return a+b+random.randrange(1, 50)
            
        .. code-block:: pycon
        
            >>> random_func()
            43
            >>> random_func()
            43
            >>> cache.delete_memoized('random_func')
            >>> random_func()
            16
            >>> param_func(1, 2)
            32
            >>> param_func(1, 2)
            32
            >>> param_func(2, 2)
            47
            >>> cache.delete_memoized('param_func', 1, 2)
            >>> param_func(1, 2)
            13
            >>> param_func(2, 2)
            47

            
        :param fname: Name of the memoized function.
        :param \*args: A list of positional parameters used with memoized function.
        :param \**kwargs: A dict of named parameters used with memoized function.
        """
        def deletes(item):

            # If no parameters given, delete all memoized versions of the function
            if not args and not kwargs:
              if item[0] == fname:
                self.cache.delete(item[1])
                return True
              return False

            # Construct the cache key as in memoized function
            cache_key = hashlib.md5()
            try:
                updated = "{0}{1}{2}".format(fname, args, kwargs)
            except AttributeError:
                updated = "%s%s%s" % (fname, args, kwargs)
            cache_key.update(updated)
            cache_key = cache_key.digest().encode('base64')[:22]

            if item[1] == cache_key:
                self.cache.delete(item[1])
                return True
            return False
        
        self._memoized[:] = [x for x in self._memoized if not deletes(x)]
        

