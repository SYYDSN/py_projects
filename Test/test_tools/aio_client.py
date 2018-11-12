# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import datetime
from tornado.httpclient import AsyncHTTPClient
from tornado.gen import coroutine
from gevent import monkey
import random


"""aiohttp客户端"""


urls =[
    "https://www.v2ex.com",
    "https://blog.csdn.net/u013851082/article/details/53942947",
    "https://flask-aiohttp.readthedocs.io/en/latest/",
    "https://github.com/Hardtack/Flask-aiohttp/blob/master/setup.py",
    "https://www.baidu.com"
]


async def req_test(ses, url):
    begin = datetime.datetime.now()
    async with ses.get(url) as resp:
            data = await resp.text()
            end = datetime.datetime.now()
            return url, (end - begin).total_seconds(), data


async def main():
    for url in urls:
        async with aiohttp.ClientSession() as session:
            resp = await req_test(session, url)
            print(resp)


async def req2(url):
        client = AsyncHTTPClient()
        resp = await client.fetch(url)
        print(resp.request.url)


def ll():
    res = []
    for index, url in enumerate(urls):
        print("No_{} {}".format(index, url))
        res.append(req2(url))
    return asyncio.wait(fs=res)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.run_until_complete(req2())
    loop.run_until_complete(ll())
    pass