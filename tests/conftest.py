import os
import shutil
import socket
import subprocess

import cachelib.file
import cachelib.simple
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


class _Clock:
    def __init__(self, now):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock(monkeypatch):
    # cachelib does ``from time import time``, so the module attribute has to
    # be replaced
    fake = _Clock(1_700_000_000.0)
    monkeypatch.setattr(cachelib.simple, "time", fake)
    monkeypatch.setattr(cachelib.file, "time", fake)
    return fake


@pytest.fixture(
    params=[method for method in fsc.SUPPORTED_HASH_FUNCTIONS],
    ids=[method.__name__ for method in fsc.SUPPORTED_HASH_FUNCTIONS],
)
def hash_method(request):
    return request.param


def _server_is_running(port):
    with socket.socket() as sock:
        sock.settimeout(1)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _ensure_server(xprocess, name, executable, port, starter):
    if _server_is_running(port):
        yield
        return

    if os.environ.get("CI", "false") == "true":
        pytest.fail(f"no {executable} server listening on port {port}")

    if shutil.which(executable) is None:
        pytest.skip(f"could not find {executable} executable")

    try:
        xprocess.ensure(name, starter)
    except (OSError, RuntimeError) as exc:
        pytest.skip(f"could not start {executable}: {exc}")

    yield
    xprocess.getinfo(name).terminate()


@pytest.fixture(scope="class")
def redis_server(xprocess):
    package_name = "redis"
    pytest.importorskip(
        modname=package_name, reason=f"could not find python package {package_name}"
    )

    class Starter(ProcessStarter):
        timeout = 20
        pattern = "[Rr]eady to accept connections"
        args = ["redis-server", "--port 6360"]

        def startup_check(self):
            out = subprocess.run(
                ["redis-cli", "-p", "6360", "ping"], stdout=subprocess.PIPE
            )
            return out.stdout == b"PONG\n"

    yield from _ensure_server(xprocess, package_name, "redis-server", 6360, Starter)


@pytest.fixture(scope="class")
def memcache_server(xprocess):
    package_name = "pylibmc"
    pytest.importorskip(
        modname=package_name, reason=f"could not find python package {package_name}"
    )

    class Starter(ProcessStarter):
        timeout = 20
        pattern = "server listening"
        args = ["memcached", "-vv", "-p", "11212"]

        def startup_check(self):
            out = subprocess.run(["memcached", "-p", "11212"], stderr=subprocess.PIPE)
            return b"Address already" in out.stderr

    yield from _ensure_server(xprocess, package_name, "memcached", 11212, Starter)
