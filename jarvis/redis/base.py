import contextlib

import redis.client


class RedisBase(object):
    """
    Base class for redis stores. *load* and *dump* may be callables used to
    transform values from strings to python objects, and from python objects to
    strings (e.g. :func:`json.loads` and :func:`json.dumps`).
    """

    def __init__(self, client, load=None, dump=None):
        self.client = client
        self.load = load
        self.dump = dump

    def load_value(self, value):
        if self.load is None:
            return value
        else:
            return self.load(value)

    def dump_value(self, value):
        if self.dump is None:
            return value
        else:
            return self.dump(value)

    def use_pipe(self, pipe):
        """
        A context manager to temporary run the commands of this object through
        *pipe*, a :class:`redis.client.Pipeline` object.
        """
        return PipelineContextManager(self, pipe)

    def _check_multi_return(self, ret):
        """
        Search exceptions in the MULTI return value *ret*, and raise the first
        found.
        """
        for value in ret:
            if isinstance(value, Exception):
                raise value

    def transaction(self, func, others=None, watches=()):
        """
        Run *func* in a transaction, possibly with other :class:`RedisBase`
        objects.
        """
        # Verify this object is not already used in a transaction
        if isinstance(self.client, redis.client.Pipeline):
            raise Exception("nested transactions are not allowed")

        # Get watches names
        if not isinstance(watches, (list, tuple)):
            watches = [watches]
        watches_names = [w.name if isinstance(w, RedisBase) else w
                for w in watches]

        # Check that all the objects use the same redis client
        objs = [self]
        if others is not None:
            if not isinstance(others, (list, tuple)):
                others = [others]
            objs.extend(others)


            clients = [o.client for o in objs]
            if not clients.count(clients[0]) == len(objs):
                for i, obj in enumerate(objs):
                    print "OBJ, CLIENT", obj, clients[i]
                raise ValueError("all objects must use the same redis client: " + str(len(objs)) + " "  + str(clients.count(clients[0])))
            client = clients[0]
        else:
            client = self.client

        # Run func in a transaction
        def transaction(pipe):
            with contextlib.nested(*(o.use_pipe(pipe) for o in objs)):
                func(pipe)

        ret = client.transaction(transaction, *watches_names)
        self._check_multi_return(ret)
        return ret


class PipelineContextManager(object):
    """
    Used by :meth:`RedisBase.use_pipe` to temporary substitute a redis client
    with a :class:`redis.client.Pipeline` object.
    """

    def __init__(self, redis_obj, pipe):
        self.redis_obj = redis_obj
        self.pipe = pipe

    def __enter__(self):
        self.old_client = self.redis_obj.client
        self.redis_obj.client = self.pipe

    def __exit__(self, *exc_info):
        self.redis_obj.client = self.old_client
