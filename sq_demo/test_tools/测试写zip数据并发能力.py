# -*- coding: utf-8 -*-
import requests
import grequests
import threading
import shutil
import os
import datetime
import math


def create_file(n):
    file_path = "/home/walle/work/temp3/2017_08_01_18_1_28.zip"
    dir_path = "/home/walle/work/temp3"
    raw = datetime.datetime.strptime('2017-12-12 01:00:00', "%Y-%m-%d %H:%M:%S")

    for x in range(n):
        detal = datetime.timedelta(minutes=5 * (x + 1))
        d = raw + detal
        d = d.strftime("%Y_%m_%d_%H_%M_%S")
        shutil.copy2(file_path, os.path.join(dir_path, "{}.zip").format(d))


# create_file(2000)


def post_img(file_path):
    """post一个文件"""
    remote = {"url": "http://192.168.0.106:5000/api/add_driving_data",
              "headers": {"auth_token": "814c25d8e1df45e0ab91ef38980664db"}}
    remote = {"url": "http://127.0.0.1:5000/api/add_driving_data",
             "headers": {"auth_token": "1cc55e2649f34e2382382d10a3ecb164"}}

    files = {"driving_data": open(file_path, 'rb')}

    r = requests.post(remote['url'], headers=remote['headers'], files=files)
    print(r.status_code)
    print(r.json())


count = 0


def post_img2(file_path):
    """post一个文件"""
    remote = {"url": "http://safego.org:5000/api/add_driving_data",
             "headers": {"auth_token": "1cc55e2649f34e2382382d10a3ecb164"}}
    remote = {"url": "http://safego.org:5000/api/add_driving_data",
             "headers": {"auth_token": "13ea1238bfeb4d78965b7149aa4d733d"}}

    remote = {"url": "http://127.0.0.1:5000/api/add_driving_data",
              "headers": {"auth_token": "39e7e6c7cc7d448190679bcd27b443fc"}}

    files = {"driving_data": open(file_path, 'rb')}

    r = grequests.post(remote['url'], headers=remote['headers'], files=files)
    return r


def run():
    for x in os.listdir("/home/walle/work/temp3"):
        post_img(os.path.join("/home/walle/work/temp3", x))


def run2():
    """异步压力测试"""
    paths = [os.path.join("/home/walle/work/temp3", x) for x in os.listdir("/home/walle/work/temp3")]
    l = len(paths)
    step = 1
    max_count = 1
    ran = int(math.ceil(l / step))
    global count
    for i in range(ran):
        begin = i * step
        if begin > max_count:
            break
        end = ((i + 1) * step) - 1
        end = l if end > l else end
        print(begin, end)
        res = (post_img2(file) for file in paths[begin: end + 1])
        for x in grequests.map(res):
            if x.status_code == 200:
                count += 1
                print(x.json())
            print("success: {}".format(count))


run2()