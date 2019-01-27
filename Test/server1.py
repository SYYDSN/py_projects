# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import abort
from flask import render_template
from werkzeug.contrib.cache import SimpleCache
import json
import random
import datetime


port = 8000
cache = SimpleCache()
app = Flask(__name__)


def aab(now: datetime.datetime):
    return now.strftime("%F")


app.jinja_env.filters['aab'] = aab


@app.route("/")
def index_func2():
    return abort(403)

@app.route("/reg", methods=['post', 'get'])
def index_func():
    method = request.method.lower()
    if method == "get":
        return render_template("index.html", page_title="登录")
    else:
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        mes = {"message": "success"}
        return json.dumps(mes)


@app.route("/data/<key>", methods=['get', 'post'])
def data_func(key):
    data = cache.get("data")
    data = dict() if data is None else data
    if key == "view":
        return json.dumps(data)
    elif key == "update":
        user_name = request.args.get("user_name")
        data['user_name'] = user_name
        cache.set('data', data, timeout=5 * 60)
        return "ok"
    else:
        return abort(401)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)