from __future__ import absolute_import

import redis

import jarvis.utils.conf as conf

connection_pool = redis.ConnectionPool()

def connect(host=None, port=None, password=None, db=None):
    """
    Create a :class:`redis.Redis` connection object, using Dragon's default
    configuration.
    """
    host = host if host is not None else conf.jarvis.REDIS_HOST if hasattr(conf.jarvis, "REDIS_HOST") else "localhost"
    port = port if port is not None else conf.jarvis.REDIS_PORT if hasattr(conf.jarvis, "REDIS_PORT") else 6379
    password = password if password is not None else conf.jarvis.REDIS_PASSWORD if hasattr(conf.jarvis, "REDIS_PASSWORD") else None
    db = db if db is not None else conf.jarvis.REDIS_DB
    return redis.Redis(host=host, port=port, password=password, db=db, connection_pool=connection_pool)

