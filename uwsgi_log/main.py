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
from tools_module import *
import time


key_str = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
app.config['THREADED'] = True            # 多线程开启
SESSION_TYPE = "redis"
Session(app)
port = 7004


@app.route('/')
def hello_world():
    args = get_args(request)
    print(args)
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)
