# -*- coding:utf8 -*-
import os
import hashlib


def get_files(dir_path, file_type=['py','html','js','css']):
    """获取一个目录下所有文件的路径，dir_path是目录的名称，返回的是文件路径的数组"""
    prex_path = dir_path  # 获取目录
    raw_list = os.listdir(dir_path)
    file_list = []
    dir_list = []
    flag = True
    file_type = []  # 不过滤任何文件
    while flag:
        for x in raw_list:
            x = os.path.join(prex_path, x)
            if os.path.isdir(x):
                dir_list.append(x)
            else:
                if x.split(".")[-1] in file_type:
                    file_list.append(x)
        raw_list = []
        for y in dir_list:
            temp_dir = os.listdir(y)
            for m in temp_dir:
                m = os.path.join(y, m)
                if os.path.isdir(m):
                    raw_list.append(m)
                else:
                    if m.split(".")[-1] in file_type:
                        file_list.append(m)
        dir_list = []
        flag = True if len(raw_list) > 0 else False
    return file_list


def md5_dict(dir_list):
    """根据文件夹路径数组生成一个key为文件路径，md5为value的字典"""
    a_dict = dict()
    for x in get_files(dir_list):
        with open(x, mode="rb") as f:
            md5_str = hashlib.md5(f.read()).hexdigest()
            a_dict[x] = md5_str
    return a_dict


def compare_dir(dir1, dir2):
    """比较两个文件夹，返回不同的文件名的数组,文件目录参数最后不要带\\"""
    a_dict = md5_dict(dir1)
    b_dict = md5_dict(dir2)
    dir1 = dir1 + os.path.sep
    dir2 = dir2 + os.path.sep
    a_key = [x.replace(dir1, "") for x in a_dict]
    b_key = [x.replace(dir2, "") for x in b_dict]

    result1 = {x: "仅存在于 {} 目录！".format(dir1) for x in a_dict.keys() if x.replace(dir1, "") not in b_key}
    result2 = {x: "仅存在于 {} 目录！".format(dir2) for x in b_dict.keys() if x.replace(dir2, "") not in a_key}
    key_list = [x for x in a_key if x in b_key]
    # for x in key_list:
    #     print(os.path.join(dir1,x))
    result3 = {x: "文件有差别" for x in key_list if a_dict[os.path.join(dir1, x)] != b_dict[os.path.join(dir2, x)]}
    result1.update(result2)
    result1.update(result3)
    return result1

# print(compare_dir("/home/walle/work/projects/My_CRM", "/media/walle/disk/my_files/付老师/My_CRM"))
print(compare_dir("/home/walle/work/test/sq_platform", "/home/walle/work/test/sq_platform2"))