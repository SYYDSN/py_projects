# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from tornado import gen
from tornado.ioloop import IOLoop


class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        self.write("Hello, Tornado!")

def make_app():
    return tornado.web.Application([
        (r"/query/", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    server = HTTPServer(app)
    app.listen(8085)
    server.start(0)  # forks one process per cpu
    print("tornado server run on 8085....")
    IOLoop.current().start()
