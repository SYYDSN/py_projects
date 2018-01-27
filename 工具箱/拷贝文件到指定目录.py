# -*- coding: utf-8 -*-
import shutil
import os
import re


"""拷贝文件到指定的目录.原计划是ｇｉｔ用的。"""


"""默认的文件后缀名过滤器"""
default_filter_suffix = ['pyc', 'log', 'bson', 'zip', 'apk', 'txt', 'pkl']
"""可以忽略的目录名称，不是绝对路径"""
default_ignore_dir_name = ['__pycache__', 'data_dump', '.idea', 'logs', 'static/thumb/track', 'static/data_file',
                           "static/apk"]
"""默认源目录"""
default_source_path = "/home/walle/work/projects/sq_platform"
# default_source_path = "/home/walle/work/test/sq_platform"
"""默认的目的目录，这是carx的ｇｉｔ默认目录"""
default_destination_path = "/home/walle/tmp/pltf2/pltf2/sq_platform"
# default_destination_path = "/media/walle/disk/my_files/sq_platform_2017_09_27_bak"
# default_destination_path = "/media/walle/disk/my_files/sq_platform"
# default_destination_path = "/home/walle/work/test/sq_platform2"


def get_file_path(dir_path: str)->list:
    """
    获取获取一个目录下，所有文件的绝对路径
    :param dir_path: 文件夹绝对路径
    :return: 应该被拷贝的文件的绝对路径组成的数组。
    """
    # filter_suffix, ignore_dir = list(), list()
    result = list()
    for name in os.listdir(dir_path):
        the_path = os.path.join(dir_path, name)
        if os.path.isdir(the_path):
            paths = get_file_path(the_path)
            result.extend(paths)
        else:
            result.append(the_path)
    return result


def _startswith_list(a_str: str, a_list) -> bool:
    """
    检查key_word是以数组中单词开头
    :param a_str:
    :param a_list:
    :return:
    """
    flag = False
    for x in a_list:
        if x.startswith(a_str):
            flag = True
            break
    return flag


def get_suffix_name(file_name, lower: bool = True) -> str:
    """
    获取一个文件的后缀名,小写
    :param file_name:
    :param lower: 是否返回的是小写后缀名?
    :return:
    """
    l = file_name.split(".")[-1]
    return l.lower()


def copy_dir(source: str = None, destination: str = None, filter_suffix: list = None, ignore_dir: list = None)->None:
    """
    把一个目录拷贝到制定的位置
    :param source:  源目录
    :param destination: 目标目录
    :param filter_suffix: 无需拷贝的文件的后缀名组成的数组。
    :param ignore_dir: 无需拷贝的文件的后缀名组成的数组。
    :return: None
    """
    source = default_source_path if source is None else source
    destination = default_destination_path if destination is None else destination
    filter_suffix = default_filter_suffix if filter_suffix is None else filter_suffix
    ignore_dir = default_ignore_dir_name if ignore_dir is None else ignore_dir
    if not os.path.exists(destination):
        os.makedirs(destination)
    paths = get_file_path(source)
    paths = [path for path in paths if (
        get_suffix_name(path) not in filter_suffix and not _startswith_list(path, ignore_dir))]
    print(len(paths))
    for path in paths:
        print(path)
        dec = os.path.join(destination, path.split("{}/".format(source))[-1])
        try:
            dir_path = os.path.dirname(dec)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            shutil.copy2(path, dec)
        except FileNotFoundError as e:
            print(path)
            raise e


if __name__ == "__main__":
    copy_dir()

