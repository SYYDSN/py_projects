# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from nameko_test.hello_world import GreetingService
from flask import send_file

app = Flask(__name__)


"""和rpc做对比"""


@app.route("/<key>")
def index_func(key):
    name = request.args.get("name")
    a = GreetingService()

    return a.hello(name=name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
    pass