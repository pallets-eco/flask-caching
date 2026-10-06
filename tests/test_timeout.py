import itertools
from datetime import timedelta

import pytest
from flask import make_response
from flask import render_template_string

from flask_caching import Cache
from flask_caching import CachedResponse
from flask_caching.utils import normalize_timeout


@pytest.mark.parametrize(
    ("timeout", "expected"),
    [
        (timedelta(seconds=30), 30),
        (timedelta(minutes=5), 300),
        (timedelta(days=1), 86400),
        (timedelta(0), 0),
        # Rounded up, a timeout of 0 would mean "never expires".
        (timedelta(milliseconds=1), 1),
        (timedelta(seconds=1.5), 2),
        (30, 30),
        (0, 0),
        (None, None),
    ],
)
def test_normalize_timeout(timeout, expected):
    assert normalize_timeout(timeout) == expected


def test_default_timeout_config_timedelta(app):
    app.config["CACHE_DEFAULT_TIMEOUT"] = timedelta(minutes=2)
    cache = Cache(app)

    assert cache.cache.default_timeout == 120


def test_cache_options_default_timeout_timedelta(app):
    app.config["CACHE_OPTIONS"] = {"default_timeout": timedelta(minutes=2)}
    cache = Cache(app)

    assert cache.cache.default_timeout == 120


def test_cached_timedelta(app, cache, clock):
    counter = itertools.count()

    @app.route("/")
    @cache.cached(timedelta(seconds=30))
    def view():
        return str(next(counter))

    tc = app.test_client()
    first = tc.get("/").data

    clock.advance(29)
    assert tc.get("/").data == first

    clock.advance(2)
    assert tc.get("/").data != first


def test_cached_timedelta_written_to_cache_timeout(app, cache, clock):
    counter = itertools.count()

    @app.route("/")
    @cache.cached(1)
    def view():
        return str(next(counter))

    view.cache_timeout = timedelta(seconds=30)

    tc = app.test_client()
    first = tc.get("/").data

    clock.advance(29)
    assert tc.get("/").data == first

    clock.advance(2)
    assert tc.get("/").data != first


def test_cached_response_timedelta(app, cache, clock):
    counter = itertools.count()

    @app.route("/")
    @cache.cached(1)
    def view():
        return CachedResponse(
            make_response(str(next(counter))), timeout=timedelta(seconds=30)
        )

    tc = app.test_client()
    first = tc.get("/").data

    clock.advance(29)
    assert tc.get("/").data == first

    clock.advance(2)
    assert tc.get("/").data != first


def test_cached_response_normalizes_timeout(app):
    with app.test_request_context():
        response = CachedResponse(make_response("hi"), timedelta(minutes=1))

    assert response.timeout == 60


def test_memoize_timedelta(app, cache, clock):
    with app.test_request_context():
        runs = []

        @cache.memoize(timedelta(minutes=1))
        def f(param):
            runs.append(param)
            return param.upper()

        assert f("icecream") == "ICECREAM"

        clock.advance(59)
        assert f("icecream") == "ICECREAM"
        assert runs == ["icecream"]

        clock.advance(2)
        assert f("icecream") == "ICECREAM"
        assert runs == ["icecream", "icecream"]


def test_jinjaext_cache_timedelta(app, cache, clock):
    template = """{% cache timeout, "fragment" %}{{ somevar }}{% endcache %}"""

    with app.test_request_context():
        assert (
            render_template_string(
                template, somevar="first", timeout=timedelta(seconds=30)
            )
            == "first"
        )

        clock.advance(29)
        assert (
            render_template_string(
                template, somevar="second", timeout=timedelta(seconds=30)
            )
            == "first"
        )

        clock.advance(2)
        assert (
            render_template_string(
                template, somevar="second", timeout=timedelta(seconds=30)
            )
            == "second"
        )
