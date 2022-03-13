"""
    flask_caching.backends.rediscache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The redis caching backend.

    :copyright: (c) 2018 by Peter Justin.
    :copyright: (c) 2010 by Thadeus Burgess.
    :license: BSD, see LICENSE for more details.
"""
from flask_caching.backends.base import (
    BaseCache, extract_serializer_args, iteritems_wrapper
)


class RedisCache(BaseCache):
    """Uses the Redis key-value store as a cache backend.

    The first argument can be either a string denoting address of the Redis
    server or an object resembling an instance of a redis.Redis class.

    Note: Python Redis API already takes care of encoding unicode strings on
    the fly.

    :param host: address of the Redis server or an object which API is
                 compatible with the official Python Redis client (redis-py).
    :param port: port number on which Redis server listens for connections.
    :param password: password authentication for the Redis server.
    :param db: db (zero-based numeric index) on Redis Server to connect.
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`. A timeout of
                            0 indicates that the cache never expires.
    :param key_prefix: A prefix that should be added to all keys.

    Any additional keyword arguments will be passed to ``redis.Redis``.
    """

    def __init__(
        self,
        host="localhost",
        port=6379,
        password=None,
        db=0,
        default_timeout=300,
        key_prefix=None,
        **kwargs
    ):
        super().__init__(default_timeout, **extract_serializer_args(kwargs))
        if host is None:
            raise ValueError("RedisCache host parameter may not be None")
        if isinstance(host, str):
            try:
                import redis
            except ImportError:
                raise RuntimeError("no redis module found")
            if kwargs.get("decode_responses", None):
                raise ValueError("decode_responses is not supported by RedisCache.")
            client = redis.Redis(
                host=host, port=port, password=password, db=db, **kwargs
            )
        else:
            client = host

        self._write_client = self._read_clients = client
        self.key_prefix = key_prefix or ""

    @classmethod
    def factory(cls, app, config, args, kwargs):
        try:
            from redis import from_url as redis_from_url
        except ImportError:
            raise RuntimeError("no redis module found")

        kwargs.update(
            dict(
                host=config.get("CACHE_REDIS_HOST", "localhost"),
                port=config.get("CACHE_REDIS_PORT", 6379),
            )
        )
        password = config.get("CACHE_REDIS_PASSWORD")
        if password:
            kwargs["password"] = password

        key_prefix = config.get("CACHE_KEY_PREFIX")
        if key_prefix:
            kwargs["key_prefix"] = key_prefix

        db_number = config.get("CACHE_REDIS_DB")
        if db_number:
            kwargs["db"] = db_number

        redis_url = config.get("CACHE_REDIS_URL")
        if redis_url:
            kwargs["host"] = redis_from_url(redis_url, db=kwargs.pop("db", None))

        return cls(*args, **kwargs)

    def _get_prefix(self):
        return (
            self.key_prefix if isinstance(self.key_prefix, str) else self.key_prefix()
        )

    def _normalize_timeout(self, timeout):
        timeout = BaseCache._normalize_timeout(self, timeout)
        if timeout == 0:
            timeout = -1
        return timeout

    def dump_object(self, value):
        """Dumps an object into a string for redis.  By default it serializes
        integers as regular string and pickle dumps everything else.
        """
        t = type(value)
        if t == int:
            return str(value).encode("ascii")
        return b"!" + self._serializer.dumps(value)

    def load_object(self, value):
        """The reversal of :meth:`dump_object`.  This might be called with
        None.
        """
        if value is None:
            return None
        if value.startswith(b"!"):
            try:
                return self._serializer.loads(value[1:])
            except self._serialization_error:
                return None
        try:
            return int(value)
        except ValueError:
            # before 0.8 we did not have serialization.  Still support that.
            return value

    def get(self, key):
        return self.load_object(self._read_clients.get(self._get_prefix() + key))

    def get_many(self, *keys):
        if self.key_prefix:
            keys = [self._get_prefix() + key for key in keys]
        return [self.load_object(x) for x in self._read_clients.mget(keys)]

    def set(self, key, value, timeout=None):
        timeout = self._normalize_timeout(timeout)
        dump = self.dump_object(value)
        if timeout == -1:
            result = self._write_client.set(name=self._get_prefix() + key, value=dump)
        else:
            result = self._write_client.setex(
                name=self._get_prefix() + key, value=dump, time=timeout
            )
        return result

    def add(self, key, value, timeout=None):
        timeout = self._normalize_timeout(timeout)
        dump = self.dump_object(value)
        created = self._write_client.setnx(name=self._get_prefix() + key, value=dump)
        if created and timeout != -1:
            self._write_client.expire(name=self._get_prefix() + key, time=timeout)
        return created

    def set_many(self, mapping, timeout=None):
        timeout = self._normalize_timeout(timeout)
        # Use transaction=False to batch without calling redis MULTI
        # which is not supported by twemproxy
        pipe = self._write_client.pipeline(transaction=False)

        for key, value in iteritems_wrapper(mapping):
            dump = self.dump_object(value)
            if timeout == -1:
                pipe.set(name=self._get_prefix() + key, value=dump)
            else:
                pipe.setex(name=self._get_prefix() + key, value=dump, time=timeout)
        return pipe.execute()

    def delete(self, key):
        return self._write_client.delete(self._get_prefix() + key)

    def delete_many(self, *keys):
        if not keys:
            return
        if self.key_prefix:
            keys = [self._get_prefix() + key for key in keys]
        return self._write_client.delete(*keys)

    def has(self, key):
        return self._read_clients.exists(self._get_prefix() + key)

    def clear(self):
        status = False
        if self.key_prefix:
            keys = self._read_clients.keys(self._get_prefix() + "*")
            if keys:
                status = self._write_client.delete(*keys)
        else:
            status = self._write_client.flushdb(asynchronous=True)
        return status

    def inc(self, key, delta=1):
        return self._write_client.incr(name=self._get_prefix() + key, amount=delta)

    def dec(self, key, delta=1):
        return self._write_client.decr(name=self._get_prefix() + key, amount=delta)

    def unlink(self, *keys):
        """when redis-py >= 3.0.0 and redis > 4, support this operation"""
        if not keys:
            return
        if self.key_prefix:
            keys = [self.key_prefix + key for key in keys]

        unlink = getattr(self._write_client, "unlink", None)
        if unlink is not None and callable(unlink):
            return self._write_client.unlink(*keys)
        return self._write_client.delete(*keys)


