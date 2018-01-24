from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from image_server import app, port

http_server = HTTPServer(WSGIContainer(app))
http_server.bind(port)
# http_server.start(0)
http_server.start(0)
print("server running on {} port ...".format(port))
IOLoop.current().start()
