Changelog
=========

Version 1.10.1
--------------

Released 2021-03-17

- A ``GoogleCloudStorageCache`` backend has been added to the user contributed
  caching backends. PR `#214 <https://github.com/sh4nks/flask-caching/pull/214>`_.
- Fix a regression introduced in the last release which broke all applications
  subclassing the ``Cache`` class.
- Add test_generic_get_bytes test case.
  PR `#236 <https://github.com/sh4nks/flask-caching/pull/236>`_.
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
  PR `#218 <https://github.com/sh4nks/flask-caching/pull/218>`_.
- Fix error in how the FileSystemCache counts the number of files.
  PR `#210 <https://github.com/sh4nks/flask-caching/pull/210>`_.
- Type Annotations have been added.
  PR `#198 <https://github.com/sh4nks/flask-caching/pull/198>`_.
- Add some basic logging to SimpleCache and FileSystemCache for better
  observability.
  PR `#203 <https://github.com/sh4nks/flask-caching/pull/203>`_.
- Add option in memoize to ignore args
  PR `#201 <https://github.com/sh4nks/flask-caching/pull/201>`_.
- Stop marking wheels as Python 2 compatible.
  PR `#196 <https://github.com/sh4nks/flask-caching/pull/196>`_.
- Fix ``default_timeout`` not being properly passed to its super constructor.
  PR `#187 <https://github.com/sh4nks/flask-caching/pull/187>`_.
- Fix ``kwargs`` not being passed on in function ``_memoize_make_cache_key``.
  PR `#184 <https://github.com/sh4nks/flask-caching/pull/184>`_.
- Add a Redis Cluster Mode caching backend.
  PR `#173 <https://github.com/sh4nks/flask-caching/pull/173>`_.
- Do not let PIP install this package on unsupported Python Versions.
  PR `#179 <https://github.com/sh4nks/flask-caching/pull/179>`_.
- Fix uWSGI initialization by checking if uWSGI has the 'cache2' option
  enabled. PR `#176 <https://github.com/sh4nks/flask-caching/pull/176>`_.
- Documentation updates and fixes.


Version 1.9.0
-------------

Released 2020-06-02

- Add an option to include the functions source code when generating the cache
  key. PR `#156 <https://github.com/sh4nks/flask-caching/pull/156>`_.
- Add an feature that allows one to completely control the way how cache keys
  are generated. For example, one can now implement a function that generates a
  cache key the based on POST requests.
  PR `#159 <https://github.com/sh4nks/flask-caching/pull/159>`_.
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
  PR `#140 <https://github.com/sh4nks/flask-caching/pull/140>`_ and
  `#141 <https://github.com/sh4nks/flask-caching/pull/141>`_.
- Allow to use ``__caching_id__`` rather than ``__repr__`` as an object
  caching key.
  PR `#123 <https://github.com/sh4nks/flask-caching/pull/123>`_.
- The RedisCache backend now support generating the key_prefix via a callable.
  PR `#109 <https://github.com/sh4nks/flask-caching/pull/109>`_.
- Emit a warning if the ``CACHE_TYPE`` is set to ``filesystem`` but no
  ``CACHE_DIR`` is set.
- Fixes Google App Engine Memcache backend.
  See issue `#120 <https://github.com/sh4nks/flask-caching/issues/120>`_ for
  more details.
- Various documentation updates and fixes.


Version 1.7.2
-------------

Released 2019-05-28

**This is the last version supporting Python 2!**

- Do not run a cached/memoized function if the cached return value is None.
  PR `#108 <https://github.com/sh4nks/flask-caching/pull/108>`_.


Version 1.7.1
-------------

Released 2019-04-16

- Fix introspecting Python 3 functions by using varkw.
  PR `#101 <https://github.com/sh4nks/flask-caching/pull/101>`_.
- Remove leftover files (``uwsgi.py``) in PyPI package. See issue
  `#102 <https://github.com/sh4nks/flask-caching/issues/102>`_ for more details.


Version 1.7.0
-------------

Released 2019-03-29

- Added a feature called 'response_filter' which enables one to only
  cache views depending on the response code.
  PR `#99 <https://github.com/sh4nks/flask-caching/pull/99>`_.
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
  PR `#94 <https://github.com/sh4nks/flask-caching/pull/94>`_.
- Re-added the ``gaememcached`` CACHE_TYPE for improved backwards compatibility.
- Documentation improvements


Version 1.5.0
-------------

Released 2019-02-23

- Add support for a Redis Sentinel Cluster.
  PR `#90 <https://github.com/sh4nks/flask-caching/pull/90>`_.
- Parameterize the hash function so alternatives can be used.
  PR `#77 <https://github.com/sh4nks/flask-caching/pull/77>`_.
- Include the deprecated ``werkzeug.contrib.cache`` module in Flask-Caching.
  PR `#75 <https://github.com/sh4nks/flask-caching/pull/75>`_.


Version 1.4.0
-------------

Released 2018-04-16

- Fix logic for creating key for var args in memoize.
  PR `#70 <https://github.com/sh4nks/flask-caching/pull/70>`_.
- Allow older Werkzeug versions by making the UWSGICache backend conditional.
  PR `#55 <https://github.com/sh4nks/flask-caching/pull/55>`_.
