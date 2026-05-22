import importlib.util
import pathlib
from importlib.metadata import version as pkg_version

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

# pylibmc doesn't have any wheels for python > 3.11
pylibmc_available = False
try:
    importlib.util.find_spec("pylibmc")
except ImportError:
    pylibmc_available = False


cache_types = [
    FileSystemCache,
    MemcachedCache,
    NullCache,
    RedisCache,
    RedisSentinelCache,
    SimpleCache,
]

if pylibmc_available:
    cache_types.append(SASLMemcachedCache)
    cache_types.append(SpreadSASLMemcachedCache)


@pytest.fixture
def app():
    app_ = Flask(__name__)

    return app_


@pytest.mark.parametrize(
    "cache_type",
    (cache_types),
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


def test_docs_conf_version_not_hardcoded():
    """Regression test for issue #510.

    ``docs/conf.py`` must not hardcode the package version, otherwise
    Read the Docs renders "Flask-Caching 1.0.0 documentation" forever
    even after new releases. See
    https://github.com/pallets-eco/flask-caching/issues/510.

    The docs ``version``/``release`` should be derived from the
    installed package metadata via ``importlib.metadata.version``.

    This test only inspects the source of ``conf.py``; the full sphinx
    build (which would also exec ``conf.py`` end-to-end) lives in the
    docs build job since it pulls docs-only dependencies like
    ``alabaster``.
    """
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    conf_path = repo_root / "docs" / "conf.py"
    src = conf_path.read_text()
    # No hardcoded version string assignment.
    assert (
        'version = "1.0.0"' not in src
    ), "docs/conf.py still hardcodes version = '1.0.0'"
    assert (
        'release = "1.0.0"' not in src
    ), "docs/conf.py still hardcodes release = '1.0.0'"
    # version/release should be derived from importlib.metadata so the
    # docs always reflect the installed package version.
    assert "importlib.metadata" in src, (
        "docs/conf.py should derive version from importlib.metadata "
        "rather than hardcoding a literal"
    )
    # Sanity: the package can be located.
    assert pkg_version("Flask-Caching")
