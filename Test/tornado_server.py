# -*- coding: utf-8 -*-
import os
import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from tornado.httpserver import HTTPServer
from tornado.options import define
from tornado.options import options
from tornado.ioloop import IOLoop
from werkzeug.contrib.cache import RedisCache


define(name='port', default=8900, help="run on the given port", type=int)
template_path = os.path.join(os.path.dirname(__file__), "templates")
static_path = os.path.join(os.path.dirname(__file__), "static")
cache = RedisCache()
cache.clear()


class TestGetHandler(RequestHandler):
    def get(self):
        self.write("Hello, World!")


class VideoView(RequestHandler):
    """
    渲染页面
    """
    def get(self, *args, **kwargs):
        page_title = "ws客户端"
        kw = dict()
        kw['page_title'] = page_title
        self.render("io_client2.html", **kw)


class PushView(RequestHandler):
    def get(self, *args, **kwargs):
        print(args)
        print(kwargs)


class ClientContainer:
    """客户端容器"""

    @classmethod
    def add(cls, obj):
        clients = cache.get("clients")
        clients = set() if clients is None else clients
        clients.add(obj)

    @classmethod
    def send_info(cls, ignore: (set, list)):
        pass




class EchoWebSocket(WebSocketHandler):
    """
    ws视图
    """
    clients = set()

    def open(self):
        self.clients.add(self)
        print("WebSocket opened")

    def send_message(self, message):
        self.write_message(u"You said: " + message)

    def on_message(self, message):
        [client.send_message(message=message) for client in self.clients]

    def on_close(self):
        self.clients.remove(self)
        print("WebSocket closed")



def make_app(debug: bool = False):
    handlers = [
        (r"/", TestGetHandler),
        (r"/ws_client", VideoView),
        (r"/echo", EchoWebSocket),
        (r"/push", PushView),
    ]
    kw = {
        "handlers": handlers,
        "template_path": template_path,
        "static_path": static_path,
        "debug": debug
    }
    return tornado.web.Application(**kw)


if __name__ == "__main__":
    application = make_app(debug=True)
    ssl_options = {
           "certfile": "/etc/nginx/key/1717636_www.x-bb.top.pem",
           "keyfile": "/etc/nginx/key/1717636_www.x-bb.top.key"
    }
    http_server = HTTPServer(application)
    http_server.listen(options.port)
    http_server.start(0)  # forks one process per cpu
    print("tornado server running on {} port...".format(options.port))
    IOLoop.current().start()

