# -*-coding:utf-8-*-
from flask import Flask

port = 7777
app = Flask(__name__)


@app.route("/")
def hello():
    return "ok"


if __name__ == "__main__":
    app.run(port=port)
