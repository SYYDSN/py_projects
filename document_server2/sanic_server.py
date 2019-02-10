# -*- coding: utf-8 -*-
from module.md_module import Document
from sanic import Sanic
from sanic.response import json
import asyncio


app = Sanic()


@app.route("/")
async def test(request):
    key = request.args.get("key", 0)
    key = key if isinstance(key, int) else int(key)
    if key % 2 == 0:
        print("偶数")
    else:
        print("奇数")
        asyncio.sleep(10)
    return json("hello world")


@app.route("/query")
async def test2(request):
    resp = Document.paginate(where=dict())
    return json(resp)


if __name__ == "__main__":
    setting = {
        "host": "0.0.0.0",
        "port": 8000,
        "access_log": True,
        "debug": True,
        "workers": 8
    }
    app.run(**setting)
