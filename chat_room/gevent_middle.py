__author__ = 'Administrator'
from gevent.wsgi import WSGIServer
from flask_server import app
import ext_tools
logger = ext_tools.get_logger_everyday("gevent")
logger.info("begin....")
http_server = WSGIServer(('', 9014), app)
print("中间件开始运行...")
http_server.serve_forever()