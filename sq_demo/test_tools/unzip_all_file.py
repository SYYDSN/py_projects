# -*- coding: utf-8 -*-
import requests


"""解压缩远程服务器上所有的服务器上残留的zip文件"""


def unzip_all_remote(url: str = "http://safego.org:5000/api/unzip_all_file")->None:
    """
    解压缩远程服务器上残留的文件，一般用于服务器重启导致的某些文件被中断处理的情况。
    :param url:
    :return:
    """
    arg_dict = {"key": "dfdK@-03", "delay": False}
    # arg_dict = {"key": "dfdK@-03"}
    r = requests.post(url, data=arg_dict)
    if r is None:
        print(r)
    else:
        if r.status_code == 200:
            print(r.json())
        else:
            print(r.status_code)


if __name__ == "__main__":
    unzip_all_remote()
