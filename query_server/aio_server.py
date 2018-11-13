# -*- coding: utf-8 -*-
import aiohttp
from aiohttp import BodyPartReader
from aiohttp import web
from module.item_module import TempRecord


port = 7013
app = web.Application()
make_resp = web.Response
make_json = web.json_response
routes = web.RouteTableDef()


@routes.get("/query")
@routes.post("/query")
async def query_func(request):
    """查询条码"""
    mes = {"message": "success"}
    args = request.query
    form = await request.post()
    sn = form['sn'] if form.get('sn') else args.get("sn", "")
    f = {"sn": sn}
    r = TempRecord.find_one(filter_dict=f)
    if r is None:
        mes['message'] = "Not Found!"
    else:
        mes['result'] = str(r['_id'])
    return make_json(mes)


if __name__ == "__main__":
    app.router.add_routes(routes)
    aiohttp.web.run_app(app=app, host="0.0.0.0", port=port, backlog=128)
    pass