# -*-coding:utf-8-*-
from tornado import gen
import tornado.web
import os
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler


class X(RequestHandler):
    @gen.coroutine
    def get(self):
        http_client = AsyncHTTPClient()
        url = 'http://www.baidu.com'
        response = yield http_client.fetch(url)
        # In Python versions prior to 3.3, returning a value from
        # a generator is not allowed and you must use
        #   raise gen.Return(response.body)
        # instead.
        self.write(response.body)

    def post(self):
        self.get()


class B(RequestHandler):
    @gen.coroutine
    def get(self):
        self.write("ok")

    def post(self):
        self.get()


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
    "login_url": "/login",
    "xsrf_cookies": True,
}
application = tornado.web.Application([
    (r"/baidu", X),
    (r"/", B),
    (r"/(apple-touch-icon\.png)", tornado.web.StaticFileHandler,
     dict(path=settings['static_path'])),
], **settings)

if __name__ == '__main__':
    server = HTTPServer(application)
    server.listen(8888)
    IOLoop.current().start()
    print("begin...")
