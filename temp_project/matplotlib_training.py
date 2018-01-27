# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt


"""matplotlib的绘图例子"""


def t_01():
    """最简单绘制一个曲线的方法"""
    x = np.arange(-np.pi, np.pi, 0.01)
    y = np.sin(x)
    plt.plot(x, y, 'c')  # x轴数据，y轴数据，颜色
    plt.plot(x * 2, y / 2, 'b')  # 第二个曲线
    plt.grid(True)  # 显示网格
    plt.xlabel("x label")  # 设置x轴标签
    plt.ylabel("y label")  # 设置y轴标签
    plt.title("i am title")  # 设置title
    plt.show()


def t_02():
    """绘制多个子图"""
    for index, color in enumerate("rgbyck"):
        plt.subplot(321 + index, facecolor=color)  # 3是行，2是列，1是第几个，比如326就是指3行2列的子图中的第六个子图（最后一个），
    plt.show()


def t_03():
    """在多个子图中绘制图标"""
    operational_symbol = [1, 2, 3, 1/3, 1/2, -1]
    for index, color in enumerate("rgbyck"):
        ax = plt.subplot(321 + index)
        v = np.random.randint(15, 25)
        x = np.arange(v - 2 * v, v, 0.01)
        y = x ** operational_symbol[index]
        ax.plot(x, y, color)
        ax.grid(True)
    plt.show()


def t_04():
    """绘制一个直方图"""
    data = np.array([np.random.random() for i in range(1000)])
    """
    histtype是指直方图的条的样式，有如下取值{'bar', 'barstacked', 'step',  'stepfilled'}，默认是bar
    """
    plt.hist(data, normed=1, facecolor='g', alpha=0.75, histtype='bar')
    plt.show()


if __name__ == "__main__":
    t_01()
