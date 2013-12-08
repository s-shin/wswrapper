# -*- coding: utf-8 -*-
import os
import argparse
import json
import msgpack
import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import myapp


class WebSocketHandler(WebSocket):
    def _log(self, msg):
        cherrypy.log(msg, "WEBSOCKET")
    
    def opened(self):
        self._log("opened")
        # Currently (v0.3.3), subprotocols are not supported.
        # if not "wswrapper" in self.protocols:
        #     self.close(reason="Subprotocol 'wswrapper' is required.")
        #     return
        # if "msgpack" in self.protocols:
        #     self._is_msgpack_used = True
        # else:
        #     self._is_msgpack_used = False
        self._is_msgpack_used = None # unknown
        myapp.on_open(self)
    
    def closed(self, code, reason):
        self._log("close")
        myapp.on_close(self)
    
    def received_message(self, message):
        # Whether msgpack is used is decided in receiving the first message.
        if self._is_msgpack_used is None:
            self._is_msgpack_used = message.is_binary
            
        if self._is_msgpack_used:
            if not message.is_binary:
                self.close(reason="")
                return
            data = msgpack.unpackb(message.data)
        else:
            data = json.loads(message.data)
        name, payload = data
        try:
            getattr(myapp, "on_%s" % name)(self, payload)
        except AttributeError as e:
            self.close(reason="'%s' event handler doesn't exits." % name)
    
    def emit(self, name, payload):
        data = [name, payload]
        if self._is_msgpack_used:
            self.send(msgpack.packb(data), True)
        else:
            self.send(json.dumps(data))


class Root(object):
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/index.html")

    @cherrypy.expose
    def ws(self):
        pass
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", metavar="PORT=3000", type=int, default=3000)
    myapp.setup_argparser(parser)
    args = parser.parse_args()
    myapp.setup_app(args)
    
    cherrypy.config.update({
        "server.socket_host": "127.0.0.1",
        "server.socket_port": args.port
    })
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()
    cherrypy.quickstart(Root(), "", config={
        "/": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": os.path.abspath(
                os.path.join(os.path.dirname(__file__), "public/")),
        },
        "/ws": {
            "tools.websocket.on": True,
            "tools.websocket.handler_cls": WebSocketHandler,
        }
    })
    
if __name__ == "__main__":
    main()
