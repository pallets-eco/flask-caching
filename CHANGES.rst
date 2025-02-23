Changelog
=========

Version 2.3.1
-------------

Released 2025-02-22

- Relax cachelib version to allow latest releases 



Version 2.3.0
-------------

Released 2024-05-04

- Added ``response_hit_indication`` flag to ``Cache.cached`` decorator for appending 'hit_cache' headers to responses, indicating cache hits.


Version 2.2.0
-------------

- Drop python 3.7 support
- python 3.11 officially supported
- Fix issue causing `args_to_ignore` to not work with `flask_caching.Cache.memoize` decorator when keyword arguments were used in the decorated function call


Version 2.1.0
-------------

Released 2024-10-08

- fix type signature in ``flask_caching.utils.make_template_fragment_key``. :pr:`430`
- Added docs and example for make_cache_key
- support Flask 3


Version 2.0.2
-------------

Released 2023-01-12

- fix issue with boto3 dependencie due to latest cachelib released
- migrate ``flask_caching.backends.RedisCluster`` dependency from redis-py-cluster to redis-py
- bug fix: make the ``make_cache_key`` attributed of decorated view functions writeable. :pr:`431`, :issue:`97`


Version 2.0.1
-------------

Released 2022-07-30

- Relax dependency pin to allow Flask 2.x.x


Version 2.0.0
-------------

Released 2022-06-26

