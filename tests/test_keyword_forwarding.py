import pytest

_KEYWORDS = [
    "fn",
    "f",
    "self",
    "unless",
    "forced_update",
    "is_stale",
    "rv",
    "args_to_ignore",
    "ordinary",
]


def _decorate(cache, kind, **options):
    if kind == "cached":
        return cache.cached(key_prefix="keyword-forwarding", **options)
    return cache.memoize(**options)


@pytest.mark.parametrize("kind", ["cached", "memoize"])
@pytest.mark.parametrize("keyword", _KEYWORDS)
def test_forward_helper_keyword_names(app, cache, kind, keyword):
    app.debug = True
    calls = []

    def value(**data):
        calls.append(data)
        return data

    decorated = _decorate(cache, kind)(value)
    with app.test_request_context():
        expected = {keyword: "hello"}
        assert decorated(**expected) == expected
        assert decorated(**expected) == expected
        assert calls == [expected]


@pytest.mark.parametrize("kind", ["cached", "memoize"])
def test_callbacks_receive_helper_keyword_names(app, cache, kind):
    app.debug = True
    expected = {keyword: keyword for keyword in _KEYWORDS}
    seen = {"unless": [], "forced_update": [], "is_stale": []}
    calls = []

    def unless(function, /, **data):
        assert function is value
        seen["unless"].append(data)
        return False

    def forced_update(**data):
        seen["forced_update"].append(data)
        return False

    def is_stale(result, /, **data):
        assert result == expected
        seen["is_stale"].append(data)
        return False

    def value(**data):
        calls.append(data)
        return data

    decorated = _decorate(
        cache, kind, unless=unless, forced_update=forced_update, is_stale=is_stale
    )(value)
    with app.test_request_context():
        assert decorated(**expected) == expected
        assert decorated(**expected) == expected
        assert calls == [expected]
        assert seen == {
            "unless": [expected, expected],
            "forced_update": [expected, expected],
            "is_stale": [expected],
        }


def test_memoize_separates_ignore_option_from_keyword_value(app, cache):
    app.debug = True
    calls = []

    @cache.memoize(args_to_ignore=["ignored"])
    def value(ignored, **data):
        calls.append(ignored)
        return data

    with app.test_request_context():
        assert value(1, args_to_ignore="first") == {"args_to_ignore": "first"}
        assert value(2, args_to_ignore="first") == {"args_to_ignore": "first"}
        assert value(3, args_to_ignore="second") == {"args_to_ignore": "second"}
        assert calls == [1, 3]


def test_delete_memoized_for_forwarded_keyword(app, cache):
    calls = []

    @cache.memoize()
    def value(fn):
        calls.append(fn)
        return len(calls), fn

    with app.test_request_context():
        assert value(fn="hello") == (1, "hello")
        assert value(fn="hello") == (1, "hello")
        cache.delete_memoized(value, fn="hello")
        assert value(fn="hello") == (2, "hello")
        assert calls == ["hello", "hello"]


def test_cached_view_forwards_fn_route_argument(app, cache):
    calls = []

    @app.get("/files/<fn>")
    @cache.cached()
    def view(fn):
        calls.append(fn)
        return f"{fn}:{len(calls)}"

    client = app.test_client()
    assert client.get("/files/first").get_data(as_text=True) == "first:1"
    assert client.get("/files/first").get_data(as_text=True) == "first:1"
    assert client.get("/files/second").get_data(as_text=True) == "second:2"
    assert calls == ["first", "second"]
