# -*- coding: utf-8 -*-
from sanic import Sanic


app = Sanic()
port = 9519


@app.route("/", methods=['post', 'get'])
async def hello(request):
    return "hello Bob!"


if __name__ == "__main__":
    setting = {
        "host": "0.0.0.0",
        "port": port,
        "debug": True,
        "workers": 1,
        "ssl": None
    }
    app.run(**setting)
