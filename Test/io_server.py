# -*- coding: utf-8 -*-
from uuid import uuid4
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import emit


"""socketio注意客户端必须用本项目中的socket.io.js,否则不支持中文"""

app = Flask(__name__)
port = 8100
secret = uuid4().hex
app.config['SECRET_KEY'] = secret
socketio = SocketIO(app)


@app.route("/io_client")
def io_client_func():
    return render_template("io_client.html")


@socketio.on('mes')
def handle_my_custom_event(json_str):
    print('received json: ' + str(json_str))
    emit("mes", json_str, broadcast=True)



if __name__ == '__main__':
    socketio.run(app, port=port, host="0.0.0.0")
    pass