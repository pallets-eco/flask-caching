from werkzeug.contrib.cache import (NullCache, SimpleCache, MemcachedCache,
                                    GAEMemcachedCache, FileSystemCache)

def null(app, args, kwargs):
    return NullCache()

def simple(app, args, kwargs):
    kwargs.update(dict(threshold=app.config['CACHE_THRESHOLD']))
    return SimpleCache(*args, **kwargs)

def memcached(app, args, kwargs):
    args.append(app.config['CACHE_MEMCACHED_SERVERS'])
    kwargs.update(dict(key_prefix=app.config['CACHE_KEY_PREFIX']))
    return MemcachedCache(*args, **kwargs)

def gaememcached(app, args, kwargs):
    kwargs.update(dict(key_prefix=app.config['CACHE_KEY_PREFIX']))
    return GAEMemcachedCache(*args, **kwargs)
    
def filesystem(app, args, kwargs):
    args.append(app.config['CACHE_DIR'])
    kwargs.update(dict(threshold=app.config['CACHE_THRESHOLD']))
    return FileSystemCache(*args, **kwargs)