- Some documentation improvements.
  PR `#48 <https://github.com/sh4nks/flask-caching/pull/48>`_,
  `#51 <https://github.com/sh4nks/flask-caching/pull/51>`_,
  `#56 <https://github.com/sh4nks/flask-caching/pull/56>`_,
  `#67 <https://github.com/sh4nks/flask-caching/pull/67>`_.
- Some CI improvements.
  PR `#49 <https://github.com/sh4nks/flask-caching/pull/49>`_,
  `#50 <https://github.com/sh4nks/flask-caching/pull/50>`_.


Version 1.3.3
-------------

Released 2017-06-25

- Add support for multiple query params and use md5 for consistent hashing.
  PR `#43 <https://github.com/sh4nks/flask-caching/pull/43>`_.


Version 1.3.2
-------------

Released 2017-06-25

- Fix ``spreadsaslmemcached`` backend when using Python 3.
- Fix kwargs order when memoizing a function using Python 3.6 or greater.
  See `#27 <https://github.com/sh4nks/flask-caching/issues/27>`_.


Version 1.3.1
-------------

Released 2017-06-20

- Avoid breakage for environments with Werkzeug<0.12 installed because
  the uwsgi backend depends on Werkzeug >=0.12. See `#38 <https://github.com/sh4nks/flask-caching/issues/38>`_.


Version 1.3.0
-------------

Released 2017-06-17

- Add uWSGI Caching backend (requires Werkzeug >= 0.12)
- Provide a keyword `query_string` to the cached decorator in order to create
  the same cache key for different query string requests,
  so long as they have the same key/value (order does not matter).
  PR `#35 <https://github.com/sh4nks/flask-caching/issues/35>`_.
- Use pytest as test suite and test runner. Additionally, the tests have
  been split up into multiple files instead of having one big file.


Version 1.2.0
-------------

Released 2017-02-02

- Allows functions with kwargs to be memoized correctly. See `#18 <https://github.com/sh4nks/flask-caching/issues/18>`_.


Version 1.1.1
-------------

Released 2016-12-09

- Fix PyPI Package distribution. See `#15 <https://github.com/sh4nks/flask-caching/issues/15>`_.


Version 1.1.0
-------------

Released 2016-12-09

- Fix 'redis' backend import mechanisim. See `#14 <https://github.com/sh4nks/flask-caching/pull/14>`_.
- Made backends a module to better control which cache backends to expose
  and moved our custom clients into a own module inside of the backends
  module. See also `#14 <https://github.com/sh4nks/flask-caching/pull/14>`_ (and partly some own changes).
- Some docs and test changes. See `#8 <https://github.com/sh4nks/flask-caching/pull/8>`_
  and `#12 <https://github.com/sh4nks/flask-caching/pull/12>`_.


Version 1.0.1
-------------

Released 2016-08-30

- The caching wrappers like `add`, `set`, etc are now returning the wrapped
  result as someone would expect. See `#5 <https://github.com/sh4nks/flask-caching/pull/5>`_.


Version 1.0.0
-------------

Released 2016-07-05

- Changed the way of importing Flask-Cache. Instead of using the depreacted
  method for importing Flask Extensions (via ``flask.ext.cache``),
  the name of the extension,  ``flask_cache`` is used. Have a look at
  `Flask's documentation <http://flask.pocoo.org/docs/0.11/extensions/#flask-before-0-8>`_
  for more information regarding this matter. This also fixes the
  deprecation warning from Flask.
- Lots of PEP8 and Documentation fixes.
- Renamed this fork Flask-Caching (``flask_caching``) as it will now be
  available on PyPI for download.

In addition to the above mentioned fixes, following pull requests have been
merged into this fork of `Flask-Cache <https://github.com/thadeusb/flask-cache>`_:

- `#90 Update documentation: route decorator before cache <https://github.com/thadeusb/flask-cache/pull/90>`_
- `#95 Pass the memoize parameters into unless(). <https://github.com/thadeusb/flask-cache/pull/95>`_
- `#109 wrapped function called twice <https://github.com/thadeusb/flask-cache/pull/109>`_
- `#117 Moves setting the app attribute to the _set_cache method <https://github.com/thadeusb/flask-cache/pull/117>`_
- `#121 fix doc for delete_memoized <https://github.com/thadeusb/flask-cache/pull/121>`_
- `#122 Added proxy for werkzeug get_dict <https://github.com/thadeusb/flask-cache/pull/122>`_
- `#123 "forced_update" option to 'cache' and 'memoize' decorators <https://github.com/thadeusb/flask-cache/pull/123>`_
- `#124 Fix handling utf8 key args <https://github.com/thadeusb/flask-cache/pull/124)>`_ (cherry-picked)
- `#125 Fix unittest failing for redis unittest <https://github.com/thadeusb/flask-cache/pull/125>`_
- `#127 Improve doc for using @cached on view <https://github.com/thadeusb/flask-cache/pull/127>`_
- `#128 Doc for delete_memoized <https://github.com/thadeusb/flask-cache/pull/128>`_
- `#129 tries replacing inspect.getargspec with either signature or getfullargspec if possible <https://github.com/thadeusb/flask-cache/pull/129>`_
- `make_cache_key() returning incorrect key <https://github.com/SkierPGP/Flask-Cache/pull/1>`_ (cherry-picked)


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
