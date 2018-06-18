from flask import Flask
from flask import render_template
from flask import request
import json
import time
import random
from flask import make_response


app = Flask(__name__)
port = 5678


@app.route('/hello')
def hello_world():
    return render_template("aa.html")


@app.route("/test")
def test_func():
    return render_template("test.html")


def allow_cros(info: dict):
    """根据字典生成一个跨域的response"""
    response = make_response(json.dumps(info))
    response.headers.set("Access-Control-Allow-Origin", "*")
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    allow_headers = "Referer,Accept,Origin,User-Agent"
    response.headers['Access-Control-Allow-Headers'] = allow_headers
    return response


@app.route("/delay", methods=['post', 'get'])
def delay_func():
    """模拟一个耗时的操作"""
    mes = {"message": "success"}
    time.sleep(random.randint(1, 5))
    resp = allow_cros(mes)
    return resp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
