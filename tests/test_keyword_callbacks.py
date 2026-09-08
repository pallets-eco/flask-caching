import itertools

import pytest


@pytest.mark.parametrize("decorator_name", ["cached", "memoize"])
@pytest.mark.parametrize("callback_name", ["forced_update", "is_stale"])
def test_keyword_only_refresh_callbacks(app, cache, decorator_name, callback_name):
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
