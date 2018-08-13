# -*-coding:utf-8-*-
from flask import Flask
from flask import request
from flask import session
from flask_session import Session
import os
from flask import render_template
from flask_socketio import SocketIO
import json
from module.quotations_module import Quotation


port = 8001
secret_key = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
# app.config['SERVER_NAME'] = "127.0.0.1:8001"  此域名下的所有子域名的session都会接受
app.config.from_object(__name__)
Session(app)
socket_io = SocketIO(app)


@app.route('/')
def hello_world():
    return 'Hello quotations_server!'


@app.route("/quotations/listen", methods=['post', 'get'])
def quotations_func():
    """"
    监听发送来的报价,并使用socketio向所有客户端发送消息,注意:
    1. 平台有优先级.优先级可以人为排序.
    2. 同一时间,只允许根据一个报价服务器的报价发布.
    3. 每次接收到报价都要检查一下当前的报价服务器是否是允许发布报价的服务器.
        如果是,那就发布报价,如果不是就竞争发布权.
            发布报价时:
                     比较上一次的报价,如果全部相等.并持续超过5秒,认为停盘.
                     确认停盘后,让出发布权.直到所有的服务器处于停盘状态.
            竞争发布权时:
                    如果当前的发布服务器超过2秒没有发布报价.则竞争发布权成功.
                    否则保持沉默. 保持沉默的报价,不写入数据库.
    """
    mes = {"message": "unknown error"}
    price_list = Quotation.analysis_request(req=request, auto_save=True)
    if isinstance(price_list, list):
        Quotation.send_io_message(init_list=price_list, event="price", io=socket_io)
        mes['message'] = "success"
    else:
        pass
    return json.dumps(mes)


@socket_io.on("login")
def quotations_func(mes):
    """接收客户端连接的示范"""
    print(mes)
    sid = request.sid  # io客户端的sid, socketio用此唯一标识客户端.
    can = False
    host = request.host
    host_list = ['127.0.0.1']
    if host in host_list:
        can = True
    elif host.startswith("192.168") or host.startswith("local") or host.endswith("91.master.cn"):
        can = True
    else:
        pass
    if can:
        socket_io.emit(event="login", data=json.dumps({"message": "connect refuse!"}))
        socket_io.server.disconnect(sid)
    else:
        socket_io.emit(event="login", data=json.dumps({"message": "connect success!"}))


"""示范部分"""


@app.route("/listen", methods=['post', 'get'])
def listen_func():
    """"监听发送来的消息,并使用socketio向所有客户端发送消息"""
    mes = {"message": "unknown error"}
    data = request.args['data'] if request.args.get('data') else request.form.get('data')
    if data is not None:
        socket_io.emit(data=data, event="mes")
        mes['message'] = "success"
    else:
        pass
    return json.dumps(mes)


@app.route("/test")
def test_func():
    return render_template("test.html")


if __name__ == '__main__':
    socket_io.run(app=app, host="0.0.0.0", port=port, debug=True)
