# -*- coding:utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.split(sys.path[0])[0]
if project_dir not in sys.path:
    sys.path.append(project_dir)
from mongo_db import ObjectId
import requests
import math
import grequests


user_id = ObjectId("59895177de713e304a67d30c")  # myself 用户id
auth_token = "626f8568f8ac44b7904a51bdfe3feaf4"  # myself app token
# auth_token = "2ac4101d2a8a40ee99a92ff671a203d0"  # app token
# auth_token = "c6cf8f56f1064349af4c90adb10901a2"  # 队长的app token
license_id = ObjectId("59ffb9b5e39a7b293e11d3c6")  # 行车证id
vio_query_generator_id = ObjectId("59ffb9b5e39a7b293e11d3ca")  # 查询器id


def query_vio_remote(token, query_id) -> dict:
    """
    根据app的token和查询器id查询违章记录.
    :param token:
    :param query_id:
    :return:
    """
    headers = {"auth_token": auth_token}
    url_remote = "http://safego.org:5000/api/query_violation"
    data = {"_id": vio_query_generator_id}
    r = requests.post(url_remote, data, headers=headers)
    print(r.status_code)
    print(r.json())


def query_vio_local(token: str = auth_token, query_id: ObjectId = ObjectId("598951e7de713e304a67d31f")) -> dict:
    """
    根据app的token和查询器id查询违章记录.
    :param token:
    :param query_id:
    {
    "_id" : ObjectId("59969543de713e39812b9711"),
    "vin_id" : "lsvnr49j492010012",
    "car_type" : "小车",
    "create_date" : ISODate("2017-08-18T15:20:35.713Z"),
    "plate_number" : "赣EG2681",
    "user_id" : ObjectId("598d6ac2de713e32dfc74796"),
    "engine_id" : "091697"
}
    :return:
    """
    headers = {"auth_token": auth_token}
    url_local = "http://127.0.0.1:5000/api/query_violation"
    data = {"_id": vio_query_generator_id}
    r = requests.post(url_local, data, headers=headers)
    print(r.status_code)
    print(r.json())


def test_security_report_detail():
    """测试安全报告明细"""
    headers = {"auth_token": auth_token}
    url = "http://127.0.0.1:5000/api/get_report_detail"
    # url = "http://safego.org:5000/api/get_report_detail"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(r.status_code)
    else:
        res = r.json()
        print(res)


def test_get_employee_list():
    """测后台获取用户下属列表"""
    headers = {"auth_token": auth_token}
    url = "http://127.0.0.1:5000/manage/get_employee_list"
    # url = "http://safego.org:5000/manage/get_employee_list"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(r.status_code)
    else:
        res = r.json()
        print(res)


def test_get_employee_archives():
    """测后台获取用户详细档案"""
    headers = {"auth_token": auth_token}
    url = "http://127.0.0.1:5000/manage/get_employee_archives"
    # url = "http://safego.org:5000/manage/get_employee_archives"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(r.status_code)
    else:
        res = r.json()
        print(res)


def test_get_ship_weather():
    """测app获取沿途天气"""
    headers = {"auth_token": auth_token}
    # url = "http://127.0.0.1:5000/api/get_ship_weather"
    url = "http://safego.org:5000/api/get_ship_weather"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(r.status_code)
    else:
        res = r.json()
        print(res)


def test_app_logout():
    """测app注销"""
    headers = {"auth_token": auth_token}
    url = "http://127.0.0.1:5000/api/logout"
    url = "http://safego.org:5000/api/logout"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(r.status_code)
    else:
        res = r.json()
        print(res)


def post_img():
    """post一个文件,模拟客户端上传数据"""
    remote = {"url": "http://safego.org:5000/api/add_driving_data",
             "headers": {"auth_token": "1cc55e2649f34e2382382d10a3ecb164"}}
    remote = {"url": "http://safego.org:5000/api/add_driving_data",
             "headers": {"auth_token": "13ea1238bfeb4d78965b7149aa4d733d"}}

    remote = {"url": "http://127.0.0.1:5000/api/add_driving_data",
              "headers": {"auth_token": auth_token}}

    # files = {"driving_data": open("/home/walle/work/temp/2017_11_22_15_42_43.zip", 'rb')}
    files = {"driving_data": open("/home/walle/work/temp/2017_11_23_05_01_34.zip", 'rb')}

    r = requests.post(remote['url'], headers=remote['headers'], files=files)
    return r


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
        res = (post_img(file) for file in paths[begin: end + 1])
        for x in grequests.map(res):
            if x.status_code == 200:
                count += 1
                print(x.json())
            print("success: {}".format(count))


def test_get_safety_report_history(auth: str = None):
    """测试get_safety_report_history函数"""
    auth = auth_token if auth is None else auth
    remote = {"url": "http://safego.org:5000/api/get_safety_report_history",
              "headers": {"auth_token": auth}}

    # remote = {"url": "http://127.0.0.1:5000/api/get_safety_report_history",
    #           "headers": {"auth_token": auth}}

    r = requests.post(remote['url'], headers=remote['headers'])
    return r


if __name__ == "__main__":
    test_get_safety_report_history("17dc8ab9c8b643cbb8ddbfb93f809af4")
    pass