class RedisSentinelCache(RedisCache):
    """Uses the Redis key-value store as a cache backend.

    The first argument can be either a string denoting address of the Redis
    server or an object resembling an instance of a redis.Redis class.

    Note: Python Redis API already takes care of encoding unicode strings on
    the fly.


    :param sentinels: A list or a tuple of Redis sentinel addresses.
    :param master: The name of the master server in a sentinel configuration.
    :param password: password authentication for the Redis server.
    :param db: db (zero-based numeric index) on Redis Server to connect.
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`. A timeout of
                            0 indicates that the cache never expires.
    :param key_prefix: A prefix that should be added to all keys.

    Any additional keyword arguments will be passed to
    ``redis.sentinel.Sentinel``.
    """

    def __init__(
        self,
        sentinels=None,
        master=None,
        password=None,
        db=0,
        default_timeout=300,
        key_prefix=None,
        **kwargs
    ):
        super().__init__(default_timeout=default_timeout)

        try:
            import redis.sentinel
        except ImportError:
            raise RuntimeError("no redis module found")

        if kwargs.get("decode_responses", None):
            raise ValueError("decode_responses is not supported by RedisCache.")

        sentinels = sentinels or [("127.0.0.1", 26379)]
        sentinel_kwargs = {
            key[9:]: value
            for key, value in kwargs.items()
            if key.startswith("sentinel_")
        }
        kwargs = {
            key[9:]: value
            for key, value in kwargs.items()
            if not key.startswith("sentinel_")
        }

        sentinel = redis.sentinel.Sentinel(
            sentinels=sentinels,
            password=password,
            db=db,
            sentinel_kwargs=sentinel_kwargs,
            **kwargs
        )

        self._write_client = sentinel.master_for(master)
        self._read_clients = sentinel.slave_for(master)

        self.key_prefix = key_prefix or ""

    @classmethod
    def factory(cls, app, config, args, kwargs):
        kwargs.update(
            dict(
                sentinels=config.get("CACHE_REDIS_SENTINELS", [("127.0.0.1", 26379)]),
                master=config.get("CACHE_REDIS_SENTINEL_MASTER", "mymaster"),
                password=config.get("CACHE_REDIS_PASSWORD", None),
                sentinel_password=config.get("CACHE_REDIS_SENTINEL_PASSWORD", None),
                key_prefix=config.get("CACHE_KEY_PREFIX", None),
                db=config.get("CACHE_REDIS_DB", 0),
            )
        )

        return cls(*args, **kwargs)


class RedisClusterCache(RedisCache):
    """Uses the Redis key-value store as a cache backend.

    The first argument can be either a string denoting address of the Redis
    server or an object resembling an instance of a rediscluster.RedisCluster
    class.

    Note: Python Redis API already takes care of encoding unicode strings on
    the fly.


    :param cluster: The redis cluster nodes address separated by comma.
                    e.g. host1:port1,host2:port2,host3:port3 .
    :param password: password authentication for the Redis server.
    :param default_timeout: the default timeout that is used if no timeout is
                            specified on :meth:`~BaseCache.set`. A timeout of
                            0 indicates that the cache never expires.
    :param key_prefix: A prefix that should be added to all keys.

    Any additional keyword arguments will be passed to
    ``rediscluster.RedisCluster``.
    """

    def __init__(
        self, cluster="", password="", default_timeout=300, key_prefix="", **kwargs
    ):
        super().__init__(default_timeout=default_timeout)

        if kwargs.get("decode_responses", None):
            raise ValueError("decode_responses is not supported by RedisCache.")

        try:
            from rediscluster import RedisCluster
        except ImportError:
            raise RuntimeError("no rediscluster module found")

        try:
            nodes = [(node.split(":")) for node in cluster.split(",")]
            startup_nodes = [
                {"host": node[0].strip(), "port": node[1].strip()} for node in nodes
            ]
        except IndexError:
            raise ValueError(
                "Please give the correct cluster argument "
                "e.g. host1:port1,host2:port2,host3:port3"
            )
        # Skips the check of cluster-require-full-coverage config,
        # useful for clusters without the CONFIG command (like aws)
        skip_full_coverage_check = kwargs.pop("skip_full_coverage_check", True)

        cluster = RedisCluster(
            startup_nodes=startup_nodes,
            password=password,
            skip_full_coverage_check=skip_full_coverage_check,
            **kwargs
        )
        self._write_client = self._read_clients = cluster
        self.key_prefix = key_prefix

    @classmethod
    def factory(cls, app, config, args, kwargs):
        kwargs.update(
            dict(
                cluster=config.get("CACHE_REDIS_CLUSTER", ""),
                password=config.get("CACHE_REDIS_PASSWORD", ""),
                default_timeout=config.get("CACHE_DEFAULT_TIMEOUT", 300),
                key_prefix=config.get("CACHE_KEY_PREFIX", ""),
            )
        )
        return cls(*args, **kwargs)
