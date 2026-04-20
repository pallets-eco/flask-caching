"""Regression tests for issue #636.

On Python 3.14+, ``inspect.signature`` and ``inspect.getfullargspec`` eagerly
evaluate annotations via PEP 649's ``__annotate__``. Functions whose
annotations reference names defined only under ``if TYPE_CHECKING:`` must
still be memoizable / cacheable.
"""

import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:

    class TypeCheckingOnly:
        pass


pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 14),
    reason="requires Python 3.14 __annotate__ / PEP 649 behavior",
)


def test_memoize_with_type_checking_annotation(cache):
    @cache.memoize(60)
    def fetch(x: int) -> TypeCheckingOnly:
        return x * 2

    assert fetch(3) == 6
    # Cache-hit path also goes through get_function_parameters.
    assert fetch(3) == 6


def test_cached_with_type_checking_annotation(app, cache):
    @app.route("/py314-annot")
    @cache.cached(60)
    def view(extra: TypeCheckingOnly = None):
        return "ok"

    client = app.test_client()
    assert client.get("/py314-annot").data == b"ok"
    assert client.get("/py314-annot").data == b"ok"


def test_memoize_unless_with_type_checking_annotation(cache):
    def skip(*args, **kwargs) -> TypeCheckingOnly:
        return False

    @cache.memoize(60, unless=skip)
    def fetch(x: int) -> TypeCheckingOnly:
        return x + 1

    assert fetch(1) == 2
