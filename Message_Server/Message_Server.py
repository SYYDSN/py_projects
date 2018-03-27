#  -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import make_response
from flask import render_template
from flask import render_template_string
from flask import send_file
from flask import request
from werkzeug.contrib.cache import RedisCache
from flask_session import Session
from log_module import get_logger
import sms_module
from tools_module import *
import os


secret_key = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
SESSION_TYPE = "redis"
app.config.from_object(__name__)
Session(app)


cache = RedisCache()
logger = get_logger()
port = 8000


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.before_request
def logger_request_info():
    """
    监控所有的请求信息
    :return:
    """
    headers = "headers: {}".format(request.headers)
    args_dict = "args: {}".format(get_args(request))
    logger.info(headers)
    logger.info(args_dict)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
