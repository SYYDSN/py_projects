# -*- coding: utf-8 -*-
from tornado.httpclient import AsyncHTTPClient
import json
import urllib.parse
from tornado.httpclient import HTTPResponse


"""
使用tornado的异步客户端实现的requests
"""

count = 0


def ge_client() -> AsyncHTTPClient:
    """
    返回一个AsyncHTTPClient实例
    :return:
    """
    client = AsyncHTTPClient()
    return client


async def fetch(url: str, data: dict = None, method: str = "get", client: AsyncHTTPClient = None, headers: dict = None,
                encoding: str = "utf-8", callbacks: list = None) -> HTTPResponse:
    """
    使用tornado.httpclient.HTTPResponse实现的异步requests函数.这是一个异步函数.
    1. 如果你在其他函数内部调用.记得使用await.
    2. 如果你直接运行此函数:
        import asyncio
        u = "http://127.0.0.1:7011/query"
        loop = asyncio.get_event_loop()
        data = {"sn": "12", "name": "tom"}
        resp = loop.run_until_complete(asyncio.wait(fs=[fetch(url=u, method="post", data=data)]))
        print(resp)

    :param url: 请求地址
    :param method: 请求方法
    :param data: 请求参数
    :param client: 一个AsyncHTTPClient实例或者None
    :param headers: 请求头
    :param encoding: 编码
    :param callbacks: 回调函数
    :return: HTTPResponse
    """
    client = client if isinstance(client, AsyncHTTPClient) else AsyncHTTPClient()
    method = "GET" if method is None else method.upper()
    data = dict() if data is None else data
    data = {k: v if isinstance(v, (float, int)) else (v if isinstance(v, str) else str(v)) for k, v in data.items()}
    url = url.strip()
    if url.endswith("?"):
        url = url.rstrip("?")
    else:
        url = url.rstrip("&")
    if method == "GET":
        p = ""
        for k, v in data.items():
            p += "&{}={}".format(k, v)
        p = p.rstrip("&")
        if url.find("?") != -1:
            url += p
        else:
            p = p.lstrip("&")
            p = "?{}".format(p)
            url += p
        resp = await client.fetch(request=url, method=method, headers=headers)
    else:
        body = urllib.parse.urlencode(query=data, encoding=encoding)
        resp = await client.fetch(request=url, method=method, body=body, headers=headers)
    if callbacks is None or len(callbacks) == 0:
        pass
    else:
        for func in callbacks:
            func(resp)
    return resp


def batch_fetch_demo() -> None:
    """
    使用tornado.httpclient.HTTPResponse实现的异步批量requests函数的示范
    调用方法
    import asyncio
    fs = [fetch(url, data)for x in range(10)]   # 返回的是一个生成器对象
    loop = asyncio.get_event_loop()
    resp = loop.run_until_complete(asyncio.wait(fs=fs))
    print(resp)
    """
    pass


def async_test(num: int = 10):
    """
    异步压力测试函数
    :param num:
    :return:
    """
    u = "http://127.0.0.1:7011/query"
    u = "http://192.168.1.112:7011/query"
    data = {"sn": "12", "name": "tom"}
    def inner(res):
        global count
        r = json.loads(res.body)
        count += 1
    q = list()
    for x in range(num):
        cli = ge_client()
        q.append(fetch(url=u, data=data, client=cli, callbacks=[inner]))
    return q


if __name__ == "__main__":
    import asyncio
    import datetime
    # u = "http://127.0.0.1:7011/query"
    # data = {"sn": "12", "name": "tom"}
    loop = asyncio.get_event_loop()
    # resp = loop.run_until_complete(asyncio.wait(fs=[fetch(url=u, method="post", data=data)]))
    # print(resp)
    """测试async_test"""
    all_req = 2000
    begin = datetime.datetime.now()
    loop.run_until_complete(asyncio.wait(fs=async_test(all_req)))
    end = datetime.datetime.now()
    delta = (end - begin).total_seconds()
    print("{}个连接,耗时{}秒,成功率{}%".format(all_req, delta, round((count / all_req) * 100, 2)))
    pass