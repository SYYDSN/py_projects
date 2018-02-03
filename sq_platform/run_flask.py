# from tornado.wsgi import WSGIContainer
# from tornado.httpserver import HTTPServer
# from tornado.ioloop import IOLoop
from flask_server import app, port
import bjoern


# http_server = HTTPServer(WSGIContainer(app))
# http_server.bind(port)
# # http_server.start(0)
# http_server.start(1)
# print("server running on {} port ...".format(port))
# IOLoop.current().start()


# bjoern部署方式
print("bjoern running on {} port ..".format(port))
bjoern.run(app, "0.0.0.0", port)

