# -*- coding: utf-8 -*-
from japronto import Application
from module.item_module import TempRecord


port = 7011
app = Application()


async def query_func(request):
    mes = {"message": "success"}
    args = request.query
    form = request.match_dict
    sn = form['sn'] if form.get('sn') else args.get("sn", "")
    f = {"sn": sn}
    r = TempRecord.find_one(filter_dict=f)
    if r is None:
        mes['message'] = "Not Found!"
    else:
        mes['result'] = str(r['_id'])
    resp = request.Response(text="ok")
    return resp



app.router.add_route(pattern="/query", handler=query_func)


if __name__ == "__main__":
    """
    和mongodb有兼容性问题,会报错:
    UserWarning: MongoClient opened before fork. Create MongoClient only after forking. 
    """
    app.run(host="0.0.0.0", port=port, debug=True, worker_num=1)
    pass