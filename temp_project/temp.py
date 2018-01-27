# -*- coding: utf-8 -*-
import math
import random


def variance(num_list) -> float:
    """
    计算一个数组的方差
    :param num_list: 数组
    :return: 方差值
    """
    s = sum(num_list)
    l = len(num_list)
    v = s / l  # 均值
    n = 0
    for i in num_list:
        n += math.pow((i - v), 2)
    return n / l


def standard_deviation(num_list) -> float:
    """计算标准差"""
    return math.sqrt(variance(num_list))


def variance2(num_list) -> float:
    """利用公式计算方差:
    数组中每个元素的平方的和除以数组的长度再减去均值的平方
    """
    s = 0
    n = 0
    l = 0
    for x in num_list:
        l += 1
        s += x
        n += math.pow(x, 2)
    return (n / l) - math.pow((s / l), 2)


if __name__ == "__main__":
    nums_01 = [7] + [9] * 2 + [10] * 4 + [11] * 2 + [13]
    nums_02 = [7] + [8] + [9] * 2 + [10] * 2 + [11] * 2 + [12] + [13]
    nums_03 = [3] * 2 + [6] + [7] * 2 + [10] * 3 + [11] + [13] + [30]
    print(standard_deviation(nums_01))
    print(standard_deviation(nums_02))
    print(standard_deviation(nums_03))