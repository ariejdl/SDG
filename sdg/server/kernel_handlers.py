
import json
import logging
import datetime

import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado.concurrent import Future
from tornado.ioloop import IOLoop

from notebook.base.zmqhandlers import ZMQStreamHandler

import jupyter_client
from jupyter_client import protocol_version as client_protocol_version
from jupyter_client.session import Session
from jupyter_client.jsonutil import date_default, extract_dates
from jupyter_client import kernelspec
from jupyter_client.asynchronous import AsyncKernelClient
from jupyter_client.multikernelmanager import AsyncMultiKernelManager

from ipython_genutils.py3compat import cast_unicode

from .handler_utils import WebSocketMixin

# enough time for app to initialise?
KERNEL_INFO_TIMEOUT = datetime.timedelta(seconds=10)

# override one method to have a tempfile for the connection_file
# https://github.com/jupyter/jupyter_client/blob/master/jupyter_client/multikernelmanager.py
class TempConnectionFileMixin():

    def pre_start_kernel(self, kernel_name, **kwargs):
        kernel_id = kwargs.pop('kernel_id', self.new_kernel_id(**kwargs))
        if kernel_id in self:
            raise DuplicateKernelError('Kernel already exists: %s' % kernel_id)

        if kernel_name is None:
            kernel_name = self.default_kernel_name
        # kernel_manager_factory is the constructor for the KernelManager
        # subclass we are using. It can be configured as any Configurable,
        # including things like its transport and ip.
        constructor_kwargs = {}
        if self.kernel_spec_manager:
            constructor_kwargs['kernel_spec_manager'] = self.kernel_spec_manager

        # override, 
        km = self.kernel_manager_factory(
            connection_file='',
            parent=self, log=self.log, kernel_name=kernel_name,
            **constructor_kwargs
        )
        return km, kernel_name, kernel_id

class CustomMultiKernelManager(TempConnectionFileMixin, AsyncMultiKernelManager):
    pass

_kernel_manager = CustomMultiKernelManager()

def make_kernel_model(km, kernel_id):
    k = km.get_kernel(kernel_id)
    return {
        'name': k.kernel_name,
        'id': kernel_id
    }

"""
much of this is taken from the jupyter notebook repository,
especially the handlers.py file
https://github.com/jupyter/notebook/blob/master/notebook/services/kernels/handlers.py
"""

