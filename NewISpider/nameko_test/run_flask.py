# -*- coding: utf-8 -*-
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from nameko_test.flask_app import app


"""跑flask_app的服务"""


# tornado方式部署,异步模式.
http_server = HTTPServer(WSGIContainer(app))
http_server.bind(8000)
http_server.start(0)
# http_server.start(1)
print("server running on {} port ...".format(8000))
IOLoop.current().start()