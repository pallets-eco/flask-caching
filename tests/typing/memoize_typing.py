"""Static typing regression tests, checked by mypy and pyright.

This module is never imported or executed - only type checked. The
annotated assignments fail the type checkers if the decorators stop
preserving signatures or stop binding ``self`` on methods.
"""

from collections.abc import Callable
from datetime import timedelta

from flask_caching import Cache

cache = Cache()


@cache.cached(timeout=1)
def cached_plain(a: int, b: str = "x") -> bytes:
    return b""


@cache.memoize(timeout=1)
def memoized_plain(a: int, b: str = "x") -> bytes:
    return b""


class Adder:
    def __init__(self, initial: int) -> None:
        self.initial = initial

    @cache.cached(timeout=1)
    def cached_add(self, b: int) -> int:
        return self.initial + b

    @cache.memoize(timeout=1)
    def memoized_add(self, b: int) -> int:
        return self.initial + b

    @classmethod
    @cache.memoize(timeout=1)
    def memoized_cls_add(cls, b: int) -> int:
        return b

    def call_through_self(self) -> int:
        return self.cached_add(1) + self.memoized_add(2)


adder = Adder(1)

plain_result: bytes = memoized_plain(1, "y")
plain_uncached: Callable[[int, str], bytes] = memoized_plain.uncached
plain_timeout: int | timedelta | None = memoized_plain.cache_timeout
plain_key: str = cached_plain.make_cache_key()
memoized_plain.delete_memoized()

# ``self`` is bound on instance access and kept on class access
memoized_bound: int = adder.memoized_add(2)
memoized_unbound: int = Adder.memoized_add(adder, 2)
memoized_bound_uncached: int = adder.memoized_add.uncached(adder, 2)
memoized_unbound_uncached: int = Adder.memoized_add.uncached(adder, 2)
adder.memoized_add.delete_memoized()

cached_bound: int = adder.cached_add(2)
cached_unbound: int = Adder.cached_add(adder, 2)
cached_bound_uncached: int = adder.cached_add.uncached(adder, 2)
cached_unbound_uncached: int = Adder.cached_add.uncached(adder, 2)

# every way a memoized function can be reached is accepted here
cache.delete_memoized(memoized_plain)
cache.delete_memoized(memoized_plain, 1, "y")
cache.delete_memoized(adder.memoized_add)
cache.delete_memoized(Adder.memoized_add, adder, 2)
cache.delete_memoized(Adder.memoized_cls_add, Adder)
cache.delete_memoized_verhash(memoized_plain)
cache.delete_memoized_verhash(adder.memoized_add)
