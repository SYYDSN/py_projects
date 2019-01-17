# -*- coding: utf-8 -*-
from flask import Flask
from flask_cors import CORS
from data_module import data
import json


"""
ajax测试服务器
"""


app = Flask(__name__)
port = 8001                      # 配置端口


@app.route("/", methods=['post', 'get'])
def index():
    return "hello world!"


@app.route("/<key>", methods=['post', 'get'])
def common_func(key):
    values = data.get(key)
    mes = {"message": "success"}
    if values is None:
        mes['message'] = "not found!"
    else:
        mes['data'] = values
    return json.dumps(mes)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
