# -*- coding:utf-8 -*-
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from main_server import app
from main_server import port
import platform

if platform.system() == "Windows":
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port)
    print("windows平台，运行{0}端口".format(port))
    IOLoop.instance().start()
else:
    http_server = HTTPServer(WSGIContainer(app))
    http_server.bind(port)
    http_server.start(2)  # 0 is forks one process per cpu
    print("linux平台，运行{0}端口".format(port))
    IOLoop.current().start()
