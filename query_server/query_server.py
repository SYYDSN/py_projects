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
from module.code_module import CodeInfo
from module.file_module import TaskSync
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


mount_plugin(app)  # 注册jinja2的自定义过滤器
prev = None
count = 0


"""视图函数"""


@app.route('/favicon.ico')
def favicon_func():
    return send_file("static/image/favicon.ico")


@app.route("/query", methods=['get', 'post'])
def query_func():
    """查询条码信息"""
    global prev, count
    count += 1
    print("第{}条信息".format(count))
    prev = datetime.datetime.now() if prev is None else prev
    begin = datetime.datetime.now()
    s = "距离上次返回数据的时间间隔： {}".format((begin - prev).total_seconds())
    print(begin)
    print(s)
    mes = {"message": "success"}
    sn = get_arg(request, "sn", "")
    r = CodeInfo.query_code(code=sn)
    result = "{}, {}".format(sn, r)
    mes['result'] = result
    print(mes)
    end = datetime.datetime.now()
    print(end)
    s = "本次查询处理耗时： {}".format((end - begin).total_seconds())
    prev = end
    print(s)
    return json.dumps(mes)


@app.route("/upload", methods=['post'])
def upload_func():
    """同步任务结果/回传条码数据"""
    mes = TaskSync.upload(req=request)
    return json.dumps(mes)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