- fix bug where ``flask_caching.backends.RedisSentinelCache.get_many`` would query wrong host&port combination. :pr:`372`
- Remove ``flask_caching.backends.FileSystemCache`` method overrides. It now shares 100% of ``cachelib.FileSystemCache`` API and is fully compatible. Functionality relient on implementation details of said overrides from older releases might not work anymore. :pr:`369`
- Add proxy to underlaying ``has`` method of cache clients. :pr:`356`
- ``flask_caching.backends.FileSystemCache`` now stores timestamps in a universal (non-frammed) way following the lastest version of ``cachelib.FileSystemCache``. The change also reduces overhead from 17 bytes (via previous method using pickle) to 4 bytes (using python's ``struct``). This, however, will break compatibily since older timestamps are serialized with a different strategy.


Version 1.11.1
--------------

Released 2022-05-27

- Add cachelib to setup.py: :pr:`354`


Version 1.11.0
--------------

Released 2022-05-27

- Add suport for cached/memoized generators. :pr:`286`
- Add support for Flask 2.0 async. :pr:`282`
- Cachelib is now used as backend. :pr:`308`
- Drop support for python 3.6. :pr:`332`
- Add support for dynamic cache timeouts `#296`
- Fix bug in ``CACHE_OPTIONS`` reading for redis in ``RedisSentinelCache``. :pr:`343`


Version 1.10.1
--------------

Released 2021-03-17

- A ``GoogleCloudStorageCache`` backend has been added to the user contributed
  caching backends. :pr:`214`
- Fix a regression introduced in the last release which broke all applications
  subclassing the ``Cache`` class.
- Add test_generic_get_bytes test case.
  :pr:`236`
- Various improvements and fixes.


Version 1.10.0
--------------

Released 2021-03-04

- **Important**: The way caching backends are loaded have been refactored.
  Instead of passing the name of the initialization function one can now use
  the full path to the caching backend class.
  For example:
  ``CACHE_TYPE="flask_caching.backends.SimpleCache"``.
  In the next major release (2.0), this will be the only supported way.
- UWSGICache is not officially supported anymore and moved to the user
  contributed backends.
- Switch from Travis-CI to GitHub Actions
- Fix add() in RedisCache without a timeout.
  :pr:`218`
- Fix error in how the FileSystemCache counts the number of files.
  :pr:`210`
- Type Annotations have been added.
  :pr:`198`
- Add some basic logging to SimpleCache and FileSystemCache for better
  observability.
  :pr:`203`
- Add option in memoize to ignore args
  :pr:`201`
- Stop marking wheels as Python 2 compatible.
  :pr:`196`
- Fix ``default_timeout`` not being properly passed to its super constructor.
  :pr:`187`
- Fix ``kwargs`` not being passed on in function ``_memoize_make_cache_key``.
  :pr:`184`
- Add a Redis Cluster Mode caching backend.
  :pr:`173`
- Do not let PIP install this package on unsupported Python Versions.
  :pr:`179`
- Fix uWSGI initialization by checking if uWSGI has the 'cache2' option
  enabled. :pr:`176`
- Documentation updates and fixes.


Version 1.9.0
-------------

Released 2020-06-02

- Add an option to include the functions source code when generating the cache
  key. :pr:`156`
- Add an feature that allows one to completely control the way how cache keys
  are generated. For example, one can now implement a function that generates a
  cache key the based on POST requests.
  :pr:`159`
- Fix the cache backend naming collisions by renaming them from ``simple`` to
  ``simplecache``, ``null`` to ``nullcache`` and ``filesystem`` to
  ``filesystemcache``.
- Explicitly pass the ``default_timeout`` to ``RedisCache`` from
  ``RedisSentinelCache``.
- Use ``os.replace`` instead of werkzeug's ``rename`` due to Windows raising an
  ``OSError`` if the dst file already exist.
- Documentation updates and fixes.


Version 1.8.0
-------------

Released 2019-11-24

- **BREAKING:** Removed support for Python 2. Python 3.5 and upwards are
  supported as of now.
- Add option to specify if ``None`` is a cached value or not. See
  :pr:`140` and
  `#141`
- Allow to use ``__caching_id__`` rather than ``__repr__`` as an object
  caching key.
  :pr:`123`
- The RedisCache backend now support generating the key_prefix via a callable.
  :pr:`109`
- Emit a warning if the ``CACHE_TYPE`` is set to ``filesystem`` but no
  ``CACHE_DIR`` is set.
- Fixes Google App Engine Memcache backend.
  See issue `#120` for
  more details.
- Various documentation updates and fixes.


Version 1.7.2
-------------

Released 2019-05-28

**This is the last version supporting Python 2!**

- Do not run a cached/memoized function if the cached return value is None.
  :pr:`108`


Version 1.7.1
-------------

Released 2019-04-16

- Fix introspecting Python 3 functions by using varkw.
  :pr:`101`
- Remove leftover files (``uwsgi.py``) in PyPI package. See issue
  `#102` for more details.


Version 1.7.0
-------------

Released 2019-03-29

- Added a feature called 'response_filter' which enables one to only
  cache views depending on the response code.
  :pr:`99`
- A DeprecationWarning got turned into a TypeError.


Version 1.6.0
-------------

Released 2019-03-06

- The ``delete_many`` function is now able to ignore any errors and continue
  deleting the cache. However, in order to preserve backwards compatibility,
  the default mode is to abort the deletion process. In order to use the new
  deletion mode, one has to flip the config setting ``CACHE_IGNORE_ERRORS`` to
  ``True``. This was and still is only relevant for the **filesystem** and
  **simple** cache backends.
  :pr:`94`
- Re-added the ``gaememcached`` CACHE_TYPE for improved backwards compatibility.
- Documentation improvements


Version 1.5.0
-------------

Released 2019-02-23

- Add support for a Redis Sentinel Cluster.
  :pr:`90`
- Parameterize the hash function so alternatives can be used.
  :pr:`77`
- Include the deprecated ``werkzeug.contrib.cache`` module in Flask-Caching.
  :pr:`75`


Version 1.4.0
-------------

Released 2018-04-16

- Fix logic for creating key for var args in memoize.
  :pr:`70`
- Allow older Werkzeug versions by making the UWSGICache backend conditional.
  :pr:`55`
- Some documentation improvements.
  :pr:`48`,
  `#51`,
  `#56`,
  `#67`
- Some CI improvements.
  :pr:`49`,
  `#50`


Version 1.3.3
-------------

Released 2017-06-25

- Add support for multiple query params and use md5 for consistent hashing.
  :pr:`43`


Version 1.3.2
-------------

Released 2017-06-25

- Fix ``spreadsaslmemcached`` backend when using Python 3.
- Fix kwargs order when memoizing a function using Python 3.6 or greater.
  See `#27`


Version 1.3.1
-------------

Released 2017-06-20

- Avoid breakage for environments with Werkzeug<0.12 installed because
  the uwsgi backend depends on Werkzeug >=0.12. See `#38`


Version 1.3.0
-------------

Released 2017-06-17

- Add uWSGI Caching backend (requires Werkzeug >= 0.12)
- Provide a keyword `query_string` to the cached decorator in order to create
  the same cache key for different query string requests,
  so long as they have the same key/value (order does not matter).
  :pr:`35`
- Use pytest as test suite and test runner. Additionally, the tests have
  been split up into multiple files instead of having one big file.


Version 1.2.0
-------------

Released 2017-02-02

- Allows functions with kwargs to be memoized correctly. See `#18`


Version 1.1.1
-------------

Released 2016-12-09

- Fix PyPI Package distribution. See `#15`


Version 1.1.0
-------------

Released 2016-12-09

- Fix 'redis' backend import mechanisim. See `#14`
- Made backends a module to better control which cache backends to expose
  and moved our custom clients into a own module inside of the backends
  module. See also `#14` (and partly some own changes).
- Some docs and test changes. See `#8`
  and `#12`


Version 1.0.1
-------------

Released 2016-08-30

- The caching wrappers like `add`, `set`, etc are now returning the wrapped
  result as someone would expect. See `#5`


Version 1.0.0
-------------

Released 2016-07-05

- Changed the way of importing Flask-Cache. Instead of using the depreacted
  method for importing Flask Extensions (via ``flask.ext.cache``),
  the name of the extension,  ``flask_cache`` is used. Have a look at
  `Flask's documentation`
  for more information regarding this matter. This also fixes the
  deprecation warning from Flask.
- Lots of PEP8 and Documentation fixes.
- Renamed this fork Flask-Caching (``flask_caching``) as it will now be
  available on PyPI for download.

In addition to the above mentioned fixes, following pull requests have been
merged into this fork of `Flask-Cache`:

- `#90 Update documentation: route decorator before cache`
- `#95 Pass the memoize parameters into unless().`
- `#109 wrapped function called twice`
- `#117 Moves setting the app attribute to the _set_cache method`
- `#121 fix doc for delete_memoized`
- `#122 Added proxy for werkzeug get_dict`
- `#123 "forced_update" option to 'cache' and 'memoize' decorators`
- `#124 Fix handling utf8 key args` (cherry-picked)
- `#125 Fix unittest failing for redis unittest`
- `#127 Improve doc for using @cached on view`
- `#128 Doc for delete_memoized`
- `#129 tries replacing inspect.getargspec with either signature or getfullargspec if possible`
- `make_cache_key() returning incorrect key` (cherry-picked)


Version 0.13
------------

Released 2014-04-21

- Port to Python >= 3.3 (requiring Python 2.6/2.7 for 2.x).
- Fixed bug with using per-memoize timeouts greater than the default timeout
- Added better support for per-instance memoization.
- Various bug fixes


Version 0.12
------------

Released 2013-04-29

- Changes jinja2 cache templates to use stable predictable keys. Previously
  the key for a cache tag included the line number of the template, which made
  it difficult to predict what the key would be outside of the application.
- Adds config variable `CACHE_NO_NULL_WARNING` to silence warning messages
  when using 'null' cache as part of testing.
- Adds passthrough to clear entire cache backend.


Version 0.11.1
--------------

Released 2013-04-7

- Bugfix for using memoize on instance methods.
  The previous key was id(self), the new key is repr(self)


Version 0.11
------------

Released 2013-03-23

- Fail gracefully in production if cache backend raises an exception.
- Support for redis DB number
- Jinja2 templatetag cache now concats all args together into a single key
  instead of treating each arg as a separate key name.
- Added delete memcache version hash function
- Support for multiple cache objects on a single app again.
- Added SpreadSASLMemcached, if a value is greater than the memcached threshold
  which defaults to 1MB, this splits the value across multiple keys.
- Added support to use URL to connect to redis.


Version 0.10.1
--------------

Released 2013-01-13

- Added warning message when using cache type of 'null'
- Changed imports to relative instead of absolute for AppEngine compatibility


Version 0.10.0
--------------

Released 2013-01-05

- Added `saslmemcached` backend to support Memcached behind SASL authentication.
- Fixes a bug with memoize when the number of args != number of kwargs


Version 0.9.2
-------------

Released 2012-11-18

- Bugfix with default kwargs


Version 0.9.1
-------------

Released 2012-11-16

- Fixes broken memoized on functions that use default kwargs


Version 0.9.0
-------------

Released 2012-10-14

- Fixes memoization to work on methods.


Version 0.8.0
-------------

Released 2012-09-30

- Migrated to the new flask extension naming convention of flask_cache instead of flaskext.cache
- Removed unnecessary dependencies in setup.py file.
- Documentation updates


Version 0.7.0
-------------

Released 2012-08-25

- Allows multiple cache objects to be instantiated with different configuration values.


Version 0.6.0
-------------

Released 2012-08-12

- Memoization is now safer for multiple applications using the same backing store.
- Removed the explicit set of NullCache if the Flask app is set testing=True
- Swapped Conditional order for key_prefix


Version 0.5.0
-------------

Released 2012-02-03

- Deleting memoized functions now properly functions in production
  environments where multiple instances of the application are running.
- get_memoized_names and get_memoized_keys have been removed.
- Added ``make_name`` to memoize, make_name is an optional callable that can be passed
  to memoize to modify the cache_key that gets generated.
- Added ``unless`` to memoize, this is the same as the unless parameter in ``cached``
- memoization now converts all kwargs to positional arguments, this is so that
  when a function is called multiple ways, it would evaluate to the same cache_key


Version 0.4.0
-------------

Released 2011-12-11

- Added attributes for uncached, make_cache_key, cache_timeout
  to the decorated functions.


Version 0.3.4
-------------

Released 2011-09-10

- UTF-8 encoding of cache key
- key_prefix argument of the cached decorator now supports callables.


Version 0.3.3
-------------

Released 2011-06-03

Uses base64 for memoize caching. This fixes rare issues where the cache_key
was either a tuple or larger than the caching backend would be able to
support.

Adds support for deleting memoized caches optionally based on function parameters.

Python 2.5 compatibility, plus bugfix with string.format.

Added the ability to retrieve memoized function names or cache keys.


Version 0.3.2
-------------

Bugfix release. Fixes a bug that would cause an exception if no
``CACHE_TYPE`` was supplied.

Version 0.3.1
-------------

Pypi egg fix.


Version 0.3
-----------

- CACHE_TYPE changed. Now one of ['null', 'simple', 'memcached',
  'gaememcached', 'filesystem'], or an import string to a function that will
  instantiate a cache object. This allows Flask-Cache to be much more
  extensible and configurable.


Version 0.2
-----------

- CACHE_TYPE now uses an import_string.
- Added CACHE_OPTIONS and CACHE_ARGS configuration values.
- Added delete_memoized


Version 0.1
-----------

- Initial public release
