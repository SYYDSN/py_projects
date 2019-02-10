# -*- coding: utf-8 -*-
from japronto import Application
from module.md_module import Document


port = 7011
app = Application()


async def query_func(request):
    mes = {"message": "success"}
    args = request.query
    form = request.match_dict
    r = Document.paginate(where=dict())
    if r is None:
        mes['message'] = "Not Found!"
    else:
        mes['data'] = r
    resp = request.Response(text="ok")
    return resp


app.router.add_route(pattern="/query", handler=query_func)


if __name__ == "__main__":
    """
    和mongodb有兼容性问题,会报错:
    UserWarning: MongoClient opened before fork. Create MongoClient only after forking. 
    """
    app.run(host="0.0.0.0", port=port, debug=False, worker_num=2)
    pass