# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import render_template
from flask_socketio import SocketIO
from flask_socketio import emit
from uuid import uuid4


"""socketio注意客户端必须用本项目中的socket.io.js,否则不支持中文"""


app = Flask(__name__)
secret = uuid4().hex
app.config['SECRET_KEY'] = secret
socketio = SocketIO(app)
port = 8500


"""一个celery的练习项目"""


@app.route('/')
def hello_world():
    return render_template("index.html")


@socketio.on('mes')
def handle_my_custom_event(json_str):
    print('received json: ' + str(json_str))
    emit("mes", json_str, broadcast=True)


@app.route("/listen", methods=['post', 'get'])
def listen_func():
    mes = request.args['mes'] if request.args.get("mes") else request.form.get("mes")
    if mes == "":
        return "error"
    else:
        socketio.emit("mes", {"mes": mes})
        return "ok"


if __name__ == '__main__':
    socketio.run(host="0.0.0.0", app=app, port=port)
