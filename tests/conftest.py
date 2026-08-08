import os
import subprocess

import flask
import pytest
from xprocess import ProcessStarter

import flask_caching as fsc


@pytest.fixture
def app(request):
    app = flask.Flask(
        request.module.__name__, template_folder=os.path.dirname(__file__)
    )
    app.testing = True
    app.config["CACHE_TYPE"] = "SimpleCache"
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
    package_name = "redis"
    pytest.importorskip(
        modname=package_name, reason=f"could not find python package {package_name}"
    )

    if os.environ.get("CI", "false") == "true":
        yield
        return

    class Starter(ProcessStarter):
        pattern = "[Rr]eady to accept connections"
        args = ["redis-server", "--port 6360"]

        def startup_check(self):
            out = subprocess.run(
                ["redis-cli", "-p", "6360", "ping"], stdout=subprocess.PIPE
            )
            return out.stdout == b"PONG\n"

    xprocess.ensure(package_name, Starter)
    yield
    xprocess.getinfo(package_name).terminate()


@pytest.fixture(scope="class")
def memcache_server(xprocess):
    package_name = "pylibmc"
    pytest.importorskip(
        modname=package_name, reason=f"could not find python package {package_name}"
    )

    if os.environ.get("CI", "false") == "true":
        yield
        return

    class Starter(ProcessStarter):
        pattern = "server listening"
        args = ["memcached", "-vv", "-p", "11212"]

        def startup_check(self):
            out = subprocess.run(["memcached", "-p", "11212"], stderr=subprocess.PIPE)
            return b"Address already" in out.stderr

    xprocess.ensure(package_name, Starter)
    yield
    xprocess.getinfo(package_name).terminate()
