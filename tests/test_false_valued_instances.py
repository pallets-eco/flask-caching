import pytest


class FalseBool:
    def __bool__(self):
        return False


class EmptyLength:
    def __len__(self):
        return 0


class AmbiguousBool:
    def __bool__(self):
        raise TypeError("This instance has no truth value")


@pytest.mark.parametrize("base", [FalseBool, EmptyLength, AmbiguousBool, object])
@pytest.mark.parametrize("operation", ["delete_memoized", "delete_memoized_verhash"])
def test_bound_method_invalidation_is_local_to_instance(cache, base, operation):
    class Counter(base):
        def __init__(self):
            self.calls = 0

        @cache.memoize()
        def value(self, argument):
            self.calls += 1
            return self.calls

    first, second = Counter(), Counter()
    for instance in (first, second):
        assert instance.value(10) == 1
        assert instance.value(20) == 2
        assert instance.value(10) == 1
        assert instance.calls == 2

    getattr(cache, operation)(first.value)

    assert first.value(10) == 3
    assert first.value(20) == 4
    assert second.value(10) == 1
    assert second.value(20) == 2
    assert first.calls == 4
    assert second.calls == 2
