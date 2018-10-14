# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from module.item_module import TempRecord
from tools_module import *
import json


app = Flask(__name__)
port = 7011


@app.route("/")
def index_func():
    return "hello world!"


@app.route("/query", methods=['post', 'get'])
def query_func():
    sn = get_arg(request, "sn", '')
    f = {"sn": sn}
    resp = TempRecord.exec("find", filter=f)
    if resp is None:
        mes = {"message": "none"}
    else:
        mes = {"message": "success"}
    return json.dumps(mes)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)