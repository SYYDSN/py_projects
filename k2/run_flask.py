from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from KY_server import app, port
import bjoern
import cherrypy
from cherrypy import _cpwsgi_server
from meinheld import server
from gevent.wsgi import WSGIServer


# tornado方式部署,异步模式.
# http_server = HTTPServer(WSGIContainer(app))
# http_server.bind(port)
# http_server.start(0)
# # http_server.start(1)
# print("server running on {} port ...".format(port))
# IOLoop.current().start()


# bjoern部署方式,c语言,异步模式.注意,这种方式不支持ssl,也不能自定义headers
# print("bjoern running on {} port ..".format(port))
# bjoern.listen(app, "0.0.0.0", port)
# bjoern.run()


# cherrypy部署方式,py语言,线程池模式.生产环境使用较多
# cherrypy.tree.graft(app, "/")
# server = cherrypy._cpserver.Server()
# server.socket_host = '0.0.0.0'
# server.socket_port = port
# server.thread_pool = 1500
# server.thread_pool_max = 5000
# server.start()


# meinheld 方式,部分c的py.
server.listen(("0.0.0.0", port))
server.run(app)


# gevent 部署方式
# server = WSGIServer(('0.0.0.0', port), app)
# server.serve_forever()