#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import requests


"""测试南京OA"""


def view_user(*args, **kwargs):
    """
    查看用户
    :param args:
    :param kwargs:
    :return:
    """
    url = "http://47.100.23.19:8089/oa/users/user"
    r = None
    try:
        r = requests.get(url, params=kwargs)
        print(r.json())
    except Exception as e:
        print(e)
    finally:
        if r is None:
            pass
        else:
            status = r.status_code
            if status == 200:
                print(r.json())
            else:
                print("response code is {}".format(status))


def add_user(*args, **kwargs):
    """
    查看用户
    :param args:
    :param kwargs:
    :return:
    """
    url = "http://47.100.23.19:8089/oa/users/adduser"
    r = None
    kw = {
        "userName": "张三",
        "loginName": "zhangsan",
        "pwd": "123456",
        "dpId": 2
    }
    try:
        r = requests.get(url, params=kw)
        print(r.json())
    except Exception as e:
        print(e)
    finally:
        if r is None:
            pass
        else:
            status = r.status_code
            if status == 200:
                print(r.json())
            else:
                print("response code is {}".format(status))


def add_goods(*args, **kwargs):
    """
    查看用户
    :param args:
    :param kwargs:
    :return:
    """
    url = "http://47.100.23.19:8089/oa/administrative/goods/add/addGoods"
    r = None
    kw = {
        "name": "u盘",
        "goodstypeId": 1,
        "description": "测试物品",
        "number": 12
    }
    try:
        r = requests.post(url, json=kw)
        print(r.json())
    except Exception as e:
        print(e)
    finally:
        if r is None:
            pass
        else:
            status = r.status_code
            if status == 200:
                print(r.json())
            else:
                print("response code is {}".format(status))


if __name__ == "__main__":
    add_goods()
    pass
