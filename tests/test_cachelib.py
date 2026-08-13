"""Tests for the cachelib integration.

Flask-Caching runs on top of cachelib: the built-in backends subclass their
cachelib counterparts, and ``CACHE_TYPE`` may also point straight at a
cachelib class, in which case the class is instantiated directly with
``CACHE_ARGS``/``CACHE_OPTIONS`` instead of going through
:meth:`.BaseCache.factory`.
"""

import cachelib
import pytest
from cachelib.serializers import SimpleSerializer

from flask_caching import Cache


@pytest.mark.parametrize(
    "cache_type",
    ("cachelib.SimpleCache", "cachelib.simple.SimpleCache"),
)
def test_cachelib_class_as_cache_type(app, cache_type):
    """A cachelib class is used as-is, not wrapped in a subclass."""
    app.config["CACHE_TYPE"] = cache_type
    cache = Cache(app)

    backend = app.extensions["cache"][cache]
    assert type(backend) is cachelib.SimpleCache


def test_cachelib_backend_gets_default_timeout(app):
    app.config["CACHE_TYPE"] = "cachelib.SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 111
    cache = Cache(app)

    assert app.extensions["cache"][cache].default_timeout == 111


def test_cachelib_backend_gets_cache_options(app):
    """CACHE_OPTIONS are passed as keyword arguments to the cachelib class."""
    app.config["CACHE_TYPE"] = "cachelib.SimpleCache"
    app.config["CACHE_OPTIONS"] = {"threshold": 7}
    cache = Cache(app)

    assert app.extensions["cache"][cache]._threshold == 7


def test_cachelib_backend_gets_cache_args(app, tmp_path):
    """CACHE_ARGS are passed as positional arguments to the cachelib class."""
    app.config["CACHE_TYPE"] = "cachelib.FileSystemCache"
    app.config["CACHE_ARGS"] = [str(tmp_path)]
    cache = Cache(app)

    backend = app.extensions["cache"][cache]
    assert type(backend) is cachelib.FileSystemCache
    assert backend._path == str(tmp_path)


def test_cachelib_backend_proxy_methods(app):
    app.config["CACHE_TYPE"] = "cachelib.SimpleCache"
    cache = Cache(app)

    with app.app_context():
        cache.set("hi", "hello")
        assert cache.get("hi") == "hello"
        assert cache.has("hi")

        cache.add("hi", "foobar")
        assert cache.get("hi") == "hello"

        cache.set_many({"a": 1, "b": 2})
        assert cache.get_many("a", "b") == [1, 2]

        cache.delete("hi")
        assert cache.get("hi") is None

        cache.clear()
        assert cache.get("a") is None


def test_cachelib_backend_with_cached_view(app):
    app.config["CACHE_TYPE"] = "cachelib.SimpleCache"
    cache = Cache(app)
    calls = []

    @app.route("/")
    @cache.cached()
    def view():
        calls.append(1)
        return "ok"

    client = app.test_client()
    assert client.get("/").data == b"ok"
    assert client.get("/").data == b"ok"
    assert len(calls) == 1


def test_cachelib_backend_with_memoize(app):
    app.config["CACHE_TYPE"] = "cachelib.SimpleCache"
    cache = Cache(app)
    calls = []

    @cache.memoize()
    def double(x):
        calls.append(x)
        return x * 2

    with app.app_context():
        assert double(2) == 4
        assert double(2) == 4
        assert len(calls) == 1

        cache.delete_memoized(double)
        assert double(2) == 4
        assert len(calls) == 2


def test_backend_uses_cachelib_serializer(app):
    """The backend holds a cachelib serializer that can be replaced."""
    cache = Cache(app)
    backend = app.extensions["cache"][cache]
    assert isinstance(backend.serializer, SimpleSerializer)

    class CountingSerializer(SimpleSerializer):
        def __init__(self):
            self.dumped = 0

        def dumps(self, value, protocol=None):
            self.dumped += 1
            return super().dumps(value)

    serializer = CountingSerializer()
    backend.serializer = serializer

    with app.app_context():
        cache.set("hi", "hello")
        assert cache.get("hi") == "hello"

    assert serializer.dumped == 1
