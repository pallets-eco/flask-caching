import hashlib
import random

import pytest

from flask_caching import Cache


def _query_string_key(path, args_as_sorted_tuple, hash_method):
    """Rebuild the key that ``cached(query_string=True)`` produces."""
    return path + hash_method(str(args_as_sorted_tuple).encode()).hexdigest()


def test_default_hash_method_is_sha256(app):
    cache = Cache(app)

    @app.route("/works")
    @cache.cached(query_string=True)
    def view():
        return "value"

    with app.test_request_context("/works?a=1&b=2"):
        assert view.make_cache_key() == _query_string_key(
            "/works", (("a", "1"), ("b", "2")), hashlib.sha256
        )


def test_cached_uses_configured_hash_method(app):
    app.config["CACHE_HASH_METHOD"] = hashlib.md5
    cache = Cache(app)

    @app.route("/works")
    @cache.cached(query_string=True)
    def view():
        return "value"

    with app.test_request_context("/works?a=1&b=2"):
        assert view.make_cache_key() == _query_string_key(
            "/works", (("a", "1"), ("b", "2")), hashlib.md5
        )


def test_decorator_argument_overrides_configured_hash_method(app):
    app.config["CACHE_HASH_METHOD"] = hashlib.md5
    cache = Cache(app)

    @app.route("/works")
    @cache.cached(query_string=True, hash_method=hashlib.sha512)
    def view():
        return "value"

    with app.test_request_context("/works?a=1&b=2"):
        assert view.make_cache_key() == _query_string_key(
            "/works", (("a", "1"), ("b", "2")), hashlib.sha512
        )


def test_hash_method_read_from_extension_config(app):
    """The option also works when passed to ``Cache`` instead of ``app``."""
    cache = Cache(app, config={"CACHE_HASH_METHOD": hashlib.md5})

    @app.route("/works")
    @cache.cached(query_string=True)
    def view():
        return "value"

    with app.test_request_context("/works?a=1&b=2"):
        assert view.make_cache_key() == _query_string_key(
            "/works", (("a", "1"), ("b", "2")), hashlib.md5
        )


def test_non_callable_hash_method_raises(app):
    app.config["CACHE_HASH_METHOD"] = "sha256"

    with pytest.raises(ValueError, match="CACHE_HASH_METHOD"):
        Cache(app)


def test_hash_method_resolved_after_decoration(app):
    """Decorators run at import time, before ``init_app``.

    The configured hash method must therefore be picked up when the key is
    built, not when the decorator is applied.
    """
    cache = Cache()

    @cache.cached(query_string=True)
    def view():
        return "value"

    app.config["CACHE_HASH_METHOD"] = hashlib.md5
    cache.init_app(app)

    with app.test_request_context("/works?a=1&b=2"):
        assert view.make_cache_key() == _query_string_key(
            "/works", (("a", "1"), ("b", "2")), hashlib.md5
        )


def test_delete_memoized_matches_configured_hash_method(app):
    """``make_cache_key`` is built at decoration time and must agree with the
    key used at call time, otherwise ``delete_memoized`` deletes nothing."""
    app.config["CACHE_HASH_METHOD"] = hashlib.md5
    cache = Cache(app)

    @cache.memoize(50)
    def add(a, b):
        return a + b + random.random()

    with app.test_request_context():
        result = add(1, 2)
        assert add(1, 2) == result

        cache.delete_memoized(add, 1, 2)

        assert add(1, 2) != result


def test_configured_hash_method_changes_memoize_key(app):
    app.config["CACHE_HASH_METHOD"] = hashlib.md5
    md5_cache = Cache(app)

    @md5_cache.memoize(50)
    def add(a, b):
        return a + b

    with app.test_request_context():
        md5_key = add.make_cache_key(add.uncached, 1, 2)
        # Swap the configured method on the same cache so that the version
        # hash stays identical and only the digest can differ.
        md5_cache.hash_method = hashlib.sha512
        assert add.make_cache_key(add.uncached, 1, 2) != md5_key


def test_file_hash_method_is_independent(app, tmp_path):
    """``CACHE_HASH_METHOD`` must not change the FileSystemCache file names."""
    app.config.update(
        CACHE_TYPE="FileSystemCache",
        CACHE_DIR=str(tmp_path),
        CACHE_HASH_METHOD=hashlib.md5,
    )
    cache = Cache(app)

    with app.test_request_context():
        assert cache.cache._hash_method is hashlib.sha256
