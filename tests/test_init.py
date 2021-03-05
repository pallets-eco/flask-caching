import pytest
from flask import Flask

from flask_caching import Cache


@pytest.fixture
def app():
    app_ = Flask(__name__)

    return app_


@pytest.mark.parametrize(
    "cache_type",
    (
            "filesystem",
            "memcached",
            "null",
            "redis",
            "redissentinel",
            "simple",
            "saslmemcached",
            "spreadsaslmemcached"
    ),
)
def test_init_nullcache(cache_type, app, tmp_path):
    extra_config = {
        "filesystem": {
            "CACHE_DIR": tmp_path,
        },
        "saslmemcached": {
            "CACHE_MEMCACHED_USERNAME": "test",
            "CACHE_MEMCACHED_PASSWORD": "test",
        },
    }
    app.config["CACHE_TYPE"] = cache_type
    app.config.update(extra_config.get(cache_type, {}))
    cache = Cache(app=app)
    assert app.extensions["cache"][cache]
