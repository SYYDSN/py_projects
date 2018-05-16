# -*- coding: utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.split(os.path.split(sys.path[0])[0])[0]
if project_dir not in sys.path:
    sys.path.append(project_dir)
from mongo_db import cache
import hashlib
import shutil
from log_module import get_logger


"""app模块"""


logger = get_logger()


the_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
client_dir = os.path.join(the_path, "static")
if not os.path.exists(client_dir):
    os.makedirs(client_dir)


def check_file(sub_dir_name="apk")->dict:
    """
    检查子目录的安装包，挑选最新的一个。
    :param sub_dir_name: 即是子目录名也是文件后缀名
    :return: dict
    """
    dir_path = os.path.join(client_dir, sub_dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    name_list = os.listdir(dir_path)
    if len(name_list) == 0:
        return None
    else:
        a_list = [{"name": name, "version": name.split("_")[1][1:].split(".")} for name in name_list if name.lower().endswith(".apk") and name.lower().find("_") != -1]
        a_list.sort(key=lambda obj: (int(obj['version'][0]), int(obj['version'][1]), int(obj['version'][2])), reverse=True)
        temp = a_list[0]
        file_name = temp['name']
        version = ".".join(temp['version'])
        full_path_raw = os.path.join(client_dir, sub_dir_name, file_name)
        full_path_dir = os.path.join(client_dir, sub_dir_name, "downloads")
        if not os.path.exists(full_path_dir):
            os.makedirs(full_path_dir)
        full_path_new = os.path.join(full_path_dir, "safego.apk")
        if os.path.exists(full_path_new):
            md5_01 = hashlib.md5(open(full_path_raw, "rb").read()).hexdigest()
            md5_02 = hashlib.md5(open(full_path_new, "rb").read()).hexdigest()
            if md5_01 == md5_02:
                pass
            else:
                shutil.copy(full_path_raw, full_path_new)
        else:
            shutil.copy(full_path_raw, full_path_new)
        return {"version": version, "url": "static/{}/{}/{}".format(sub_dir_name, "downloads", "safego.apk")}


def check_version(os_type="android"):
    """检查apk版本
    os_type  移动端操作系统
    return   字典
    """
    sub_dir_name = "apk"
    if os_type.lower() == "android":
        pass
    else:
        try:
            ms = "check_version func Error,os_type={}".format(os_type)
            raise ValueError(ms)
        except ValueError as e:
            print(e)
            logger.exception("Error:e={}".format(e))
    key = "{}_check_version".format(sub_dir_name)
    result = cache.get(key)
    if result is None:
        result = check_file(sub_dir_name)
        cache.set(key, result, timeout=60)
    return result


if __name__ == "__main__":
    print(check_version())