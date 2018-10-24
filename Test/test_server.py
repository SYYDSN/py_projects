# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import render_template
from module.item_module import TempRecord
from flask.views import MethodView
from tools_module import *
import random
import json
import time


app = Flask(__name__)
port = 7011


def require_login(f):
    """检测用户是否登录的装饰器,仅仅做示范"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")  # 检测session中的user_id
        if user_id is None:
            """没"""
            return redirect(url_for("reg_func"))
        else:
            """检查通过"""
            return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index_func():
    de = request.args.get("de")
    if de is None:
        return render_template("index.html", page_title="hello world")
    else:
        return redirect(url_for("name1"))


@app.route("/reg")
def reg_func():

    return "register page!"


@app.route("/query", methods=['post', 'get'])
def query_func():
    sn = get_arg(request, "sn", '')
    f = {"sn": sn}
    resp = TempRecord.exec("find", filter=f)
    if resp is None:
        mes = {"message": "none"}
    else:
        mes = {"message": "success"}
    mes['val'] = random.random()
    return json.dumps(mes)


@app.route("/query2", methods=['post', 'get'])
def query_func2():
    sn = get_arg(request, "sn", '')
    f = {"sn": sn}
    resp = TempRecord.exec("find", filter=f)
    if resp is None:
        mes = {"message": "none"}
    else:
        mes = {"message": "success"}
    mes['val'] = random.random()
    return json.dumps(mes)


class MyView(MethodView):
    """视图类"""
    def get(self):
        return "get"

    def post(self):
        return "post"


app.add_url_rule("/class", view_func=MyView.as_view("name1"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)