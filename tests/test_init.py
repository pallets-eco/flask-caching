import pytest
from flask import Flask

from flask_caching import Cache
from flask_caching.backends import FileSystemCache
from flask_caching.backends import MemcachedCache
from flask_caching.backends import NullCache
from flask_caching.backends import RedisCache
from flask_caching.backends import RedisSentinelCache
from flask_caching.backends import SASLMemcachedCache
from flask_caching.backends import SimpleCache
from flask_caching.backends import SpreadSASLMemcachedCache


@pytest.fixture
def app():
    app_ = Flask(__name__)

    return app_


@pytest.mark.parametrize(
    "cache_type",
    (
        FileSystemCache,
        MemcachedCache,
        NullCache,
        RedisCache,
        RedisSentinelCache,
        SASLMemcachedCache,
        SimpleCache,
        SpreadSASLMemcachedCache,
    ),
)
def test_init_nullcache(cache_type, app, tmp_path):
    extra_config = {
        FileSystemCache: {
            "CACHE_DIR": tmp_path,
        },
        SASLMemcachedCache: {
            "CACHE_MEMCACHED_USERNAME": "test",
            "CACHE_MEMCACHED_PASSWORD": "test",
        },
    }
    app.config["CACHE_TYPE"] = "flask_caching.backends." + cache_type.__name__
    app.config.update(extra_config.get(cache_type, {}))
    cache = Cache(app=app)

    assert isinstance(app.extensions["cache"][cache], cache_type)


@pytest.mark.parametrize(
    "short_name, expected_type",
    (
        ("null", NullCache),
        ("simple", SimpleCache),
        ("filesystem", FileSystemCache),
        ("redis", RedisCache),
        ("redissentinel", RedisSentinelCache),
        ("saslmemcached", SASLMemcachedCache),
        ("spreadsaslmemcached", SpreadSASLMemcachedCache),
    ),
)
def test_short_names_no_deprecation_warning(short_name, expected_type, app, tmp_path):
    """Short CACHE_TYPE names should resolve to classes without DeprecationWarning."""
    import warnings

    extra_config = {
        "filesystem": {
            "CACHE_DIR": tmp_path,
        },
        "saslmemcached": {
            "CACHE_MEMCACHED_USERNAME": "test",
            "CACHE_MEMCACHED_PASSWORD": "test",
        },
    }
    app.config["CACHE_TYPE"] = short_name
    app.config["CACHE_NO_NULL_WARNING"] = True
    app.config.update(extra_config.get(short_name, {}))

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cache = Cache(app=app)

    deprecation_warnings = [
        x for x in w if issubclass(x.category, DeprecationWarning)
    ]
    assert len(deprecation_warnings) == 0, (
        f"Unexpected DeprecationWarning for CACHE_TYPE='{short_name}': "
        f"{[str(x.message) for x in deprecation_warnings]}"
    )
    assert isinstance(app.extensions["cache"][cache], expected_type)
