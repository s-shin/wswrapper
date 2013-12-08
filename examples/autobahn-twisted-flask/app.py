import argparse
import json
import msgpack
from flask import Flask, render_template
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.web.wsgi import WSGIResource
from autobahn.websocket import WebSocketServerFactory, WebSocketServerProtocol
from autobahn.resource import WebSocketResource
import myapp

app = Flask(__name__)
app.debug = True

@app.route("/")
def index():
    return render_template("index.html")


class WebSocketWrapperProtocol(WebSocketServerProtocol):
    
    def onConnect(self, req):
        P = "wswrapper_msgpack"
        if P in req.protocols:
            self._is_msgpack_used = True
            return (P, {})
        P = "wswrapper_json"
        if P in req.protocols:
            self._is_msgpack_used = False
            return (P, {})
        
    def onMessage(self, msg, binary):
        if self._is_msgpack_used:
            data = msgpack.unpackb(msg)
        else:
            data = json.loads(msg)
        name, payload = data
        try:
            getattr(myapp, "on_%s" % name)(self, payload)
        except AttributeError as e:
            self.close()
    
    def emit(self, name, payload):
        data = [name, payload]
        if self._is_msgpack_used:
            self.sendMessage(msgpack.packb(data), True)
        else:
            self.sendMessage(json.dumps(data))


class Root(Resource):
    wsgi = WSGIResource(reactor, reactor.getThreadPool(), app)
    
    def getChild(self, child, req):
        req.prepath.pop()
        req.postpath.insert(0, child)
        return self.wsgi
    
    def render(self, req):
        return self.wsgi.render(req)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", metavar="PORT=3000", type=int, default=3000)
    myapp.setup_argparser(parser)
    args = parser.parse_args()
    myapp.setup_app(args)
    
    factory = WebSocketServerFactory("ws://localhost:%d" % args.port)
    factory.protocol = WebSocketWrapperProtocol
    
    root = Root()
    root.putChild("ws", WebSocketResource(factory))
    reactor.listenTCP(args.port, Site(root))
    reactor.run()

if __name__ == "__main__":
    main()

