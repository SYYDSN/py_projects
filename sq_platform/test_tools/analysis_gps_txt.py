#  -*- coding: utf-8 -*-
import os
import datetime


"""分析gps文本"""


def get_txt_paths(dir_path: str = "txt") -> list:
    """
    取出txt目录下所有gps文件的路径
    :param dir_path: 相对路径
    :return:
    """
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), dir_path)
    names = os.listdir(dir_path)
    paths = [os.path.join(dir_path, name) for name in names if name.endswith(".txt") and name.lower().find("gps") != -1]
    paths = [path for path in paths if os.path.isfile(path)]
    return paths


def get_gps(file_path: str) -> list:
    """
    读txt文件,获取gps记录
    :param file_path: gps txt文件绝对路径
    :return:
    """
    f = open(file_path, mode="r", encoding="utf-8")
    res = list()
    for i, line in enumerate(f):
        temp = eval(line)[0]
        t_str = temp['ts']
        if t_str.startswith("1970"):
            print("错误的gps记录位于文件 {} 第{}行".format(file_path, i + 1))
        temp['time'] = datetime.datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
        res.append(temp)
    f.close()
    return res


def read_txt(path_list: list) -> list:
    """
    批量读取txt文件获取gps记录
    :param path_list: gps txt文件绝对路径 的数组
    :return:
    """
    res = list()
    for path in path_list:
        res += get_gps(path)
    res.sort(key=lambda obj: obj['time'], reverse=True)
    return res


if __name__ == "__main__":
    ps = get_txt_paths()
    r = read_txt(ps)
    print("{}至{}间共计上传{}条记录,其中3条无效".format(r[-4]['time'], r[0]['time'], len(r)))
    for i in r:
        print(i['ts'])