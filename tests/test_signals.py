import contextlib

import pytest

from flask_caching import Cache
from flask_caching import cache_memoize_hit
from flask_caching import cache_memoize_miss
from flask_caching import cache_view_hit
from flask_caching import cache_view_miss

ALL_SIGNALS = (cache_view_hit, cache_view_miss, cache_memoize_hit, cache_memoize_miss)


@contextlib.contextmanager
def record_signals(*signals):
    """Connect a recorder to each signal and collect the payloads it receives.

    Yields a dict mapping each signal to the list of keyword payloads sent
    while the context manager is active.
    """
    recorded = {signal: [] for signal in signals}
    # blinker holds receivers weakly, so keep a reference to each one around
    receivers = []

    with contextlib.ExitStack() as stack:
        for signal in signals:

            def receiver(sender, _payloads=recorded[signal], **kwargs):
                _payloads.append(kwargs)

            receivers.append(receiver)
            stack.enter_context(signal.connected_to(receiver))

        yield recorded


@pytest.fixture
def signals_cache(app):
    app.config["CACHE_ENABLE_SIGNALS"] = True
    return Cache(app)


def test_signals_disabled_by_default(app, cache):
    @app.route("/")
    @cache.cached()
    def cached_view():
        return "hello"

    @cache.memoize()
    def add(a, b):
        return a + b

    with record_signals(*ALL_SIGNALS) as recorded:
        tc = app.test_client()
        tc.get("/")
        tc.get("/")
        add(1, 2)
        add(1, 2)

    assert all(payloads == [] for payloads in recorded.values())


def test_cached_view_sends_miss_then_hit(app, signals_cache):
    @app.route("/")
    @signals_cache.cached()
    def cached_view():
        return "hello"

    with record_signals(cache_view_miss, cache_view_hit) as recorded:
        tc = app.test_client()

        tc.get("/")
        assert len(recorded[cache_view_miss]) == 1
        assert recorded[cache_view_hit] == []

        tc.get("/")
        assert len(recorded[cache_view_miss]) == 1
        assert len(recorded[cache_view_hit]) == 1

    miss = recorded[cache_view_miss][0]
    hit = recorded[cache_view_hit][0]

    assert miss["cache"] is signals_cache
    assert hit["cache"] is signals_cache
    assert miss["cache_key"] == hit["cache_key"]
    assert miss["args"] == ()
    assert miss["kwargs"] == {}


def test_cached_view_signals_are_per_cache_key(app, signals_cache):
    @app.route("/<name>")
    @signals_cache.cached()
    def cached_view(name):
        return name

    with record_signals(cache_view_miss, cache_view_hit) as recorded:
        tc = app.test_client()
        tc.get("/foo")
        tc.get("/bar")
        tc.get("/foo")

    assert len(recorded[cache_view_miss]) == 2
    assert len(recorded[cache_view_hit]) == 1

    first_miss, second_miss = recorded[cache_view_miss]
    assert first_miss["cache_key"] != second_miss["cache_key"]
    assert recorded[cache_view_hit][0]["cache_key"] == first_miss["cache_key"]


def test_memoize_sends_miss_then_hit(app, signals_cache):
    @signals_cache.memoize()
    def add(a, b):
        return a + b

    with record_signals(cache_memoize_miss, cache_memoize_hit) as recorded:
        assert add(1, 2) == 3
        assert len(recorded[cache_memoize_miss]) == 1
        assert recorded[cache_memoize_hit] == []

        assert add(1, 2) == 3
        assert len(recorded[cache_memoize_miss]) == 1
        assert len(recorded[cache_memoize_hit]) == 1

    miss = recorded[cache_memoize_miss][0]
    hit = recorded[cache_memoize_hit][0]

    assert miss["cache"] is signals_cache
    assert miss["f"] is add.uncached
    assert hit["f"] is add.uncached
    assert miss["cache_key"] == hit["cache_key"]
    assert miss["args"] == (1, 2)
    assert miss["kwargs"] == {}


def test_memoize_sends_kwargs(app, signals_cache):
    @signals_cache.memoize()
    def add(a, b=0):
        return a + b

    with record_signals(cache_memoize_miss) as recorded:
        assert add(1, b=2) == 3

    miss = recorded[cache_memoize_miss][0]
    assert miss["args"] == (1,)
    assert miss["kwargs"] == {"b": 2}


def test_memoize_forced_update_sends_miss(app, signals_cache):
    forced = False

    @signals_cache.memoize(forced_update=lambda: forced)
    def add(a, b):
        return a + b

    add(1, 2)

    with record_signals(cache_memoize_miss, cache_memoize_hit) as recorded:
        add(1, 2)
        assert len(recorded[cache_memoize_hit]) == 1

        forced = True
        add(1, 2)
        assert len(recorded[cache_memoize_miss]) == 1
        assert len(recorded[cache_memoize_hit]) == 1


def test_signals_enabled_through_cache_config(app):
    cache = Cache(app, config={"CACHE_ENABLE_SIGNALS": True})

    @cache.memoize()
    def add(a, b):
        return a + b

    with record_signals(cache_memoize_miss) as recorded:
        add(1, 2)

    assert len(recorded[cache_memoize_miss]) == 1
