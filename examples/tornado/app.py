import os
import logging
import argparse
import json
import msgpack
import tornado.ioloop
import tornado.web
import tornado.websocket
import myapp

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    
    def select_subprotocol(self, subprotocols):
        P = "wswrapper_msgpack"
        if P in subprotocols:
            self._is_msgpack_used = True
            return P
        P = "wswrapper_json"
        if P in subprotocols:
            self._is_msgpack_used = False
            return P
        self.close()
    
    def open(self):
        logging.info("opened.")
        myapp.on_open(self)
    
    def on_close(self):
        logging.info("closed.")
        myapp.on_close(self)
        
    def on_message(self, message):
        if self._is_msgpack_used:
            data = msgpack.unpackb(message)
        else:
            data = json.loads(message)
        name, payload = data
        try:
            getattr(myapp, "on_%s" % name)(self, payload)
        except AttributeError as e:
            self.close()
    
    def emit(self, name, payload):
        data = [name, payload]
        if self._is_msgpack_used:
            self.write_message(msgpack.packb(data), True)
        else:
            self.write_message(json.dumps(data))
        

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", metavar="PORT=3000", type=int, default=3000)
    myapp.setup_argparser(parser)
    args = parser.parse_args()
    myapp.setup_app(args)
    
    tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", WebSocketHandler)
    ], **{
        "cookie_secret": "myapp_secret_string",
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "xsrf_cookies": True,
    }).listen(args.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
