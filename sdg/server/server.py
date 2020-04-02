
import os
import tornado

from .terminal_handlers import initialize as init_terminal
from .kernel_handlers import kernel_handlers

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("""
        <!DOCTYPE html>
        <html>
          <head>

        <style>
        html, body { height: 100%; }
        </style>

            <link rel="stylesheet" href="/static/node_modules/xterm/css/xterm.css" />
            <script src="/static/node_modules/xterm-addon-fit/lib/xterm-addon-fit.js"></script>
            <script src="/static/node_modules/xterm/lib/xterm.js"></script>

            <script src="/static/terminado.js"></script>
            <script src="/static/app.js"></script>

          </head>
          <body>
          </body>
        </html>
        """)


class WSEchoHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")


def main():
    port = 8001
    server_url = 'http://localhost:{}'.format(port)

    cur_dir = os.path.abspath(os.getcwd())

    settings = {
        "static_path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'static')),
        "base_url": "/"
    }
    
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/echo", WSEchoHandler),

        *kernel_handlers
        
    ], **settings)

    init_terminal(application, cur_dir, server_url, settings)
    
    application.listen(port)
    tornado.ioloop.IOLoop.current().start()

