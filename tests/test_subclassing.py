"""Tests that the decorators go through the public ``Cache`` API.

Third-party instrumentation (tracing, metrics) works by subclassing ``Cache``
and wrapping its public methods. Those wrappers only see the traffic caused by
``@cached``/``@memoize`` if the decorators call ``self.get()``/``self.set()``
rather than reaching into ``self.cache`` directly.
"""

import pytest

from flask_caching import Cache


class RecordingCache(Cache):
    """A ``Cache`` subclass that records the public methods it was asked for."""

    def __init__(self, *args, **kwargs):
        self.calls = []
        super().__init__(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.calls.append("get")
        return super().get(*args, **kwargs)

    def has(self, *args, **kwargs):
        self.calls.append("has")
        return super().has(*args, **kwargs)

    def set(self, *args, **kwargs):
        self.calls.append("set")
        return super().set(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.calls.append("delete")
        return super().delete(*args, **kwargs)

    def delete_many(self, *args, **kwargs):
        self.calls.append("delete_many")
        return super().delete_many(*args, **kwargs)

    def get_many(self, *args, **kwargs):
        self.calls.append("get_many")
        return super().get_many(*args, **kwargs)

    def set_many(self, *args, **kwargs):
        self.calls.append("set_many")
        return super().set_many(*args, **kwargs)


@pytest.fixture
def recording_cache(app):
    return RecordingCache(app)


def test_cached_uses_public_methods(app, recording_cache):
    @app.route("/")
    @recording_cache.cached()
    def cached_view():
        return "hello"

    tc = app.test_client()

    tc.get("/")
    assert recording_cache.calls == ["get", "set"]

    recording_cache.calls.clear()
    tc.get("/")
    assert recording_cache.calls == ["get"]


def test_cached_cache_none_uses_public_has(app, recording_cache):
    @app.route("/")
    @recording_cache.cached(cache_none=True)
    def cached_view():
        return "hello"

    tc = app.test_client()

    tc.get("/")
    assert recording_cache.calls == ["get", "has", "set"]


def test_memoize_uses_public_methods(app, recording_cache):
    with app.test_request_context():

        @recording_cache.memoize()
        def big_foo(a, b):
            return a + b

        big_foo(5, 2)
        assert recording_cache.calls == [
            "get_many",
            "set_many",
            "get",
            "set",
            "get_many",  # memoize version gets read
            "set_many",  # memoize version gets updated
        ]

        recording_cache.calls.clear()
        big_foo(5, 2)
        assert recording_cache.calls == ["get_many", "get"]


def test_delete_memoized_uses_public_delete(app, recording_cache):
    with app.test_request_context():

        @recording_cache.memoize()
        def big_foo(a, b):
            return a + b

        big_foo(5, 2)

        recording_cache.calls.clear()
        recording_cache.delete_memoized(big_foo, 5, 2)
        assert "delete" in recording_cache.calls


def test_delete_memoized_without_args_uses_public_set_many(app, recording_cache):
    with app.test_request_context():

        @recording_cache.memoize()
        def big_foo(a, b):
            return a + b

        big_foo(5, 2)

        recording_cache.calls.clear()
        recording_cache.delete_memoized(big_foo)
        assert "set_many" in recording_cache.calls


def test_delete_memoized_verhash_uses_public_delete_many(app, recording_cache):
    with app.test_request_context():

        @recording_cache.memoize()
        def big_foo(a, b):
            return a + b

        big_foo(5, 2)

        recording_cache.calls.clear()
        recording_cache.delete_memoized_verhash(big_foo)
        assert "delete_many" in recording_cache.calls


def test_subclass_overrides_still_cache_correctly(app, recording_cache):
    """The recording subclass must not change the caching behaviour itself."""
    with app.test_request_context():
        runs = []

        @recording_cache.memoize()
        def big_foo(a, b):
            runs.append((a, b))
            return a + b

        assert big_foo(5, 2) == 7
        assert big_foo(5, 2) == 7
        assert runs == [(5, 2)]
