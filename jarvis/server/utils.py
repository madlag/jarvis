from gevent.coros import RLock
import Crypto.Random as CryptoRandom
import base64
import urllib

class LockContext(object):
    """
    Used by :meth:`RedisBase.use_pipe` to temporary substitute a redis client
    with a :class:`redis.client.Pipeline` object.
    """

    def __init__(self, lock):
        self.lock = lock

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, *exc_info):
        self.lock.release()

class GeventLockable(object):
    def __init__(self):
        self.__lock__ = RLock()
        
    def lock(self):
        return LockContext(self.__lock__)


def generate_random(length):
    p = CryptoRandom.get_random_bytes(length)
    p = base64.b32encode(p)
    return p.strip("=")


def update(base_url, id, op, content):
    body = urllib.urlencode({"op":op, "content":content})
    print body, base_url
    response = urllib.urlopen(base_url + id + "/", body).read()
    print "response=", response
    if response != "OK":
        raise Exception(response)
    
