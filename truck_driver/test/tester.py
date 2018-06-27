#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import requests
from model.identity_validate import GlobalSignature


"""所有的测试函数都建议在此实现"""


def test_get_signature() -> dict:
    """测试获取签名和算法"""
    sid = "18336048620"
    u = "http://127.0.0.1:7001/identity/get_signature"
    data = {"sid": sid}
    r = requests.post(url=u, data=data)
    s = r.status_code
    p = dict()
    if s != 200:
        print(s)
    else:
        p = r.json()
        print(p)
    return p


def test_company_login(sig: str, algo: str):
    """
    测试公司登录
    :return:
    """
    url = "http://127.0.0.1:7001/web/login_company"
    user_name = "jack"
    user_password = "b6c572fe59e80d9912ae510b13a6a6a7"
    payload = {
        "user_name": user_name,
        "user_password": user_password
    }
    data = {"payload": GlobalSignature.encode(payload=payload, secret=sig, algorithm=algo)}
    r = requests.post(url=url, data=data)
    s = r.status_code
    if s != 200:
        print(s)
    else:
        p = r.json()
        print(p)



if __name__ == "__main__":
    """获取签名和算法"""
    rs = test_get_signature()['data']
    algorithm = rs['algorithm']
    signature = rs['signature']
    """测试公司登录"""
    test_company_login(signature, algorithm)
    pass