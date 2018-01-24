import datetime
import numpy as np
import sys

def count_time(func, args_dict: dict = None):
    """计算函数的运行时间"""
    b = datetime.datetime.now()
    if args_dict is not None:
        s = func(**args_dict)
    else:
        s = func()
    e = datetime.datetime.now()
    delta = (e - b).total_seconds()
    print("{} in {} seconds".format(s, delta))


a_list = np.arange(0, 100000, 0.01, np.float32)


def a1(arg):
    count = 0
    l = len(arg)
    res = []
    for x in arg:
        if count == 0 or count == (l - 1) or (count % 20) == 0:
            res.append(x)
        count += 1
    # res = []
    # for i, x in enumerate(arg):
    #     if i == 0 or i == (l - 1) or (i % 20) == 0:
    #         res.append(x)
    name = sys._getframe().f_code.co_name
    mes = "{} process {} time".format(name, len(res))
    return mes


def a2(arg):
    l= len(arg)
    # res = [x for i, x in enumerate(arg) if i == 0 or i == (l - 1) or (i % 20) == 0]
    res = []
    for i, x in enumerate(arg):
        if i == 0 or i == (l - 1) or (i % 20) == 0:
            res.append(x)
    name = sys._getframe().f_code.co_name
    mes = "{} process {} time".format(name, len(res))
    return mes

for i in range(10):
    print("#############################")
    count_time(a1, {"arg": a_list})
    count_time(a2, {"arg": a_list})