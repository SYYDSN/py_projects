# -*- coding: utf-8 -*-
from nameko.standalone.rpc import ClusterRpcProxy
import datetime


config = {"AMQP_URI": "pyamqp://remote_client:NewSpider-123@192.168.2.154"}


with ClusterRpcProxy(config=config) as cluster_rpc:
    r = cluster_rpc.greeting_server.hello.call_async("tom")
    print(r.result())
    print(datetime.datetime.now())


with ClusterRpcProxy(config=config) as cluster_rpc:
    r = cluster_rpc.greeting_server2.hello("jack")
    print(r)
    print(datetime.datetime.now())

import zerorpc

c = zerorpc.Client()
c.connect("tcp://0.0.0.0:4242")
print(c.add_42(12))