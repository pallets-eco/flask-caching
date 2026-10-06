import itertools

import pytest


def unless_with_optional_kwarg(*, enabled=False):
    return enabled


def forced_update_with_optional_kwarg(*, enabled=False):
    return enabled


def is_stale_with_optional_kwarg(value, *, enabled=False):
    return enabled


OPTIONAL_KWARG_CALLBACKS = [
    ("unless", unless_with_optional_kwarg),
    ("forced_update", forced_update_with_optional_kwarg),
    ("is_stale", is_stale_with_optional_kwarg),
]


@pytest.mark.parametrize("decorator_name", ["cached", "memoize"])
@pytest.mark.parametrize("callback_name", ["forced_update", "is_stale"])
def test_required_keyword_only_callbacks_receive_view_args(
    app, cache, decorator_name, callback_name
):
    app.debug = True
    counter = itertools.count()
    calls = []

    if callback_name == "forced_update":

        def callback(*, item_id):
            calls.append(item_id)
            return item_id == "refresh"

    else:

        def callback(value, *, item_id):
            calls.append(item_id)
            return item_id == "refresh"

    @app.route("/<item_id>")
    @getattr(cache, decorator_name)(**{callback_name: callback})
    def view(*, item_id):
        return f"{item_id}:{next(counter)}"

    client = app.test_client()
    assert client.get("/cached").data == b"cached:0"
    assert client.get("/cached").data == b"cached:0"
    assert client.get("/refresh").data == b"refresh:1"
    assert client.get("/refresh").data == b"refresh:2"
    assert "cached" in calls
    assert "refresh" in calls


@pytest.mark.parametrize("decorator_name", ["cached", "memoize"])
@pytest.mark.parametrize("callback_name, callback", OPTIONAL_KWARG_CALLBACKS)
def test_optional_keyword_only_callbacks_on_view(
    app, cache, decorator_name, callback_name, callback
):
    app.debug = True
    counter = itertools.count()

    @app.route("/<item_id>")
    @getattr(cache, decorator_name)(**{callback_name: callback})
    def view(item_id):
        return f"{item_id}:{next(counter)}"

    client = app.test_client()
    assert client.get("/a").data == b"a:0"
    assert client.get("/a").data == b"a:0"


@pytest.mark.parametrize("callback_name, callback", OPTIONAL_KWARG_CALLBACKS)
def test_optional_keyword_only_callbacks_on_memoized_function(
    app, cache, callback_name, callback
):
    app.debug = True
    counter = itertools.count()

    @cache.memoize(**{callback_name: callback})
    def add(a, b):
        return a + b + next(counter)

    with app.test_request_context():
        assert add(1, 2) == 3
        assert add(1, 2) == 3
