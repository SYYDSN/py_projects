from flask import Flask
from flask import request
from flask import session
from flask_session import Session
from flask import redirect
import json
import datetime
import os
from module.item_module import RawWebChatMessage
from tools_module import *
from mongo_db import cache


keystr = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = keystr  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
SESSION_TYPE = "redis"
Session(app)
port = 8080


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/message", methods=['post', 'get'])
def message_func():
    """接收微信发来的消息"""
    mes = {"message": "success"}
    return json.dumps(mes)


@app.before_request
def logger_request_info():
    """
    监控所有的请求信息
    :return:
    """
    headers = {k: v for k, v in request.headers.items()}
    args = {k: v for k, v in request.args.items()}
    form = {k: v for k, v in request.form.items()}
    json_data = None if request.json is None else {k: v for k, v in request.headers.items()}
    ip = get_real_ip(request)
    now = datetime.datetime.now()
    data = {
        "ip": ip,
        "headers": headers,
        "args": args,
        "form": form,
        "json": json_data,
        "time": now
    }
    mes = RawWebChatMessage(**data)
    mes.save_plus()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
