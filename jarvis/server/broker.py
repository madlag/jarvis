import jarvis.redis.base as redisbase
import jarvis.server.redisconnect as redisconnect
import jarvis.redis.pubsub as pubsub

class Broker(redisbase.RedisBase):
    def __init__(self, client = None):
        self.client = client

    def connect(self):
        if self.client == None:
            self.client = redisconnect.connect()
        return self.client

    def subscriber(self):
        client = self.connect()
        return pubsub.RedisJsonSubscriber(client)

    def publisher(self):
        client = self.connect()
        publisher = pubsub.RedisJsonPublisher(client)
        return publisher

