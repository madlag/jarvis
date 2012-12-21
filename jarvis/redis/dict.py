import json
import types

from redis.client import Redis

from jarvis.redis.base import RedisBase


class RedisHashDict(RedisBase):
    """
    Dict-like object on top of a Redis hash.
    """

    def __init__(self, client, name, load=None, dump=None):
        super(RedisHashDict, self).__init__(client, load=load, dump=dump)
        self.name = name

    def __getitem__(self, key):
        ret = self.raw_get(key)
        if ret is None:
            raise KeyError(key)
        return self.load_value(ret)

    def __setitem__(self, key, value):
        value = self.dump_value(value)
        self.client.hset(self.name, key, value)

    def raw_delete(self, key):
        return self.client.hdel(self.name, key)

    def __delitem__(self, key):
        if not self.raw_delete(key):
            raise KeyError(key)

    def __len__(self):
        return self.client.hlen(self.name)

    def __contains__(self, key):
        return self.client.hexists(self.name, key)

    def __iter__(self):
        return iter(self.keys())

    def keys(self):
        return self.client.hkeys(self.name)

    def values(self):
        return [self.load_value(v) for v in self.raw_values()]

    def raw_values(self):
        return self.client.hvals(self.name)

    def items(self):
        return [(k, self.load_value(v)) for k, v in self.raw_items().items()]

    def update(self, mapping):
        values = dict((k, self.dump_value(v)) for k, v in mapping.items())
        self.client.hmset(self.name, values)

    def setnx(self, key, value):
        """
        Set *key* with *value*, only if it doesn't exist.

        Return a boolean indicating if the key was modified.
        """
        return self.client.hsetnx(self.name, key, self.dump_value(value))

    def raw_items(self):
        """
        Retrieve raw key/value pairs (usefull in transactions).
        """
        return self.client.hgetall(self.name)

    def get(self, key, default=None):
        ret = self.raw_get(key)
        if ret is None:
            return default
        return self.load_value(ret)

    def raw_get(self, key):
        return self.client.hget(self.name, key)

    def getall(self, keys):
        """
        Get all values paired with the list of keys *keys*.
        """
        return [self.load_value(v) for v in self.raw_getall(keys)]

    def raw_getall(self, keys):
        return self.client.hmget(self.name, keys)


class RedisDict(RedisBase):
    """
    Dict-like object on top of Redis keys.

    The optional *ttl* parameter allows to specify a time-to-live for
    keys created with this object. If *ttl* is an integer then the Redis
    EXPIRE command is used; if it is a float the PEXPIRE command is used. In
    all cases *ttl* is specified in seconds.

    *prefix* may be a string defining the prefix of the keys. The default is
    no prefix, meaning the dict spans all the keys in the database.
    """

    def __init__(self, client, ttl=None, prefix='', load=None, dump=None):
        if not isinstance(ttl, (types.NoneType, int, float)):
            raise TypeError('ttl must be None, an int or a float')
        super(RedisDict, self).__init__(client, load=load, dump=dump)
        self._ttl = ttl
        self.prefix = prefix

    def __getitem__(self, key):
        key = self.raw_key(key)
        ret = self.client.get(key)
        if ret is None:
            raise KeyError(key)
        return self.load_value(ret)

    def __setitem__(self, key, value):
        key = self.raw_key(key)
        value = self.dump_value(value)
        if self._ttl is None:
            self.client.set(key, value)
        else:
            if isinstance(self._ttl, int):
                duration = self._ttl
                func = self.client.setex
            elif isinstance(self._ttl, float):
                duration = int(self._ttl) * 1000
                func = self.client.psetex
            if isinstance(self.client, Redis):
                func(key, value, duration)
            else:
                func(key, duration, value)

    def __delitem__(self, key):
        key = self.raw_key(key)
        self.client.delete(key)

    def setnx(self, key, value):
        """
        Set *key* with value, only if *key* does not exist.

        Returns a boolean indicating if the key was created.

        .. warning:: this method does **NOT** set an expiration time on the
                     created key.
        """
        key = self.raw_key(key)
        value = self.dump_value(value)
        return self.client.setnx(key, value)

    def __contains__(self, key):
        key = self.raw_key(key)
        return self.client.exists(key)

    def get(self, key, default=None):
        key = self.raw_key(key)
        value = self.client.get(key)
        if value is None:
            return default
        return self.load_value(value)

    def raw_key(self, key):
        """
        Get the raw key name of *key*, as it is stored in Redis.
        """
        return self.prefix + key

    def keys(self):
        """
        Return the keys in this dict with their prefix removed.
        """
        return [k[len(self.prefix):] for k in self.raw_keys()]

    def raw_keys(self):
        """
        Return the keys in this dict, with their prefix.
        """
        return self.client.keys(self.prefix + '*')

    def values(self):
        """
        Return the values in this dict.
        """
        keys = self.raw_keys()
        if not keys:
            return []
        return [self.load_value(v)
                for v in self.client.mget(*keys) if v is not None]

    def items(self):
        """
        Return ``(key, value)`` pairs in this dict.
        """
        keys = self.raw_keys()
        if not keys:
            return []
        values = self.client.mget(*keys)
        return [(k[len(self.prefix):], self.load_value(v))
                for k, v in zip(keys, values) if v is not None]

    def expire(self, key, duration=None):
        """
        Refresh or set the expiration timeout of *key*.

        The default :attr:`ttl` duration is used, or *duration* may be
        specified to override it (in seconds).
        """
        key = self.raw_key(key)
        if duration is None:
            if self._ttl is None:
                raise ValueError("the dict doesn't have a default "
                        "expiration set, please pass a value to the "
                        "duration parameter")
            duration = self._ttl
        if isinstance(duration, int):
            self.client.expire(key, duration)
        elif isinstance(duration, float):
            self.client.pexpire(key, int(duration * 1000))

    def ttl(self, key):
        """
        Get the remaining time to live of *key*, in seconds.

        The method tries to get the most precise answer, first trying PTTL,
        then TTL if the client doesn't support it. Returns None if the key
        doesn't have an expiration set.
        """
        try:
            ttl = self.raw_pttl(key)
            if ttl is not None:
                return ttl / 1000.0
        except AttributeError:
            ttl = self.raw_ttl(key)
            if ttl is not None:
                return float(ttl)

    def raw_ttl(self, key):
        """
        Raw call to :meth:`redis.client.Redis.ttl`.
        """
        key = self.raw_key(key)
        return self.client.ttl(key)

    def raw_pttl(self, key):
        """
        Raw call to :meth:`redis.client.Redis.pttl`.
        """
        key = self.raw_key(key)
        return self.client.pttl(key)


class RedisHashJsonDict(RedisHashDict):

    def __init__(self, client, name):
        super(RedisHashJsonDict, self).__init__(client, name, load=json.loads,
                dump=json.dumps)


class RedisJsonDict(RedisDict):
    def __init__(self, client, ttl=None, prefix=''):
        super(RedisJsonDict, self).__init__(client, ttl=ttl, prefix=prefix,
                load=json.loads, dump=json.dumps)
