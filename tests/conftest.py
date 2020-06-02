# -*- coding: utf-8 -*-
import errno
import os

import flask
import pytest

import flask_caching as fsc

# build the path to the uwsgi marker file
# when running in tox, this will be relative to the tox env
filename = os.path.join(
    os.environ.get("TOX_ENVTMPDIR", ""), "test_uwsgi_failed"
)

try:
    __import__("pytest_xprocess")
    from xprocess import ProcessStarter
except ImportError:

    @pytest.fixture(scope="session")
    def xprocess():
        pytest.skip("pytest-xprocess not installed.")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """``uwsgi --pyrun`` doesn't pass on the exit code when ``pytest`` fails,
    so Tox thinks the tests passed. For UWSGI tests, create a file to mark what
    tests fail. The uwsgi Tox env has a command to read this file and exit
    appropriately.
    """
    outcome = yield
    report = outcome.get_result()
    if item.cls != "TestUWSGICache":
        return

    if report.failed:
        with open(filename, "a") as f:
            f.write(item.name + "\n")


@pytest.fixture
def app(request):
    app = flask.Flask(
        request.module.__name__, template_folder=os.path.dirname(__file__)
    )
    app.testing = True
    app.config["CACHE_TYPE"] = "simple"
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
        import redis
    except ImportError:
        pytest.skip("Python package 'redis' is not installed.")

    class Starter(ProcessStarter):
        pattern = "[Rr]eady to accept connections"
        args = ["redis-server"]

    try:
        xprocess.ensure("redis_server", Starter)
    except IOError as e:
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
                import memcache
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
    except IOError as e:
        # xprocess raises FileNotFoundError
        if e.errno == errno.ENOENT:
            pytest.skip("Memcached is not installed.")
        else:
            raise

    yield
    xprocess.getinfo("memcached").terminate()

