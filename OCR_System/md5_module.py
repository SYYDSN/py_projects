# -*-coding:utf-8 -*-
import hashlib
import os

"""md5模块"""


def get_md5(f=None):
    """利用文件绝对路径来取md5"""
    if not f:
        raise ValueError("文件名不能为空")
    else:
        if not os.path.exists(f):
            raise ValueError("文件{}不存在".format(f))
        else:
            m = hashlib.md5()
            fd = open(f, "rb")
            while 1:
                x = fd.read(32000)
                if not x:
                    break
                m.update(x)
            fd.close()
            return m.hexdigest()
#
# import requests
#
# url = "http://113.108.9.33:8000/message/upload_success"
# headers = {"author": 1}
# md5 = get_md5("/home/walle/下载/redirect/项目需求/EAI票据识别系统/测试资料/case0001.zip")
# print(md5)
# data = {"case0001.zip": md5}
# res = requests.post(url, data=data, headers=headers)
# if res.status_code == 200:
#     print(res.json())
# else:
#     print(res.status_code)