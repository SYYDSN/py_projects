# -*- coding: utf-8 -*-
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from query_server import app, port
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
    "connection_limit": 400,  # 连接限制
    "asyncore_use_poll": True
}
serve(**server_ini)


# meinheld 方式,部分c的py.
# server.listen(("0.0.0.0", port))
# server.run(app)


# gevent 部署方式
# server = WSGIServer(('0.0.0.0', port), app)
# server.serve_forever()


"""
gunicorn的部署方式 需要virtualenv支持
gunicorn  --config=gunicorn.py test_server:app
"""

"""
uwsgi 部署方式.
1. 安装uwsgi 
    sudo apt install uwsgi 
    或者 pip install uwsgi
2. 安装python3插件
    apt install uwsgi-plugin-python3
    或者直接 sudo apt install uwsgi-plugins-all 安装所有的插件
uwsgi --http-socket 127.0.0.1:7011 --plugin python3 --wsgi-file test_server.py --callable app --process 8 --threads 2
"""