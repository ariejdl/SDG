
import os
import json

import tornado.websocket
import tornado.ioloop
import tornado.web

import jupyter_client
from jupyter_client import kernelspec
from jupyter_client.asynchronous import AsyncKernelClient
from jupyter_client.manager import start_new_kernel, start_new_async_kernel
from jupyter_client.multikernelmanager import AsyncMultiKernelManager


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("""
        <!DOCTYPE html>
        <html>
          <head>
            <script src="/static/app.js"></script>
          </head>
          <body>
          </body>
        </html>
        """)


# jupyter websocket handler:
# https://github.com/jupyter/notebook/blob/master/notebook/services/kernels/handlers.py
# intricate: ZMQChannelsHandler, probably want to simplify it
# of note:
# - REST handlers for creation/viewing/stopping/actions on kernels
# - open(kernel_id) - this is different to creation, creation returns a kernel_id
#   - _on_zmq_reply()
# - create_stream()
# - initialize()
# - for simplicity may not want to use the 'MappingKernelManager' buffering approach
# - on_message()
# - close()/on_close()
# - and smaller things
# - ping/pong of `WebSocketMixin` may be helpful

def make_kernel_model(km, kernel_id):
    k = km.get_kernel(kernel_id)
    return {
        'name': k.kernel_name,
        'kernel_id': kernel_id
    }

class APIHandler(tornado.web.RequestHandler):
    kernel_manager = AsyncMultiKernelManager()
    
    def get_json_body(self):
        """Return the body of the request as JSON data."""
        if not self.request.body:
            return None
        # Do we need to call body.decode('utf-8') here?
        body = self.request.body.strip().decode(u'utf-8')
        try:
            model = json.loads(body)
        except Exception:
            raise web.HTTPError(400, u'Invalid JSON in body of request')
        return model

class MainKernelHandler(APIHandler):

    def get(self):
        specs = list(kernelspec.find_kernel_specs().keys())
        km = self.kernel_manager
        running = [make_kernel_model(km, kid) for kid in km.list_kernel_ids()]
        
        self.finish(json.dumps({
            'available': specs,
            'running': running
        }))

    async def post(self):
        km = self.kernel_manager
        model = self.get_json_body()
        if model is None:
            model = {}
        
        model.setdefault('name', km.default_kernel_name)

        kernel_id = await km.start_kernel(kernel_name=model['name'])
        model['kernel_id'] = kernel_id
        self.set_status(201)
        self.finish(json.dumps(model))

class KernelHandler(APIHandler):

    #@web.authenticated
    def get(self, kernel_id):
        km = self.kernel_manager
        model = make_kernel_model(km, kernel_id)
        self.finish(json.dumps(model))

    #@web.authenticated
    async def delete(self, kernel_id):
        km = self.kernel_manager
        if kernel_id in km:
            await km.shutdown_kernel(kernel_id)
            self.set_status(204)
        else:
            self.finish(json.dumps({ "error": "kernel_id was not found" }))
            self.set_status(404)

class KernelActionHandler(APIHandler):

    #@web.authenticated
    async def post(self, kernel_id, action):
        km = self.kernel_manager
        if action == 'interrupt':
            await km.interrupt_kernel(kernel_id)
            self.set_status(204)
        if action == 'restart':
            try:
                await km.restart_kernel(kernel_id)
            except Exception as e:
                self.log.error("Exception restarting kernel", exc_info=True)
                self.set_status(500)
            else:
                model = make_kernel_model(km, kernel_id)
                self.write(json.dumps(model))
        self.finish()


# may want to inherit from jupyter_notebook class
class ZMQChannelsHandler():
    pass
        
class WebSocketHandler(tornado.websocket.WebSocketHandler):

    def get(self):
        # TODO: authorization
        # e.g. get() / pre_get()
        print('get info')
        return super(WebSocketHandler, self).get()
    
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")


def main():

    _kernel_id_regex = r"(?P<kernel_id>\w+-\w+-\w+-\w+-\w+)"
    _kernel_action_regex = r"(?P<action>restart|interrupt)"
    
    settings = {
        "static_path": os.path.abspath(os.path.dirname(__file__)),
    }
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/echo", WebSocketHandler),

        (r"/api/kernels", MainKernelHandler),
        (r"/api/kernels/%s" % _kernel_id_regex, KernelHandler),
        (r"/api/kernels/%s/%s" % (_kernel_id_regex, _kernel_action_regex), KernelActionHandler),
        #(r"/api/kernels/%s/channels" % _kernel_id_regex, ZMQChannelsHandler),
        
    ], **settings)
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
