#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import requests


"""所有的测试函数都建议在此实现"""


def test_company_login():
    """测试公司账户登录"""
    un = "jack"
    pw = "b6c572fe59e80d9912ae510b13a6a6a7"
    u = "http://127.0.0.1:7000/web/login_company"
    data = {"user_name": un, "user_password": pw}
    r = requests.post(url=u, data=data)
    s = r.status_code
    if s != 200:
        print(s)
    else:
        p = r.json()
        print(p)


if __name__ == "__main__":
    """测试公司账户登录"""
    # test_company_login()
    """"""
    import jwt
    secret = "abcd"
    encoded = jwt.encode(payload={"name": "jack", "password": "123456"}, key=secret)
    print(encoded)
    print(jwt.decode(jwt=encoded.decode(), key=secret))
    pass