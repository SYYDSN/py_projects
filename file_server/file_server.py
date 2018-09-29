# -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import send_from_directory
from flask import render_template
from flask import make_response
from flask import request
from flask import session
from flask_session import Session
from flask import redirect
import json
import datetime
import os
import json
from views.image_view import image_blueprint
from views.api_view import api_blueprint
from tools_module import *
import time


key_str = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
app.config['THREADED'] = True            # 多线程开启
app.register_blueprint(image_blueprint)  # 注册图片视图
app.register_blueprint(api_blueprint)  # 注册通用api视图
SESSION_TYPE = "redis"
Session(app)
port = 7001


@app.route("/")
def welcome():
    return "hello world"


@app.route("/test", methods=['post', 'get'])
def test_func():
    num = get_arg(request, "num", "")
    print(get_args(request))
    if num == "1":
        time.sleep(3)
        return "no"
    else:
        return "yes"


@app.before_request
def logger_request_info():
    """
    监控所有的请求信息

    :return:
    """
    pass


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)
