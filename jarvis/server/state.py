import jarvis.redis.dict as redisdict
import jarvis.server.broker as broker
import json
import copy
import time

# The State store objects and receive/send operations  on objects through a broker 

STATE_PREFIX = "state"
KEY_SEPARATOR = "-"

class StateObject(object):    
    def __init__(self, state, id, user, type, full_object):
        self.state = state
        self.id = id
        self.user = user
        self.type = type
        self.load(full_object)

    def load(self, full_object):
        self.full_object = full_object
        self.value = self.decode_value()

    def decode_value(self):
        return self.full_object.get("value", None)
    
    def encode_value(self):
        self.full_object["value"] = self.value

    def create_operation(self, op, timestamp = None, operation_parameters = None):
        operation = {}
        operation["op"] = op
        operation["user"] = self.user
        operation["id"] = self.id
        operation["time"] = timestamp or self.full_object.get("time")
        operation["parameters"] = operation_parameters or {}
        return operation
                
    def save(self, pipe = None):
        timestamp = time.time()
        self.full_object["time"] = timestamp
        self.encode_value()
        self.state[self.id] = self.full_object
        
        return timestamp

    def op(self, op, **kwargs):
        objFunction = getattr(self, op + "_operation")
        self.state.op(op, self, objFunction, **kwargs)

    def get_agregated_operation(self):
        return self.create_operation("set", None, {"content":self.value})
        
class StringObject(StateObject):
    def set_operation(self, content):
        self.value = content
        return self.create_operation("set", None, {"content":content})

    def append_operation(self, content):
        self.value += content
        return self.create_operation("append", None, {"content":content})


class StateObjectSubscriber(object):
    def __init__(self, state):
        self.state = state
        self.subscriber = state.broker.subscriber()

    def subscribe(self, id):
        key = self.state.id_to_key(id)
        self.subscriber.subscribe(id)

    def __iter__(self):
        """
        Yield ``(channel, message)`` tuples as messages arrive on subscribed
        channels.
        """
        for channel, item in self.subscriber:
            yield channel, item            

class State(redisdict.RedisDict):
    def __init__(self, user, client):
        self.user = user

        assert(client != None)
        
        # Create the broker
        self.broker = broker.Broker(client)
        self.publisher = self.broker.publisher()

        super(State, self).__init__(client)

    def id_to_key(self, id):
        key = KEY_SEPARATOR.join([STATE_PREFIX, self.user, id])

        return key
        
    def key_to_id(self, key):
        return key[len(STATE_PREFIX):]
                
    def factory(self, type, id, full_object):
        type = type.capitalize()
        constructor = globals()[type + "Object"]
        o = constructor(self, id, self.user, type, full_object)
        return o

    def __setitem__(self, id, value):
        key = self.id_to_key(id)
        super(State, self).__setitem__(key, json.dumps(value))
        
    def __getitem__(self, id):
        key = self.id_to_key(id)
        value = super(State, self).__getitem__(key)
        full_object = json.loads(value)
        type = full_object.get("type")
        return self.factory(type, id, full_object)
    
    def get_or_create(self, id, type):
        try:
            return self[id]
        except:
            full_object = {"id": id, "user": self.user, "type": type}
            return self.factory(type, id, full_object)

    def get_agregated_operation(self, id):
        obj = self[id]
        return obj.get_agregated_operation()
        
    def publish(self, id, message):
        key = self.id_to_key(id)
        self.publisher.publish(key, message)
        
    def transaction(self, function, others, watches):
        others += [self.publisher, self.broker]

        tr_watches = []
        for k in watches:
            tr_watches = self.id_to_key(k)
            
        super(State, self).transaction(function, others = others, watches = tr_watches)
        
    def op(self, op, obj, objFunction, **kwargs):
        def update_state_set(pipe):
            self.get_or_create(obj.id, obj.type)
            pipe.multi()
            # Set the value in state

            operation = objFunction(**kwargs)
            
            timestamp = obj.save()
            operation["time"] = timestamp
            
            # Publish the value
            self.publish(obj.id, operation)
        
        # Execute the transation
        self.transaction(update_state_set, others = [], watches = [obj.id])
        
    def subscriber(self):
        return StateObjectSubscriber(self)
    
