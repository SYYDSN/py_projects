# -*- coding: utf-8 -*-
import requests
import time
import threading


def short_req(n):
    u = "http://127.0.0.1:7001/test"
    r = requests.get(u)
    print("{} short: {}".format(n, r.status_code))


def long_req(n):
    u = "http://127.0.0.1:7001/test?num=1"
    r = requests.get(u)
    print("{} long: {}".format(n, r.status_code))


count1 = 1
count2 = 1
while count1 < 100:
    t1 = threading.Thread(target=long_req, args=(count1,))
    t2 = threading.Thread(target=short_req, args=(count2,))
    t1.start()
    t2.start()
    # time.sleep(1)
    count1 += 1
    count2 += 1