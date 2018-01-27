# -*- coding: utf-8 -*-
from flask import Flask
import json

"""mongodb的日志服务器,用于监控日志变化"""

app = Flask(__name__)
port = 5100

@app.route("/hello")
def hello_func():
    return json.dumps({"hello": "world!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)