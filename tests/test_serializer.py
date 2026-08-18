"""Tests for the ``CACHE_SERIALIZER`` configuration option.

Every cachelib backed backend holds a ``serializer`` instance that turns
values into bytes before they reach the store. ``CACHE_SERIALIZER`` replaces
it for the backend Flask-Caching builds.
"""

import pytest
from cachelib.serializers import JSONSerializer
from cachelib.serializers import SimpleSerializer

from flask_caching import Cache


class CountingSerializer(SimpleSerializer):
    def __init__(self):
        self.dumped = 0
        self.loaded = 0

    def dumps(self, value, protocol=None):
        self.dumped += 1
        return super().dumps(value)

    def loads(self, bvalue):
        self.loaded += 1
        return super().loads(bvalue)


class NeedsArguments(SimpleSerializer):
    def __init__(self, protocol):
        self.protocol = protocol


def test_default_keeps_the_cachelib_serializer(app):
    cache = Cache(app)

    assert isinstance(app.extensions["cache"][cache].serializer, SimpleSerializer)


def test_instance_is_used_as_is(app):
    serializer = JSONSerializer()
    app.config["CACHE_SERIALIZER"] = serializer
    cache = Cache(app)

    assert app.extensions["cache"][cache].serializer is serializer


def test_class_is_instantiated(app):
    app.config["CACHE_SERIALIZER"] = JSONSerializer
    cache = Cache(app)

    assert isinstance(app.extensions["cache"][cache].serializer, JSONSerializer)


def test_serializer_read_from_extension_config(app):
    cache = Cache(app, config={"CACHE_SERIALIZER": JSONSerializer})

    assert isinstance(app.extensions["cache"][cache].serializer, JSONSerializer)


def test_configured_serializer_is_used_for_get_and_set(app):
    serializer = CountingSerializer()
    app.config["CACHE_SERIALIZER"] = serializer
    cache = Cache(app)

    with app.app_context():
        cache.set("hi", "hello")
        assert cache.get("hi") == "hello"

    assert serializer.dumped == 1
    assert serializer.loaded == 1


def test_values_are_stored_in_the_configured_format(app):
    app.config["CACHE_SERIALIZER"] = JSONSerializer
    cache = Cache(app)

    with app.app_context():
        cache.set("hi", {"a": 1})
        assert cache.cache._cache["hi"][1] == b'{"a": 1}'
        assert cache.get("hi") == {"a": 1}


def test_cachelib_cache_type_gets_the_serializer(app):
    app.config["CACHE_TYPE"] = "cachelib.SimpleCache"
    app.config["CACHE_SERIALIZER"] = JSONSerializer
    cache = Cache(app)

    assert isinstance(app.extensions["cache"][cache].serializer, JSONSerializer)


def test_backend_without_serializer_warns(app):
    app.config.update(
        CACHE_TYPE="NullCache",
        CACHE_NO_NULL_WARNING=True,
        CACHE_SERIALIZER=JSONSerializer,
    )

    with pytest.warns(UserWarning, match="CACHE_SERIALIZER"):
        Cache(app)


def test_string_serializer_raises(app):
    app.config["CACHE_SERIALIZER"] = "json"

    with pytest.raises(ValueError, match="CACHE_SERIALIZER"):
        Cache(app)


def test_non_cachelib_serializer_raises(app):
    class DuckTyped:
        def dumps(self, value):
            return b""

        def loads(self, bvalue):
            return None

    app.config["CACHE_SERIALIZER"] = DuckTyped()

    with pytest.raises(ValueError, match="BaseSerializer"):
        Cache(app)


def test_non_cachelib_serializer_class_raises(app):
    class DuckTyped:
        def dumps(self, value):
            return b""

        def loads(self, bvalue):
            return None

    app.config["CACHE_SERIALIZER"] = DuckTyped

    with pytest.raises(ValueError, match="BaseSerializer"):
        Cache(app)


def test_serializer_class_needing_arguments_raises(app):
    app.config["CACHE_SERIALIZER"] = NeedsArguments

    with pytest.raises(ValueError, match="already created instance"):
        Cache(app)


def test_serializer_is_rejected_before_the_backend_is_built(app):
    app.config["CACHE_TYPE"] = "flask_caching.backends.RedisCache"
    app.config["CACHE_SERIALIZER"] = "json"

    with pytest.raises(ValueError, match="CACHE_SERIALIZER"):
        Cache(app)

    assert "cache" not in app.extensions
