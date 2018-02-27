#  -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import render_template
from flask_sse import sse
import json


app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')


@app.route("/")
def index_func():
    """文字聊天室页面"""
    return render_template("chat_room.html", sse=sse)


@app.route('/hello')
def publish_hello():
    mes = json.dumps({"message": "Hello!"})
    sse.publish(mes, type='greeting')
    return "Message sent!"


if __name__ == "__main__":
    app.run(port=8001, debug=True, threaded=True)