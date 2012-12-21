import json

from jarvis.redis.base import RedisBase

class RedisPublisher(RedisBase):
    """
    Redis-based publisher.
    """

    def __init__(self, client, dump=None):
        super(RedisPublisher, self).__init__(client, dump=dump)

    def publish(self, channel, message):
        """
        Wrapper for :meth:`redis.Redis.publish`.
        """
        message = self.dump_value(message)
        self.client.publish(channel, message)


class RedisSubscriber(RedisBase):
    """
    Redis-based subscriber.
    """

    def __init__(self, client, load=None):
        super(RedisSubscriber, self).__init__(client, load=load)
        self.pubsub = client.pubsub()

    def psubscribe(self, channels):
        """
        Subscribe to all channels matching any pattern in *patterns*.
        """
        self.pubsub.psubscribe(channels)
        self.pubsub.parse_response()

    def punsubscribe(self, channels=[]):
        """
        Unsubscribe from any channel matching any pattern in *patterns*.  If
        empty, unsubscribe from all channels.
        """
        self.pubsub.punsubscribe(channels)
        self.pubsub.parse_response()

    def subscribe(self, channels):
        """
        Subscribe to *channels*, waiting for messages to be published.
        """
        self.pubsub.subscribe(channels)
        self.pubsub.parse_response()

    def unsubscribe(self, channels=[]):
        """
        Unsubscribe from *channels*. If empty, unsubscribe from all channels.
        """
        self.pubsub.unsubscribe(channels)
        self.pubsub.parse_response()

    def recv(self):
        """
        Get the next message.

        Returns a ``(channel, message)`` tuple. This method will block if there
        is nothing in the subscribed channels.
        """
        return next(iter(self))

    def __iter__(self):
        """
        Yield ``(channel, message)`` tuples as messages arrive on subscribed
        channels.
        """
        for item in self.pubsub.listen():
            if item["type"] == "message":
                yield item["channel"], self.load_value(item["data"])


class RedisJsonPublisher(RedisPublisher):
    """
    Convenience class for publishing JSON data.
    """

    def __init__(self, client):
        super(RedisJsonPublisher, self).__init__(client, dump=json.dumps)


class RedisJsonSubscriber(RedisSubscriber):
    """
    Convenience class for subscribing to JSON channels.
    """

    def __init__(self, client):
        super(RedisJsonSubscriber, self).__init__(client, load=json.loads)

