# -*- coding: utf-8 -*-
from aiohttp import web


route = web.RouteTableDef()
app = web.Application()
port = 8084


@route.get('/query/')
async def hello_world(request):
    return web.Response(text="Hello, Aio!")




async def my_web_app():
    app = web.Application()
    app.add_routes(route)
    return app



if __name__ == '__main__':
    web.run_app(app=my_web_app(), host="0.0.0.0", port=port)
