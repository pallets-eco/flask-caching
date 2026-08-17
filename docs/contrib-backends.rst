Contributed Cache Backends
--------------------------

.. warning::
   The backends in this section were contributed by users of Flask-Caching.
   They are not officially supported: this project does not guarantee that
   they are maintained, tested or functional at any given time.  Use at your
   own risk.

Unlike the built-in backends, these cannot be selected by their class name
alone.  Set ``CACHE_TYPE`` to the full import path of the class.


.. _googlecloudstoragecache:

GoogleCloudStorageCache
```````````````````````

Set ``CACHE_TYPE`` to
``flask_caching.contrib.googlecloudstoragecache.GoogleCloudStorageCache`` to
use this type.  Uses a Google Cloud Storage bucket as a cache backend. The
``google-cloud-storage`` package is required.

Relevant configuration values

- CACHE_DEFAULT_TIMEOUT
- CACHE_KEY_PREFIX
- CACHE_ARGS
- CACHE_OPTIONS

``CACHE_GCS_BUCKET`` is required and is the name of the bucket to use. The
bucket must already exist.

The following entries in CACHE_OPTIONS are recognised, any others are passed
to ``google.cloud.storage.Client`` as ``**kwargs``

*delete_expired_objects_on_read*
    If ``True``, a read that finds a stale object deletes it before returning
    a response. This slows down responses. Defaults to ``False``.

*anonymous*
    If ``True``, use anonymous credentials. Useful for testing. Defaults to
    ``False``.

.. note::
   Cache keys must be valid GCS object names, that is a sequence of Unicode
   characters whose UTF-8 encoding is at most 1024 bytes long.

.. note::
   Expired cache objects are not purged automatically. Unless
   *delete_expired_objects_on_read* is enabled, stale objects have to be
   deleted out of band, for example with a bucket lifecycle rule::

       {"rule": [{"action": {"type": "Delete"},
                  "condition": {"daysSinceCustomTime": 0}}]}

   See `Object Lifecycle Management
   <https://cloud.google.com/storage/docs/lifecycle#dayssincecustomtime>`_.

.. versionadded:: 1.10.1


.. _uwsgicache:

UWSGICache
``````````

Set ``CACHE_TYPE`` to ``flask_caching.contrib.uwsgicache.UWSGICache`` to use
this type.  You also have to set ``CACHE_UWSGI_NAME`` to the cache name you
set in your uWSGI configuration.

Relevant configuration values

- CACHE_DEFAULT_TIMEOUT
- CACHE_IGNORE_ERRORS
- CACHE_UWSGI_NAME

.. note::
   This backend cannot be used when running under PyPy, because the uWSGI API
   implementation for PyPy is lacking the needed functionality.

.. versionchanged:: 1.10.0
   Moved to the user contributed backends.
