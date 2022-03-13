"""
    tests.cache
    ~~~~~~~~~~~

    Tests the cache system

    :copyright: (c) 2014 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import time

import pytest

from flask_caching import backends

try:
    import redis
except ImportError:
    redis = None

try:
    import pylibmc as memcache
except ImportError:
    try:
        from google.appengine.api import memcache
    except ImportError:
        try:
            import memcache
        except ImportError:
            memcache = None


class CacheTestsBase:
    _can_use_fast_sleep = True
    _guaranteed_deletes = True

    @pytest.fixture
    def make_cache(self):
        """Return a cache class or factory."""
        raise NotImplementedError()

    @pytest.fixture
    def c(self, make_cache):
        """Return a cache instance."""
        return make_cache()


class GenericCacheTests(CacheTestsBase):
    def test_generic_get_dict(self, c):
        assert c.set("a", "a")
        assert c.set("b", "b")
        d = c.get_dict("a", "b")
        assert "a" in d
        assert "a" == d["a"]
        assert "b" in d
        assert "b" == d["b"]

    def test_generic_set_get(self, c):
        for i in range(3):
            assert c.set(str(i), i * i)

        for i in range(3):
            result = c.get(str(i))
            assert result == i * i, result

    def test_generic_get_set(self, c):
        assert c.set("foo", ["bar"])
        assert c.get("foo") == ["bar"]

    def test_generic_get_many(self, c):
        assert c.set("foo", ["bar"])
        assert c.set("spam", "eggs")
        assert c.get_many("foo", "spam") == [["bar"], "eggs"]

    def test_generic_set_many(self, c):
        assert c.set_many({"foo": "bar", "spam": ["eggs"]})
        assert c.get("foo") == "bar"
        assert c.get("spam") == ["eggs"]

    def test_generic_add(self, c):
        # sanity check that add() works like set()
        assert c.add("foo", "bar")
        assert c.get("foo") == "bar"
        assert not c.add("foo", "qux")
        assert c.get("foo") == "bar"

    def test_generic_delete(self, c):
        assert c.add("foo", "bar")
        assert c.get("foo") == "bar"
        assert c.delete("foo")
        assert c.get("foo") is None

    def test_generic_delete_many(self, c):
        assert c.add("foo", "bar")
        assert c.add("spam", "eggs")
        assert c.delete_many("foo", "spam")
        assert c.get("foo") is None
        assert c.get("spam") is None

    def test_generic_inc_dec(self, c):
        assert c.set("foo", 1)
        assert c.inc("foo") == c.get("foo") == 2
        assert c.dec("foo") == c.get("foo") == 1
        assert c.delete("foo")

    def test_generic_true_false(self, c):
        assert c.set("foo", True)
        assert c.get("foo") in (True, 1)
        assert c.set("bar", False)
        assert c.get("bar") in (False, 0)

    def test_generic_timeout(self, c):
        c.set("foo", "bar", 0)
        assert c.get("foo") == "bar"
        c.set("baz", "qux", 1)
        assert c.get("baz") == "qux"
        time.sleep(3)
        # timeout of zero means no timeout
        assert c.get("foo") == "bar"
        if self._guaranteed_deletes:
            assert c.get("baz") is None

    def test_generic_has(self, c):
        assert c.has("foo") in (False, 0)
        assert c.has("spam") in (False, 0)
        assert c.set("foo", "bar")
        assert c.has("foo") in (True, 1)
        assert c.has("spam") in (False, 0)
        c.delete("foo")
        assert c.has("foo") in (False, 0)
        assert c.has("spam") in (False, 0)


class TestSimpleCache(GenericCacheTests):
    @pytest.fixture
    def make_cache(self, serialization_args):
        return lambda: backends.SimpleCache(**serialization_args)

    def test_purge(self):
        c = backends.SimpleCache(threshold=2)
        c.set("a", "a")
        c.set("b", "b")
        c.set("c", "c")
        c.set("d", "d")
        # Cache purges old items *before* it sets new ones.
        assert len(c._cache) == 3


class TestFileSystemCache(GenericCacheTests):
    @pytest.fixture
    def make_cache(self, tmpdir, serialization_args):
        return lambda **kw: backends.FileSystemCache(
            cache_dir=str(tmpdir), **{**kw, **serialization_args}
        )

    def test_filesystemcache_hashes(self, make_cache, hash_method):
        cache = make_cache(hash_method=hash_method)
        self.test_count_file_accuracy(cache)

    def test_filesystemcache_prune(self, make_cache):
        THRESHOLD = 13
        c = make_cache(threshold=THRESHOLD)

        for i in range(2 * THRESHOLD):
            assert c.set(str(i), i)

        nof_cache_files = c.get(c._fs_count_file)
        assert nof_cache_files <= THRESHOLD

    def test_filesystemcache_clear(self, c):
        assert c.set("foo", "bar")
        nof_cache_files = c.get(c._fs_count_file)
        assert nof_cache_files == 1
        assert c.clear()
        nof_cache_files = c.get(c._fs_count_file)
        assert nof_cache_files == 0
        cache_files = c._list_dir()
        assert len(cache_files) == 0

    def test_no_threshold(self, make_cache):
        THRESHOLD = 0
        c = make_cache(threshold=THRESHOLD)

        for i in range(10):
            assert c.set(str(i), i)

        cache_files = c._list_dir()
        assert len(cache_files) == 10

        # File count is not maintained with threshold = 0
        nof_cache_files = c.get(c._fs_count_file)
        assert nof_cache_files is None

    def test_filecount_caching_none(self, make_cache):
        c = make_cache()
        for _ in range(3):
            assert c.set("a", None)
            assert c.get(c._fs_count_file) == 1

    def test_filecount_after_deletion_in_has(self, make_cache):
        c = make_cache()
        assert c.set("foo", "bar", timeout=0.01)
        assert c.get(c._fs_count_file) == 1
        time.sleep(0.1)
        assert c.has("foo") in (False, 0)
        assert c.get(c._fs_count_file) == 0

    def test_filecount_after_deletion_in_get(self, make_cache):
        c = make_cache()
        assert c.set("foo", "bar", timeout=0.01)
        assert c.get(c._fs_count_file) == 1
        time.sleep(0.1)
        assert c.get("foo") is None
        assert c.get(c._fs_count_file) == 0

    def test_count_file_accuracy(self, c):
        assert c.set("foo", "bar")
        assert c.set("moo", "car")
        c.add("moo", "tar")
        assert c.get(c._fs_count_file) == 2
        assert c.add("too", "far")
        assert c.get(c._fs_count_file) == 3
        assert c.delete("moo")
        assert c.get(c._fs_count_file) == 2
        assert c.clear()
        assert c.get(c._fs_count_file) == 0


# don't use pytest.mark.skipif on subclasses
# https://bitbucket.org/hpk42/pytest/issue/568
# skip happens in requirements fixture instead
class TestRedisCache(GenericCacheTests):
    _can_use_fast_sleep = False

    def gen_key_prefix(self):
        return "werkzeug-test-case:"

    @pytest.fixture(scope="class", autouse=True)
    def requirements(self, redis_server):
        pass

    @pytest.fixture(params=(None, False, True, gen_key_prefix))
    def make_cache(self, request, serialization_args):
        key_prefix = "werkzeug-test-case:"
        if request.param is None:
            host = "localhost"
        elif request.param:
            host = redis.StrictRedis()
        elif callable(request.param):
            key_prefix = gen_key_prefix  # noqa (flake8 error: undefined)
            host = redis.Redis()
        else:
            host = redis.Redis()

        c = backends.RedisCache(host=host, key_prefix=key_prefix, **serialization_args)
        yield lambda: c
        c.clear()

    def test_compat(self, c):
        assert c._write_client.set(c._get_prefix() + "foo", "Awesome")
        assert c.get("foo") == b"Awesome"
        assert c._write_client.set(c._get_prefix() + "foo", "42")
        assert c.get("foo") == 42

    def test_empty_host(self):
        with pytest.raises(ValueError) as exc_info:
            backends.RedisCache(host=None)
        assert str(exc_info.value) == "RedisCache host parameter may not be None"


class TestMemcachedCache(GenericCacheTests):
    _can_use_fast_sleep = False
    _guaranteed_deletes = False

    @pytest.fixture(scope="class", autouse=True)
    def requirements(self, memcache_server):
        pass

    @pytest.fixture
    def make_cache(self, serialization_args):
        c = backends.MemcachedCache(key_prefix="werkzeug-test-case:", **serialization_args)
        yield lambda: c
        c.clear()

    def test_compat(self, c):
        assert c._client.set(c.key_prefix + "foo", "bar")
        assert c.get("foo") == "bar"

    def test_huge_timeouts(self, c):
        # Timeouts greater than epoch are interpreted as POSIX timestamps
        # (i.e. not relative to now, but relative to epoch)
        epoch = 2592000
        c.set("foo", "bar", epoch + 100)
        assert c.get("foo") == "bar"

    def test_timeouts(self, c):
        c.set("foo", "bar", 1)
        assert c.get("foo") == "bar"
        time.sleep(1)
        assert c.has("foo") is False


class TestNullCache(CacheTestsBase):
    @pytest.fixture(scope="class", autouse=True)
    def make_cache(self):
        return backends.NullCache

    def test_has(self, c):
        assert not c.has("foo")
