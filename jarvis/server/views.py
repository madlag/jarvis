from pyramid.view import view_config
from pyramid.response import Response
import jarvis.server.redisconnect as redisconnect
import jarvis.server.utils as utils
from gevent.queue import Queue
import gevent
import json
import time
import os
import jarvis.server.state as state
import state_observer

STATE_PREFIX = "state-"

def state_id_key(id):
    return STATE_PREFIX + id

def decode_state(value):
    return json.loads(value)        

# Update a state
@view_config(route_name='state_update', request_method="POST")
def state_post(context, request):
    id = request.matchdict["id"]
    object_type = request.POST.get('type', 'string')
    operation_type = request.POST.get("op", "set")
    
    parameters = {}
    for k, v in request.POST.iteritems():
        if k not in ["op", "type"]:
            parameters[k] = v
            
    # Create redis client
    client = redisconnect.connect()

    # Create top level         
    st = state.State("user", client)

    obj = st.get_or_create(id, object_type)
        
    obj.op(operation_type, **parameters)
        
    resp = Response()
    resp.content_type = "text/plain"
    resp.text = u"OK"
    # return the old value of the key
    return resp
                
class StateObserverSessionSet(utils.GeventLockable):
    def __init__(self):
        super(StateObserverSessionSet, self).__init__()
        self.sessions = {}
        

    def get_observer(self, session, user, **kwargs):
        if session != None:
            session = "-".join([user, session])

        with self.lock():
            if session not in self.sessions:            
                queue = Queue()
                observer = self.factory(session, user, queue, **kwargs)
                if session != None:
                    # No session is required
                    self.sessions[session] = (queue, observer)
                observer.start()
            else:
                queue, observer = self.sessions[session]
                
            
        return queue, observer


def state_get(context, request, stateObserverSet, response, content_type, stream = True):
    session_id = request.matchdict["session_id"]
    request_dict = request.params
    max_messages = int(request_dict.get("count", -1))
    ids_string = request_dict.get("ids")

    if ids_string != None:
        ids = ids_string.split(",")
    else:
        ids = []

    user = "user"
    # Create response
    queue, observer = stateObserverSet.get_observer(session_id, user, max_messages = max_messages)
    
    for id in ids:
        observer.add_id(id)

    if stream:
        response.app_iter = queue
        response.content_type = content_type
    else:
        response.text == u"OK"
        response.content_type = "text/plain"
    return response

    
class JsonStateObserverSessionSet(StateObserverSessionSet):
    factory = state_observer.JsonStateObserver

jsonStateObserverSet = JsonStateObserverSessionSet()

@view_config(route_name='state_stream_json', request_method="GET")
def state_get_json(context, request):
    response = Response()
    return state_get(context, request, jsonStateObserverSet, response, 'application/json')
    

class EventSourceStateObserverSessionSet(StateObserverSessionSet):
    factory = state_observer.EventSourceStateObserver

eventSourceStateObserverSet = EventSourceStateObserverSessionSet()

@view_config(route_name='state_stream_eventsource', request_method="POST")
def state_get_event_source(context, request):
    event_stream = request.headers.get("accept") == "text/event-stream"

    response = Response()
    if event_stream:
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Cache-Control'] = 'no-cache'

    return state_get(context, request, eventSourceStateObserverSet, response, 'text/event-stream', stream = event_stream)