class APIHandler(tornado.web.RequestHandler):
    kernel_manager = _kernel_manager
    log = logging
    
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

    #@web.authenticated
    def get(self):
        specs = list(kernelspec.find_kernel_specs().keys())
        km = self.kernel_manager
        running = [make_kernel_model(km, kid) for kid in km.list_kernel_ids()]
        
        self.finish(json.dumps({
            'available': specs,
            'running': running
        }))

    #@web.authenticated
    async def post(self):
        km = self.kernel_manager
        model = self.get_json_body()
        if model is None:
            model = {}
        
        model.setdefault('name', km.default_kernel_name)

        kernel_id = await km.start_kernel(kernel_name=model['name'])
        model['id'] = kernel_id
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
class ZMQChannelsHandler(ZMQStreamHandler, WebSocketMixin, APIHandler):
    
    # class-level registry of open sessions
    # allows checking for conflict on session-id,
    # which is used as a zmq identity and must be unique.
    _open_sessions = {}
    allow_origin = '*'

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, getattr(self, 'kernel_id', 'uninitialized'))

    def initialize(self):
        """
        called by tornado
        """
        super(ZMQChannelsHandler, self).initialize()
        self.zmq_stream = None
        self.channels = {}
        self.kernel_id = None
        self.kernel_info_channel = None
        self._kernel_info_future = Future()
        self._close_future = Future()
        self.session_key = ''

    def create_stream(self):
        km = self.kernel_manager
        identity = self.session.bsession
        for channel in ('shell', 'control', 'iopub', 'stdin'):
            meth = getattr(km, 'connect_' + channel)
            self.channels[channel] = stream = meth(self.kernel_id, identity=identity)
            stream.channel = channel
            
    def request_kernel_info(self):
        """send a request for kernel_info"""
        km = self.kernel_manager
        kernel = km.get_kernel(self.kernel_id)
        try:
            # check for previous request
            future = kernel._kernel_info_future
        except AttributeError:
            self.log.debug("Requesting kernel info from %s", self.kernel_id)
            # Create a kernel_info channel to query the kernel protocol version.
            # This channel will be closed after the kernel_info reply is received.
            if self.kernel_info_channel is None:
                self.kernel_info_channel = km.connect_shell(self.kernel_id)
            self.kernel_info_channel.on_recv(self._handle_kernel_info_reply)
            self.session.send(self.kernel_info_channel, "kernel_info_request")
            # store the future on the kernel, so only one request is sent
            kernel._kernel_info_future = self._kernel_info_future
        else:
            if not future.done():
                self.log.debug("Waiting for pending kernel_info request")
            future.add_done_callback(lambda f: self._finish_kernel_info(f.result()))
        return self._kernel_info_future
    
    def _handle_kernel_info_reply(self, msg):
        """process the kernel_info_reply
        
        enabling msg spec adaptation, if necessary
        """
        idents,msg = self.session.feed_identities(msg)
        try:
            msg = self.session.deserialize(msg)
        except:
            self.log.error("Bad kernel_info reply", exc_info=True)
            self._kernel_info_future.set_result({})
            return
        else:
            info = msg['content']
            self.log.debug("Received kernel info: %s", info)
            if msg['msg_type'] != 'kernel_info_reply' or 'protocol_version' not in info:
                self.log.error("Kernel info request failed, assuming current %s", info)
                info = {}
            self._finish_kernel_info(info)
        
        # close the kernel_info channel, we don't need it anymore
        if self.kernel_info_channel:
            self.kernel_info_channel.close()
        self.kernel_info_channel = None

    def _finish_kernel_info(self, info):
        """Finish handling kernel_info reply
        
        Set up protocol adaptation, if needed,
        and signal that connection can continue.
        """
        protocol_version = info.get('protocol_version', client_protocol_version)
        if protocol_version != client_protocol_version:
            self.session.adapt_version = int(protocol_version.split('.')[0])
            self.log.info("Adapting from protocol version {protocol_version} (kernel {kernel_id}) to {client_protocol_version} (client).".format(protocol_version=protocol_version, kernel_id=self.kernel_id, client_protocol_version=client_protocol_version))
        if not self._kernel_info_future.done():
            self._kernel_info_future.set_result(info)
    
        
    async def pre_get(self):
        # authenticate first
        await super(ZMQChannelsHandler, self).pre_get()
        # check session collision:
        await self._register_session()
        # then request kernel info, waiting up to a certain time before giving up.
        # We don't want to wait forever, because browsers don't take it well when
        # servers never respond to websocket connection requests.
        kernel = self.kernel_manager.get_kernel(self.kernel_id)
        self.session.key = kernel.session.key
        future = self.request_kernel_info()

        def give_up():
            """Don't wait forever for the kernel to reply"""
            if future.done():
                return
            self.log.warning("Timeout waiting for kernel_info reply from %s", self.kernel_id)
            future.set_result({})
        
        loop = IOLoop.current()
        loop.add_timeout(KERNEL_INFO_TIMEOUT, give_up)
        # actually wait for it
        res = await future
        return res

    async def _register_session(self):
        """Ensure we aren't creating a duplicate session.
        
        If a previous identical session is still open, close it to avoid collisions.
        This is likely due to a client reconnecting from a lost network connection,
        where the socket on our side has not been cleaned up yet.
        """
        if self.kernel_id is None or self.session.session is None:
            raise web.HTTPError(500, u'Invalid Kernel ID or Kernel Session')
        
        self.session_key = '%s:%s' % (self.kernel_id, self.session.session)
        stale_handler = self._open_sessions.get(self.session_key)
        if stale_handler:
            self.log.warning("Replacing stale connection: %s", self.session_key)
            await stale_handler.close()
        self._open_sessions[self.session_key] = self

    async def get(self, kernel_id):
        self.kernel_id = cast_unicode(kernel_id, 'ascii')
        self.session = self.kernel_manager.get_kernel(self.kernel_id).session
        return await super(ZMQChannelsHandler, self).get(kernel_id=kernel_id)

    def open(self, kernel_id):
        super(ZMQChannelsHandler, self).open()
        km = self.kernel_manager

        try:
            self.create_stream()
        except web.HTTPError as e:
            self.log.error("Error opening stream: %s", e)
            # WebSockets don't response to traditional error codes so we
            # close the connection.
            for channel, stream in self.channels.items():
                if not stream.closed():
                    stream.close()
            self.close()
            return

        km.add_restart_callback(self.kernel_id, self.on_kernel_restarted)
        km.add_restart_callback(self.kernel_id, self.on_restart_failed, 'dead')

        for channel, stream in self.channels.items():
            stream.on_recv_stream(self._on_zmq_reply)

    def close(self):
        super(ZMQChannelsHandler, self).close()
        return self._close_future

    def on_message(self, msg):
        if not self.channels:
            # already closed, ignore the message
            self.log.debug("Received message on closed websocket %r", msg)
            return
        if isinstance(msg, bytes):
            msg = deserialize_binary_message(msg)
        else:
            msg = json.loads(msg)
        channel = msg.pop('channel', None)
        if channel is None:
            self.log.warning("No channel specified, assuming shell: %s", msg)
            channel = 'shell'
        if channel not in self.channels:
            self.log.warning("No such channel: %r", channel)
            return
        mt = msg['header']['msg_type']
        stream = self.channels[channel]
        self.session.send(stream, msg)


    def _on_zmq_reply(self, stream, msg_list):
        idents, fed_msg_list = self.session.feed_identities(msg_list)
        msg = self.session.deserialize(fed_msg_list)
        parent = msg['parent_header']

        channel = getattr(stream, 'channel', None)
        msg_type = msg['header']['msg_type']

        super(ZMQChannelsHandler, self)._on_zmq_reply(stream, msg)
        
    def on_close(self):
        self.log.debug("Websocket closed %s", self.session_key)
        # unregister myself as an open session (only if it's really me)
        if self._open_sessions.get(self.session_key) is self:
            self._open_sessions.pop(self.session_key)

        km = self.kernel_manager
        if self.kernel_id in km:
            #km.notify_disconnect(self.kernel_id)
            km.remove_restart_callback(
                self.kernel_id, self.on_kernel_restarted,
            )
            km.remove_restart_callback(
                self.kernel_id, self.on_restart_failed, 'dead',
            )

            """
            # start buffering instead of closing if this was the last connection
            if km._kernel_connections[self.kernel_id] == 0:
                km.start_buffering(self.kernel_id, self.session_key, self.channels)
                self._close_future.set_result(None)
                return
            """

        # This method can be called twice, once by self.kernel_died and once
        # from the WebSocket close event. If the WebSocket connection is
        # closed before the ZMQ streams are setup, they could be None.
        for channel, stream in self.channels.items():
            if stream is not None and not stream.closed():
                stream.on_recv(None)
                stream.close()

        self.channels = {}
        self._close_future.set_result(None)

    def _send_status_message(self, status):
        iopub = self.channels.get('iopub', None)
        if iopub and not iopub.closed():
            # flush IOPub before sending a restarting/dead status message
            # ensures proper ordering on the IOPub channel
            # that all messages from the stopped kernel have been delivered
            iopub.flush()
        msg = self.session.msg("status",
            {'execution_state': status}
        )
        msg['channel'] = 'iopub'
        self.write_message(json.dumps(msg, default=date_default))
        
    def on_kernel_restarted(self):
        logging.warn("kernel %s restarted", self.kernel_id)
        self._send_status_message('restarting')

    def on_restart_failed(self):
        logging.error("kernel %s restarted failed!", self.kernel_id)
        self._send_status_message('dead')        


_kernel_id_regex = r"(?P<kernel_id>\w+-\w+-\w+-\w+-\w+)"
_kernel_action_regex = r"(?P<action>restart|interrupt)"

kernel_handlers = [
    (r"/api/kernels", MainKernelHandler),
    (r"/api/kernels/%s" % _kernel_id_regex, KernelHandler),
    (r"/api/kernels/%s/%s" % (_kernel_id_regex, _kernel_action_regex), KernelActionHandler),
    (r"/api/kernels/%s/channels" % _kernel_id_regex, ZMQChannelsHandler),
]
    
