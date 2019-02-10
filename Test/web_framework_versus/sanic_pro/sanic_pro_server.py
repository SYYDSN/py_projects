# -*- coding: utf-8 -*-
from sanic import Sanic
from sanic import response


app = Sanic()


@app.route("/query/")
async def test(request):
    return response.text("Hello Sanic!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083)