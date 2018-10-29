# -*- coding: utf-8 -*-
import os
from flask import Flask
from views.root_view import root_blueprint
from flask import session
from flask import send_file
from flask_session import Session
from orm_module import FlaskUrlRule
import datetime


app = Flask(__name__)
key_str = os.urandom(24)  # 生成密钥，为session服务。
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
app.register_blueprint(root_blueprint)           # 注册管理员视图
SESSION_TYPE = "redis"
Session(app)
port = 7012


@app.route('/favicon.ico')
def favicon_func():
    return send_file("static/image/favicon.ico")


"""获取路由规则,必须在最后部分"""


FlaskUrlRule.init(flask_app=app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
