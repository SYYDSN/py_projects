# -*- coding: utf-8 -*-
import zerorpc
import requests
import datetime


c = zerorpc.Client()
c.connect("tcp://192.168.2.154:4242")  # 连接到rpc服务器

user_name1 = "jack"
user_name2 = "tom"
b1 = datetime.datetime.now()
n = 500
for i in range(n):
    c.add_user(user_name1)
    c.add_user(user_name2)
    print(c.all_user(), end="    ")
e1 = datetime.datetime.now()
print()
print("{}次rpc调用耗时: {}秒".format(n, (e1 - b1).total_seconds()))
b2 = datetime.datetime.now()
ses = requests.Session()
u = "http://127.0.0.1:8003/some_api"
params = {"user_name": user_name1}
for i in range(n):
    r = ses.get(url=u, params=params)
    print(r.text, end="    ")
e2 = datetime.datetime.now()
print()
print("{}次restful调用耗时: {}秒".format(n, (e2 - b2).total_seconds()))