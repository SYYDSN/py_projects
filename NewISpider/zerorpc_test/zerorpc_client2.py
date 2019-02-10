# -*- coding: utf-8 -*-
import zerorpc
import requests
import datetime


c = zerorpc.Client()
c.connect("tcp://127.0.0.1:4242")  # 连接到rpc服务器

print(c.test())