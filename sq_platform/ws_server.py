# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import session
from flask import render_template
from flask_socketio import SocketIO
import os


"""这是一个flask-socketio服务器,用于提供实时的消息传递"""


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socket_io = SocketIO(app)
port = 5006


@app.route("/")
def client_demo_func():
    """socketio客户端示范页面"""
    return render_template("socket_io/io_client_demo.html")


@socket_io.on("demo")
def message_handler_func(mes):
    """socketio接收到消息的时候"""
    print(mes)
    return "ok"


@socket_io.on("last_position")
def index_last_position_func(mes):
    print(mes)
    send_last_position("hello world")


def send_last_position(info):
    socket_io.emit("last_position", info)


@app.route("/test")
def test_func():
    mes = request.args.get("mes")
    data = {"mes": mes}
    send_last_position(data)
    return "ok"


if __name__ == "__main__":
    socket_io.run(app=app, host="0.0.0.0", port=port, debug=True)