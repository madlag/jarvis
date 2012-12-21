import os
import os.path as op

from pyramid.config import Configurator
from gevent.pywsgi import WSGIServer

class Frontend(object):
    def start(self, start_wsgi_server=False, forever = False):
        """
        Start the frontend's greenlets.

        If *start_wsgi_server* is True, also create the frontend's main WSGI
        application and serve it with gevent's WSGI server.
        """
        # Start the frontend WSGI server if requested
        if start_wsgi_server:
            wsgi_app = self.create_wsgi_app({
                'pyramid.debug_authorization': 'true',
                'pyramid.debug_routematch': 'true',
                'pyramid.reload_templates': 'true',
                'pyramid.debug_notfound': 'true'
            })
            logfile = open("/tmp/jarvis.log", "w")

            self.wsgi_server = WSGIServer(("127.0.0.1", 9017), wsgi_app, log=logfile)
            if forever:
                self.wsgi_server.serve_forever()
            else:
                self.wsgi_server.start()
        else:
            self.wsgi_server = None

    def stop(self):
        if self.wsgi_server is not None:
            self.wsgi_server.stop()

    def create_wsgi_app(self, settings):
        # Create applincation
        config = Configurator(settings=settings)
        config.add_route('state_update', '/state/update/{id}/')
        config.add_route('state_stream_json', '/state/stream/json/{session_id}/')
        config.add_route('state_stream_eventsource', '/state/stream/eventsource/{session_id}/')
        static_path = op.join(op.dirname(__file__), "media")
        config.add_static_view(name='static', path=static_path)
        config.scan()

        return config.make_wsgi_app()
