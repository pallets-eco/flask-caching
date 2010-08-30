# -*- coding: utf-8 -*-
"""
    flaskext.cache
    ~~~~~~~~~~~~~~
    
    Adds cache support to your application.
    
    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details
"""
from functools import wraps
from werkzeug.contrib.cache import (SimpleCache, NullCache, MemcachedCache,
                                    GAEMemcachedCache, FileSystemCache)

class Cache(object):
    """
    This class is used to control the cache objects.
    
    If TESTING is True it will use NullCache.
    """
    
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None
        
    def init_app(self, app):
        "This is used to initialize cache with your app object"
        
        app.config.setdefault('CACHE_DEFAULT_TIMEOUT', 300)
        app.config.setdefault('CACHE_THRESHOLD', 500)
        app.config.setdefault('CACHE_KEY_PREFIX', None)
        app.config.setdefault('CACHE_MEMCACHED_SERVERS', None)
        app.config.setdefault('CACHE_DIR', None)
        app.config.setdefault('CACHE_TYPE', 'NullCache')
        
        self.app = app
        
        self._set_cache()
        
    def _set_cache(self):
        if self.app.config['TESTING']:
            self.cache = NullCache()
        else:
            if self.app.config['CACHE_TYPE'] == 'Null':
                self.cache = NullCache()
            elif self.app.config['CACHE_TYPE'] == 'Simple':
                self.cache = SimpleCache(
                    threshold=app.config['CACHE_THRESHOLD'],
                    default_timeout=app.config['CACHE_DEFAULT_TIMEOUT']
                )
            elif self.app.config['CACHE_TYPE'] == 'Memcached':
                self.cache = MemcachedCache(
                    app.config['CACHE_MEMCACHED_SERVERS'],
                    default_timeout = app.config['CACHE_DEFAULT_TIMEOUT'],
                    key_prefix = app.config['CACHE_KEY_PREFIX']
                )
            elif self.app.config['CACHE_TYPE'] == 'GAE':
                self.cache = GAEMemcachedCache(
                    default_timeout = app.config['CACHE_DEFAULT_TIMEOUT'],
                    key_prefix = app.config['CACHE_KEY_PREFIX']
                )
            elif self.app.config['CACHE_TYPE'] == 'FileSystem':
                self.cache = FileSystemCache(
                    app.config['CACHE_DIR'],
                    threshold = app.config['CACHE_THRESHOLD'],
                    default_timeout = app.config['CACHE_DEFAULT_TIMEOUT']
                )
        
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
        function by changing the `key_prefix`. If the token `%s` is loacted
        within the `key_prefix` then it will replace that with `request.path`
        
        Example::
        
            #: An example view function
            @cache.cached(timeout=50)
            def big_foo():
                return big_bar_calc()
                
            #: An example misc function to cache.
            @cache.cached(key_prefix='MyCachedList')
            def get_list():
                return [random.randrange(0, 1) for i in range(50000)]
                
            >>> my_list = get_list()
        
        :param timeout: Default None. If set to an integer, will cache for that
                        amount of time.
        :param key_prefix: Default 'view/%(request.path)s'. Beginning key to .
                           use for the cache key.
        :param unless: Default None. Cache will *always* execute the caching
                       facilities unless this callable is true. This will bypass
                       the caching entirely.
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
                if not rv or current_app.debug:
                    rv = f(*args, **kwargs)
                    self.cache.set(cache_key, rv, timeout=timeout)
                return rv
            return decorated_function
        return decorator
        
    def memoize(self, timeout=None):
        """
        Use this to cache the result of a function, taking its arguments into
        account in the cache key. 
        
        Information on `Memoization <http://en.wikipedia.org/wiki/Memoization>`_.
        
        Example::
        
            @cache.memoize(timeout=50)
            def big_foo(a, b):
                return a + b + random.randrange(0, 1000)
                
            >>> big_foo(5, 2)
            753
            >>> big_foo(5, 3)
            234
            >>> big_foo(5, 2)
            753
        
        :param timeout: Default None. If set to an integer, will cache for that
                        amount of time.
        """
        
        def memoize(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = (f.__name__, id(f), args, str(kwargs))
                
                rv = self.cache.get(cache_key)
                if rv is None:
                    rv = f(*args, **kwargs)
                    self.cache.set(cache_key, rv)
                return rv
            return decorated_function
        return memoize
