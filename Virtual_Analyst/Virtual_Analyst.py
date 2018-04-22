#  -*- coding: utf-8 -*-
from flask import Flask
import os
from werkzeug.contrib.cache import RedisCache
from flask_session import Session
from logging import getLogger
from tools_module import *


secret_key = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
SESSION_TYPE = "redis"
app.config.from_object(__name__)
Session(app)


cache = RedisCache()
logger = get_logger()
port = 8600


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
