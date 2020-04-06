
# jupyter websocket handler:
# https://github.com/jupyter/notebook/blob/master/notebook/services/kernels/handlers.py

import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        # TODO: add static encrypted password test and use secure cookie with 1 day duration
        return "anon_user"

class WebSocketMixin(object):

    def set_default_headers(self):
        """Undo the set_default_headers in IPythonHandler
        which doesn't make sense for websockets
        """
        pass
    
    def initialize(self):
        pass

    def check_origin(self, origin=None):
        pass

    async def pre_get(self):
        # TODO: auth
        if self.get_current_user() is None:
            #self.log.warning("Couldn't authenticate WebSocket connection")
            #raise web.HTTPError(403)
            pass

        if self.get_argument('session_id', False):
            self.session.session = cast_unicode(self.get_argument('session_id'))
        else:
            self.log.warning("No session ID specified")        

    async def get(self, *args, **kwargs):
        await self.pre_get()

    def initialize(self):
        #self.session = Session()
        #self.session.auth = None
        pass
