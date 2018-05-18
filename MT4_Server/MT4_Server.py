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
import json
from module.item_module import RawRequestInfo
from tools_module import *
import os


secret_key = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
# app.config['SERVER_NAME'] = "127.0.0.1:8001"  此域名下的所有子域名的session都会接受
app.config.from_object(__name__)
Session(app)


cache = RedisCache()
logger = get_logger()
port = 8008


@app.route('/', methods=['post', 'get'])
def hello_world():
    return 'Hello World!'


@app.route("/<key1>/<key2>", methods=['get', 'post'])
def every_event_func(key1, key2):
    """监听所有的消息"""
    mes = {"message": "success"}
    args = RawRequestInfo.get_init_dict(request)
    mes['data'] = args
    return json.dumps(mes)


@app.before_request
def logger_request_info():
    """
    监控所有的请求信息
    :return:
    """
    # headers = "headers: {}".format(request.headers)
    # args = "args: {}".format(request.args)
    # form = "form: {}".format(request.form)
    # json = "json: {}".format(request.json)
    # logger.info(headers)
    # logger.info(args)
    # logger.info(form)
    # logger.info(json)
    RawRequestInfo.record(request)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
