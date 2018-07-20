#  -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import render_template
from flask_session import Session
from user_module import User
from module.data.pickle_data import query_chart_data
from tools_module import *
from module.item_module import *
from views.mt4_view import mt4_blueprint
import os


secret_key = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
# app.config['SERVER_NAME'] = "127.0.0.1:8001"  此域名下的所有子域名的session都会接受
app.config.from_object(__name__)
app.register_blueprint(mt4_blueprint)  # 注册监听mt4后台发送过来的消息的蓝图
Session(app)


cache = RedisCache()
logger = get_logger()
port = 8000