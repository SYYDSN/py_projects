# -*- coding: utf-8 -*-
import math
import random

n = 10
C = 10
s = [4, 2, 7, 3, 5, 4, 2, 3, 6, 2]


def test():
    """贪心算法"""
    k = 0
    """初始化一个全为0的长度为n的数组.用来可能需要用到集装箱序列"""
    b = [0 for i in range(n)]
    for i in range(n):
        """
        变量mi用于内层循环比较每个集装箱装完货物后的剩余空间
        min是关键字,用mi替代 
        """
        mi = C
        m = k + 1  # 当前用到了第几个集装箱?
        """循环已用的(包含当前的)集装箱序列,k+1是当所有已用的箱子都放不下时.新开一个箱子"""
        for j in range(k + 1):
            temp = C - b[j] - s[i]  # 当前集装箱装入货物后剩下的容量
            if 0 <= temp < mi:
                """
                如果当前集装箱的剩余空间装的下货物:
                temp > 0 就是集装箱的剩余空间足够.
                由于mi的初始值是最大10,所以只要装的下货物的集装箱.装完后的剩余空间
                每次和mi比较,比mi小的话就给mi赋值.否则就忽略.这样就保证了
                0 <= temp < mi 条件满足的,总是已知mi最小(且为正数)的情况.
                就是最小的(最佳匹配)
                temp < mi 每次赋值其实就是在比较哪个集装箱是装完货物后最小的
                """
                mi = temp
                m = j
            else:
                """
                这里是装不下货物的temp<0和装完后剩余空间不是最小的tem>mi情况.
                注意: 这个mi是上一次内循环被赋值的,如果j=0,那么这个mi就是在
                外层循环中被初始化的
                """
                pass
        b[m] = b[m] + s[i]
        k = k if k > (m + 1) else (m + 1)
    return k


def merge(arr, p, q, r):
    """规并排序"""
    left, right = [], []
    n1 = q - p + 1
    i = 0
    n2 = r - q
    for i in range(n1):
        left.append(arr[p + i])
    left.append(65535)
    for i in range(n2):
        right.append(arr[q + i + 1])
    right.append(65535)
    i = 0
    j = 0
    for k in range(p, r + 1):
        if left[i] > right[j]:
            arr[k] = right[j]
            j += 1
        else:
            arr[k] = left[i]
            i += 1


def merge_sort(arr, begin: int = None, end: int = None):
    """
    归并排序
    :param arr:
    :param begin:
    :param end:
    :return:
    """
    begin = 0 if begin is None else begin
    end = len(arr) if end is None else end
    if begin < end:
        mid = int((begin + end) / 2)
        merge_sort(arr, begin, mid)
        merge_sort(arr, mid + 1, end)
        merge(arr, begin, mid, end)


if __name__ == "__main__":
    """归并排序"""
    l = [random.randint(1, 20) for i in range(10)]
    merge_sort(l)
    pass
