from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from flask_server import app, port

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(port)
IOLoop.instance().start()