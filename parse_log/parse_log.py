#  -*- coding: utf-8 -*-
import os
import datetime


def get_files():
    dir = "logs"
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), dir)
    names = os.listdir(dir_path)
    names = [os.path.join(dir_path, x) for x in names if os.path.isfile(os.path.join(dir_path, x))]
    return names


def parse_page(file_path):
    f = open(file_path, mode="r", encoding="utf-8")
    res = list()
    for line in f:
        if "function=app_user_reg" in line:
            res.append(line)
    f.close()
    return res


if __name__ == "__main__":
    paths = get_files()
    res = list()
    for x in paths:
        res += parse_page(x)
    res.sort(key=lambda obj: datetime.datetime.strptime(obj.split(",")[0], "%Y-%m-%d %H:%M:%S"), reverse=True)
    l1 = list()
    l2 = list()
    l3 = list()
    for x in res:
        if x.startswith("2018-03-30"):
            l1.append(x)
    #     elif x.startswith("2018-03-28"):
    #         l2.append(x)
    #     elif x.startswith("2018-03-27"):
    #         l3.append(x)
    # l1.extend(l2)
    # l1.extend(l3)
    for x in l1:
        print(x)
    print(len(l1))