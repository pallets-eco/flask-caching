.. currentmodule:: flask_caching

Overriding the Default Serializer
---------------------------------

Values are serialized by cachelib before they are handed to the backend. Every
backend holds a cachelib ``serializer`` instance. By default they all use ``pickle``:

- :ref:`SimpleCache <simplecache>` uses ``SimpleSerializer``
- :ref:`FileSystemCache <filesystemcache>` uses ``FileSystemSerializer``
- :ref:`RedisCache <rediscache>` uses ``RedisSerializer``
- :ref:`UWSGICache <uwsgicache>` uses ``UWSGISerializer``

:ref:`NullCache <nullcache>` and the memcached backends do not use one.

The attribute is defined on the backend class, so assigning to
:attr:`Cache.cache` replaces it for that cache instance only::

    from cachelib.serializers import JSONSerializer

    cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})
    cache.cache.serializer = JSONSerializer()


Example: Caching Unpicklable Values
```````````````````````````````````

The usual reason to replace the serializer is a value that pickle refuses to
handle. Responses from ``send_from_directory`` are one example: they wrap an
open file stream, and pickling a stream raises ``TypeError``.

The simplest fix is not a serializer at all. Calling
:meth:`~flask.Response.freeze` reads the stream into memory and makes the
response picklable::

    @app.route("/download")
    @cache.cached()
    def download():
        response = send_from_directory(directory, filename)
        response.freeze()
        return response

If the problem is not confined to one view, handle it in the serializer
instead. Wrap the stream in a picklable object and fall back to it when
``pickle.dumps`` fails::

    import io
    import pickle
    import typing as _t
    from os.path import basename
    from os.path import dirname

    from flask import Flask
    from flask import send_from_directory
    from flask_caching import Cache

    from cachelib.serializers import SimpleSerializer

    app = Flask(__name__)
    serializer_cache = Cache(app, config={"CACHE_TYPE": "simple"})

    class _PicklableStream:
        """
        Picklable wrapper for file like objects.
        """
        def __init__(self, data: bytes):
            self._data = data
            self._buf = io.BytesIO(data)

        def read(self, size: int = -1) -> bytes:
            return self._buf.read(size)

        def __getstate__(self):
            return {"data": self._data}

        def __setstate__(self, state):
            self.__init__(state["data"])


    class CustomSerializer(SimpleSerializer):
        """
        Custom serializer that handles pickling files streams.

        Read the file stream into memory and store it as bytes.
        """

        def _materialize_streams(self, value, _seen=None):
            _seen = _seen if _seen is not None else set()
            if id(value) in _seen:
                return value
            _seen.add(id(value))
            if hasattr(value, "read") and callable(value.read):
                return _PicklableStream(value.read())
            if hasattr(value, "__dict__"):
                for attr, attr_value in vars(value).items():
                    if hasattr(attr_value, "read") and callable(attr_value.read):
                        setattr(value, attr, _PicklableStream(attr_value.read()))
                    else:
                        self._materialize_streams(attr_value, _seen)
            return value

        def dumps(
            self, value: _t.Any, protocol: int = pickle.HIGHEST_PROTOCOL
        ) -> bytes | None:
            try:
                serialized = pickle.dumps(value, protocol)
            except TypeError:
                materialized = self._materialize_streams(value)
                return pickle.dumps(materialized, protocol)
            except (pickle.PickleError, pickle.PicklingError) as e:
                self._warn(e)
                return None
            return serialized

    serializer_cache.cache.serializer = CustomSerializer()

    @app.route("/serializer-override")
    @serializer_cache.cached()
    def root():
        return send_from_directory(dirname(__file__), basename(__file__))

Reading the stream loads the whole file into memory, both when caching and
when serving from the cache. Either approach trades memory for the cache hit.

.. note::

    Adapted from a suggestion in :issue:`167`.
