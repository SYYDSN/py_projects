# -*- coding: utf-8 -*-
import os
import sys
__root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __root_path not in sys.path:
    sys.path.append(__root_path)
import requests
import datetime
from tornado.httpclient import AsyncHTTPClient
import asyncio
import urllib.parse
import threading
import time

url = "http://127.0.0.1:7011/query"
data = {"sn": "34444444"}


async def asy(n):
    client = AsyncHTTPClient()
    count = 0
    begin = datetime.datetime.now()
    for i in range(n):
        resp = await client.fetch(url, method='POST', body=urllib.parse.urlencode(data))
        if resp.code == 200:
            count += 1
            # print(resp.body)
    end = datetime.datetime.now()
    delta = (end - begin).total_seconds()
    print("异步查询{}个查询耗时{}秒,成功率: {}%".format(n, delta, (count / n) * 100))


def batch_req(n):
    with requests.Session() as ses:
        count = 0
        begin = datetime.datetime.now()
        for i in range(n):
            resp = ses.post(url, data=data)
            if resp.status_code == 200:
                count += 1
        end = datetime.datetime.now()
        delta = (end - begin).total_seconds()
        print("顺序查询{}个查询耗时{}秒,成功率: {}%".format(n, delta, (count / n) * 100))


def req(m, count):
    with requests.Session() as ses:
        m = int(m)
        for i in range(m):
            resp = ses.post(url, data=data)
            if resp.status_code == 200:
                count['val'] = count['val'] + 1
    count['status'] = True


def th(n):
    begin = datetime.datetime.now()
    count1 = {"val": 0, "status": False}
    count2 = {"val": 0, "status": False}
    count3 = {"val": 0, "status": False}
    count4 = {"val": 0, "status": False}
    t1 = threading.Thread(target=req, args=(n/4, count1,), daemon=True)
    t2 = threading.Thread(target=req, args=(n/4, count2,), daemon=True)
    t3 = threading.Thread(target=req, args=(n/4, count3,), daemon=True)
    t4 = threading.Thread(target=req, args=(n/4, count4,), daemon=False)
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    while not (count1['status'] and count2['status'] and count3['status'] and count4['status']):
        time.sleep(0.0000001)
    end = datetime.datetime.now()
    delta = (end - begin).total_seconds()
    count = count1['val'] + count2['val'] + count3['val'] + count4['val']
    print("4线程查询{}个查询耗时{}秒,成功率: {}%".format(n, delta, (count / n) * 100))


if __name__ == "__main__":
    # batch_req(2000)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asy(2000))
    th(2000)
    pass