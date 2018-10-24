from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from test_server import app, port
import bjoern
from waitress import serve
from meinheld import server
try:
    from gevent.wsgi import WSGIServer
except ImportError as e:
    print(e)
    from gevent.pywsgi import WSGIServer


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


# waitress windows和unix皆可,推荐
server_ini = {
    "app": app,
    "host": "0.0.0.0",
    "port": port,
    "connection_limit": 200,  # 连接限制
    "asyncore_use_poll": True
}
serve(**server_ini)


# meinheld 方式,部分c的py.
# server.listen(("0.0.0.0", port))
# server.run(app)


# gevent 部署方式
# server = WSGIServer(('0.0.0.0', port), app)
# server.serve_forever()