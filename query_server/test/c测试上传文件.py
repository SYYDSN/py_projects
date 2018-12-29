# -*- coding: utf-8 -*-
import os
import sys
__root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __root_path not in sys.path:
    sys.path.append(__root_path)
import requests


"""各种客户端的测试程序"""


def upload_task_sync():
    """上传任务同步文件"""
    with open("task2_g.zip", mode='rb') as file:
        files = {"file": file}
        r = requests.post("http://127.0.0.1:7012/upload", files=files)
        print(r.json())


if __name__ == "__main__":
    upload_task_sync()
    pass