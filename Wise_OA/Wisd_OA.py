# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask import request
from flask import session
from flask import send_file
from flask_session import Session
from views.manage_view import manage_blueprint
from my_filter import mount_plugin
import json
import datetime


app = Flask(__name__)
key_str = os.urandom(24)  # 生成密钥，为session服务。
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
app.register_blueprint(manage_blueprint)           # 注册平台操作视图
SESSION_TYPE = "redis"
Session(app)
port = 7012


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
