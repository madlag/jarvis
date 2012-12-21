import gevent
import jarvis.server.utils as utils
import jarvis.server.broker as broker
import jarvis.server.redisconnect as redisconnect
import jarvis.redis.dict as redis_dict
import jarvis.server.state as state
import json

class BaseStateObserver(gevent.Greenlet):
    def __init__(self, session, user, queue, max_messages = None):
        gevent.Greenlet.__init__(self)
        self.session = session
        self.user = user
        self.queue = queue
        self.message_count = 0
        self.max_messages = max_messages

        self.wake_up_channel = "-".join([user, session if session else self.random_session(), "wakeup"])
        self.ready = False

    def random_session(self):
        return utils.generate_random(10)

    def emit(self, msg):
        self.message_count += 1

        if self.max_messages < 0:
            ret = True
        else:
            ret = self.message_count < self.max_messages

        if not ret:
            self.queue.put(StopIteration)
        return ret

    def add_id(self, id):
        if id == '':
            raise Exception("Empty id")

        while not self.ready:
            gevent.sleep(0.01)

        brok = broker.Broker()
        publisher = brok.publisher()
        publisher.publish(self.wake_up_channel, {"id":id, "op":"listen"})

    def prepare(self):
        pass

    def _run(self):
        # Create redis client
        client = redisconnect.connect()
        self.dict = redis_dict.RedisDict(client)
        # Create the broker
        self.state = state.State(self.user, client)
        self.subscriber = self.state.subscriber()
        self.lastTime = {}

        # Subscribe to the "wake-up" signal
        self.subscriber.subscribe(self.wake_up_channel)
        self.ready = True

        self.prepare()

        try:
            # Create top level redis dict
            for operation in self.subscriber:
                operation = operation[1]
                id = operation["id"]
                if operation.get("op") == "listen":
                    self.subscriber.subscribe(self.state.id_to_key(id))

                    try:
                        operation = self.state.get_agregated_operation(id)
                    except KeyError:
                        # We will only get subscribe messages, as the object does exist yet
                        continue

                    self.emit(operation)
                    self.lastTime[id] = operation["time"]
                else:
                    t = operation["time"]

                    if id in self.lastTime and t > self.lastTime[id]:
                        go_on = self.emit(operation)
                        self.lastTime[id] = t
                    if not go_on:
                        break
        finally:
            self.queue.put(StopIteration)



class JsonStateObserver(BaseStateObserver):
    def emit(self, msg):
        self.queue.put(json.dumps(msg) + "\n")
        return super(JsonStateObserver, self).emit(msg)

class EventSourceStateObserver(BaseStateObserver):
    def emit_(self, type, content, final_data = False):
        suffix = "\n\n" if final_data else "\n"
        output = type + ": " + content + suffix
        self.queue.put(output)

    def emit(self, msg):
        self.emit_("data", json.dumps(msg), final_data = True)

        return super(EventSourceStateObserver, self).emit(msg)

    def prepare(self):
        # 2kb padding for IE
        self.emit_('', ' ' * 2048)
        self.emit_('retry', '2000')
