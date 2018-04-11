# -*-coding:utf-8-*-
from flask import Flask
from flask import request
from extends_func import add_uuid


port = 7777
app = Flask(__name__)


@app.route("/")
def hello():
    name = request.args.get("name")
    res = add_uuid(name)
    return res


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
