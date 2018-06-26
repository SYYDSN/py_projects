# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from flask import session
from flask_session import Session
from flask import redirect
from views.driver_view import web_blueprint
from views.identity_view import identity_blueprint
import json
import datetime
import os


port = 7001
key_str = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
SESSION_TYPE = "redis"
app.config.from_object(__name__)
app.register_blueprint(web_blueprint)
app.register_blueprint(identity_blueprint)
Session(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.before_request
def show_request_before():
    """在此检查请求源地址是否合法,检查的方法待定"""
    pass


@app.after_request
def allow_cross_domain(response):
    """允许跨域资源访问管理"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    allow_headers = "Referer,Accept,Origin,User-Agent"
    response.headers['Access-Control-Allow-Headers'] = allow_headers
    # 也可以在此设置cookie
    # resp.set_cookie('username', 'the username')
    return response




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)  # 一般调试模式
