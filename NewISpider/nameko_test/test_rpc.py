# -*- coding: utf-8 -*-
from nameko.standalone.rpc import ClusterRpcProxy
import datetime
import requests
import zerorpc


config = {"AMQP_URI": "pyamqp://remote_client:NewSpider-123@192.168.2.154"}

count1 = list()
count11 = list()
count2 = list()
count22 = list()


def test1():
    global  count1
    begin = datetime.datetime.now()
    with ClusterRpcProxy(config=config) as cluster_rpc:
        r = cluster_rpc.greeting_server.hello("tom")
        # print(r)
        end = datetime.datetime.now()
        d = (end - begin).microseconds
        count1.append(d)


def test11(cluster_rpc):
    global  count11
    begin = datetime.datetime.now()
    r = cluster_rpc.greeting_server.hello("tom")
    # print(r)
    end = datetime.datetime.now()
    d = (end - begin).microseconds
    count11.append(d)


def test2():
    global  count2
    begin = datetime.datetime.now()
    r = requests.get("http://127.0.0.1:8000/")
    # print(r.status_code)
    end = datetime.datetime.now()
    d = (end - begin).microseconds
    count2.append(d)


def test22(client):
    global  count22
    begin = datetime.datetime.now()
    r = client.add_42(12)
    # print(r)
    end = datetime.datetime.now()
    d = (end - begin).microseconds
    count22.append(d)


def add(l: list):
    r = 0
    for x in l:
        r += x
    return r


if __name__ == "__main__":
    begin = datetime.datetime.now()
    for x in range(100):
        test1()
    while len(count1) == 100 or (datetime.datetime.now() - begin).total_seconds() > 30:
        print(len(count1))
        print("count1: {}".format(add(count1)))
        break

    begin = datetime.datetime.now()
    with ClusterRpcProxy(config=config) as cluster_rpc:
        for i in range(100):
            test11(cluster_rpc)
    while len(count11) == 100 or (datetime.datetime.now() - begin).total_seconds() > 30:
        print(len(count11))
        print("count11: {}".format(add(count11)))
        break

    begin = datetime.datetime.now()
    for x in range(100):
        test2()
    while len(count2) == 100 or (datetime.datetime.now() - begin).total_seconds() > 30:
        print(len(count2))
        print("count2: {}".format(add(count2)))
        break

    begin = datetime.datetime.now()
    c = zerorpc.Client()
    c.connect("tcp://0.0.0.0:4242")
    # c.connect("tcp://47.98.113.173:4242")
    for x in range(100):
        test22(c)
    while len(count22) == 100 or (datetime.datetime.now() - begin).total_seconds() > 30:
        print("count22: {}".format(add(count22)))
        break

    pass