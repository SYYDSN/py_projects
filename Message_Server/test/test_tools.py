# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import requests
import json



"""测试工具"""


def send_signal():
    """发送一个喊单信号"""
    url = "http://127.0.0.1:8000/listen_signal_test"
    s = {
        "data": {
            "_widget_1520843228626": 10,
            "_id": "5b4d5e9a68304f247f641714",
            "appId": "5a45b8436203d26b528c7881",
            "_widget_1514518782514": "恒指",
            "updater": {
                "_id": "5a1e680642f8c1bffc5dbd6f",
                "name": "测试"
            },
            "_widget_1514518782592": 28220,
            "_widget_1522117404041": -282300,
            "_widget_1514887799261": "",
            "updateTime": "2019-08-17T03:12:26.046Z",
            "_widget_1520843763126": -282200,
            "_widget_1516245169208": "普通",
            "_widget_1522134222811": 100,
            "deleteTime": None,
            "formName": "分析师交易记录",
            "deleter": None,
            "createTime": "2019-08-17T03:12:26.046Z",
            "entryId": "5a45b90254ca00466b3c0cd1",
            "_widget_1514887799459": 1,
            "_widget_1514518782842": -282200,
            "_widget_1514518782504": "2019-08-17T03:12:06.000Z",
            "_widget_1514518782557": "买入",
            "creator": {
                "_id": "5a1e680642f8c1bffc5dbd6f",
                "name": "测试"
            },
            "_widget_1514887799231": None,
            "_widget_1514518782603": [
                {
                    "_widget_1514518782632": 28020,
                    "_widget_1514518782614": 28620
                }
            ]
        },
        "op": "data_create"
    }
    r = requests.post(url=url, json=json.dumps(s))
    print(r.json())


if __name__ == "__main__":
    """测试发送喊单信号"""
    send_signal()
    pass
