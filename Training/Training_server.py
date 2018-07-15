# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import session
from flask_session import Session
import os
import datetime
from views.flash_view import flash_blueprint


"""训练服务器"""


port = 5678
key_str = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
SESSION_TYPE = "redis"
app.config.from_object(__name__)
app.register_blueprint(flash_blueprint)  # 注册闪卡训练蓝图
Session(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    if __name__ == '__main__':
        app.run(host="0.0.0.0", port=port, debug=True, threaded=True)  # 一般调试模式
