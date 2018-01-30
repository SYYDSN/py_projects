# -*-coding:utf8-*-
import requests
import hashlib
import os

author = "8af044f186374563b30dfd5f3da2b5e3"
headers = {
    "author": author,  # token
    "debug": "1"  # 是否是测试
}
batch_info = {"file4.zip": "ccccc", "file5.zip": "dddddd", "file6.zip": "eeeeeee"}
batch_info = {"picc22332343434.zip": "06a9d348616dd320b9de9a55703dba6c"}


url1 = "http://192.168.116.15:8000/message/upload_success"
url2 = "http://113.108.9.33:8000/message/upload_success"
url3 = "http://113.108.9.33:8100/message/upload_success"
url4 = "http://127.0.0.1:8000/message/upload_success"


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


def get_data():
    dir = os.path.join(os.path.split(__file__)[0], "batch_zip")
    file_list = os.listdir(dir)
    result = dict()
    for file_name in file_list:
        file_path = os.path.join(dir, file_name)
        md5 = get_md5(file_path)
        result[file_name] = md5
    return result


r = requests.post(url=url2, data=get_data(), headers=headers)
if r.status_code == 200:
    print(r.json())