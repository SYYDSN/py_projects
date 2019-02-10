# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
import ujson
from flask_cors import CORS


app = Flask(__name__)
CORS(app=app)


"""基础的flask服务器,用作调试"""


@app.route("/")
def index_func():
    return "hello world"


@app.route("/user/user_login/", methods=['post', 'get'])
def user_login():
    resp = {"message": "success"}
    return  ujson.dumps(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7999, debug=True)
    pass