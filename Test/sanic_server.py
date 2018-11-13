# -*- coding: utf-8 -*-
from sanic import Sanic
from sanic import response
from tools_module import get_arg
from module.item_module import TempRecord


port = 7011
app = Sanic()


@app.route("/query", methods=["GET", "POST"])
async def query_func(request):
    """查询条码"""
    mes = {"message": "success"}
    sn = get_arg(request, "sn", "")
    f = {"sn": sn}
    r = TempRecord.find_one(filter_dict=f)
    if r is None:
        mes['message'] = "Not Found!"
    else:
        mes['result'] = str(r['_id'])
    return response.json(mes)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
    pass