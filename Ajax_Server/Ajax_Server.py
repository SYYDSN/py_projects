# -*- coding: utf-8 -*-
from flask import Flask
from flask_cors import CORS
from flask import request
import json


app = Flask(__name__)
CORS(app)
port = 8015


def get_args(req):
    """一次性取出所有取参数集，注意，参数的值不能是json对象"""
    the_form = req.form
    arg_dict = {k: v for k, v in the_form.items()}
    if len(arg_dict) == 0:
        arg_dict = {k: v for k, v in req.args.items()}
    if len(arg_dict) == 0:
        arg_dict = req.json
    arg_dict = dict() if arg_dict is None else arg_dict
    return arg_dict


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/<path>', methods=['post', 'get'])
def common_func(path):
    args = get_args(request)
    mes = {"message": "success", 'data': args, "path": path}
    return json.dumps(mes)


if __name__ == '__main__':
    print("服务器运行于8015端口.....")
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
