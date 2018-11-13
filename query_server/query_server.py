# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask import request
from views.manage_view import manage_blueprint
from flask import session
from flask import send_file
from module.item_module import TempRecord
from tools_module import get_arg
from flask_session import Session
from my_filter import mount_plugin
from orm_module import FlaskUrlRule
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
port = 7012  # 7012是管理平台的端口, 7013是异步查询平台的端口, 7014是websocket查询的接口


"""扩展jinja2过滤器"""

mount_plugin(app)


"""视图函数"""


@app.route('/favicon.ico')
def favicon_func():
    return send_file("static/image/favicon.ico")


@app.route("/query", methods=['get', 'post'])
def query_func():
    """查询条码信息"""
    mes = {"message": "success"}
    sn = get_arg(request, "sn", "")
    result = "{}, {}".format(sn, 1)
    mes['result'] = result
    return json.dumps(mes)


@app.route("/upload", methods=['post'])
def upload_func():
    """查询条码信息"""
    mes = {"message": "success"}
    sn = get_arg(request, "sn", "")
    result = "{}, {}".format(sn, 1)
    mes['result'] = result
    return json.dumps(mes)



"""获取路由规则,必须在最后部分"""


FlaskUrlRule.init(flask_app=app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
