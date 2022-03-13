import errno
import os

import flask
import pytest

import flask_caching as fsc
from flask_caching.serialization import json, JSONError, pickle, PickleError

try:
    __import__("pytest_xprocess")
    from xprocess import ProcessStarter
except ImportError:

    @pytest.fixture(scope="session")
    def xprocess():
        pytest.skip("pytest-xprocess not installed.")


@pytest.fixture(params=[
    {},
    {'serializer_impl': pickle, 'serializer_error': PickleError},
    {'serializer_impl': json, 'serializer_error': JSONError}
])
def serialization_args(request):
    return request.param.copy()


@pytest.fixture(params=[
    {},
    {"CACHE_SERIALIZER": "pickle", "CACHE_SERIALIZER_ERROR": "PickleError"},
    {"CACHE_SERIALIZER": "json", "CACHE_SERIALIZER_ERROR": "JSONError"},
    {"CACHE_SERIALIZER": pickle, "CACHE_SERIALIZER_ERROR": PickleError},
    {"CACHE_SERIALIZER": json, "CACHE_SERIALIZER_ERROR": JSONError}
])
def app_serialization_args(request):
    return request.param.copy()


@pytest.fixture
def app(request, app_serialization_args):
    app = flask.Flask(
        request.module.__name__, template_folder=os.path.dirname(__file__)
    )
    app.testing = True
    app.config["CACHE_TYPE"] = "simple"
    app.config.update(app_serialization_args)
    return app


@pytest.fixture
def cache(app):
    return fsc.Cache(app)


@pytest.fixture(
    params=[method for method in fsc.SUPPORTED_HASH_FUNCTIONS],
    ids=[method.__name__ for method in fsc.SUPPORTED_HASH_FUNCTIONS],
)
def hash_method(request):
    return request.param


@pytest.fixture(scope="class")
def redis_server(xprocess):
    try:
        import redis  # noqa
    except ImportError:
        pytest.skip("Python package 'redis' is not installed.")

    class Starter(ProcessStarter):
        pattern = "[Rr]eady to accept connections"
        args = ["redis-server"]

    try:
        xprocess.ensure("redis_server", Starter)
    except OSError as e:
        # xprocess raises FileNotFoundError
        if e.errno == errno.ENOENT:
            pytest.skip("Redis is not installed.")
        else:
            raise

    yield
    xprocess.getinfo("redis_server").terminate()


@pytest.fixture(scope="class")
def memcache_server(xprocess):
    try:
        import pylibmc as memcache
    except ImportError:
        try:
            from google.appengine.api import memcache
        except ImportError:
            try:
                import memcache  # noqa
            except ImportError:
                pytest.skip(
                    "Python package for memcache is not installed. Need one of "
                    "pylibmc', 'google.appengine', or 'memcache'."
                )

    class Starter(ProcessStarter):
        pattern = ""
        args = ["memcached", "-vv"]

    try:
        xprocess.ensure("memcached", Starter)
    except OSError as e:
        # xprocess raises FileNotFoundError
        if e.errno == errno.ENOENT:
            pytest.skip("Memcached is not installed.")
        else:
            raise

    yield
    xprocess.getinfo("memcached").terminate()
