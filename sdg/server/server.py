
import os
import sys
import tornado
import logging as log

log.basicConfig(stream=sys.stdout, level=log.DEBUG)

from notebook.services.contents.filemanager import FileContentsManager

from .terminal_handlers import initialize as init_terminal
from .kernel_handlers import handlers as kernel_handlers
from .contents_handlers import handlers as contents_handlers

class WSEchoHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        pass

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        pass

    def check_origin(self, origin):
        # enable CORS, check security! check if overriden by allow_origin='*'
        return True
    

def main():
    port = 8001
    server_url = 'http://localhost:{}'.format(port)

    cur_dir = os.path.abspath(os.getcwd())

    settings = {
        #"static_path": os.path.abspath(
        #    os.path.join(os.path.dirname(__file__), '..', '..', 'client', 'dist')),
        
        # TODO: implement
        "login_url": "/login",
        "base_url": "/",
        "contents_manager": FileContentsManager(),

        "xsrf_cookies": False,
        
        'allow_origin': '*',
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': '*'
        }

    }
    
    application = tornado.web.Application([
        (r"/echo", WSEchoHandler),

        *kernel_handlers,
        *contents_handlers
        
    ], **settings)

    init_terminal(application, cur_dir, server_url, settings)

    log.info("listening on {}".format(port))
    application.listen(port)
    tornado.ioloop.IOLoop.current().start()

