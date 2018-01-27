#  -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math
import random
import sympy
import matplotlib


matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设定全局字体，前提是安装了微软雅黑字体


"""微积分的练习"""


def draw_multiple_ploy_line(data_dict) -> None:
    """
    绘制多个曲线.
    :param data_dict: 数据字典的数组,其中数据字典的组成如下:
    {
        "title": "我是总标题",
        "data":[
            {
                "label": "label_01",   # 曲线的标签,用做图示
                "lw": 0,               # 图示的位置 参考lw参数说明
                "color": 'c',          # 折线的颜色 参考颜色说明
                "linestyle": '-',      # 折线的样式 参考折线样式说明, 默认是 '-'
                "marker": '.',         # 端点的样式 参考端点样式说明, 默认是 None
                "data_x": x_list,      # x轴数据
                "data_y": y_list       # y轴数据
            },
            ...
        ]
    }
    lw参数说明(数字对应的位置):
                    ===============   =============
                    Location String   Location Code
                    ===============   =============
                    'best'            0
                    'upper right'     1
                    'upper left'      2
                    'lower left'      3
                    'lower right'     4
                    'right'           5
                    'center left'     6
                    'center right'    7
                    'lower center'    8
                    'upper center'    9
                    'center'          10
                    ===============   =============
    color 颜色说明:
        标记符    颜色
        r         红
        g         绿
        b         蓝
        c         蓝绿
        m         紫红
        y          黄
        k          黑
        w          白
    也可以用RGB来指定任意颜色[0.2,0.3,0.6]  注意和往常的0~255不同,这里的颜色是0~1的,同也可以用'#054E9F'这样的十六位表示的颜色.
    linestyle 线条样式说明:(第一列是参数)
    '-'       solid            line style
    '--'      dashed           line style
    '-.'      dash-dot         line style
    ':'       dotted           line style
    marker 端点样式说明:(第一列是参数)
    '.'       point marker
    ','       pixel marker
    'o'       circle marker
    'v'       triangle_down marker
    '^'       triangle_up marker
    '<'       triangle_left marker
    '>'       triangle_right marker
    '1'       tri_down marker
    '2'       tri_up marker
    '3'       tri_left marker
    '4'       tri_right marker
    's'       square marker
    'p'       pentagon marker
    '*'       star marker
    'h'       hexagon1 marker
    'H'       hexagon2 marker
    '+'       plus marker
    'x'       x marker
    'D'       diamond marker
    'd'       thin_diamond marker
    '|'       vline marker
    '_'       hline marker
    :return:
    """
    plt.title(data_dict.pop("title", ""))
    plt.grid(True)  # 显示网格
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
    handles = []
    for i, d in enumerate(data_dict['data']):
        color = colors[i % 7] if d.get("color") is None else d.get("color")
        label = "" if d.get("label") is None else d.get("label")
        lw = 0 if d.get("lw") is None else d.get("lw")
        linestyle = '-' if d.get("linestyle") is None else d.get("linestyle")
        marker = None if d.get("marker") is None else d.get("marker")
        data_x = d.get("data_x")
        data_y = d.get("data_y")
        patch = mpatches.Patch(color=color, label=label, lw=lw, linestyle=linestyle)  # 一个图示
        plot = plt.plot(data_x, data_y, color=color, linestyle=linestyle, marker=marker)  # 绘制
        handles.append(patch)
    plt.legend(handles=handles)
    plt.show()


if __name__ == "__main__":
    x_1 = [x for x in range(1, 51)]
    y_1 = [1 / i for i in x_1]
    y_2 = [1 / math.pow(i, 2) for i in x_1]
    x = sympy.symbols('x1')
    # 打印ｙ１函数的导数
    for i in x_1:
        print(sympy.limit((i + x), x, 0))
    print(sympy.limit(1 / x, x, 0))  # 第一个参数是函数,第二个参数是x变量,第三个参数表示x的逼近方向
    data = [
        {"data_x": x_1, "data_y": y_1, "label": "1/x"},
        {"data_x": x_1, "data_y": y_2, "label": "1/x^2"}
    ]
    datas ={"data": data}
    draw_multiple_ploy_line(datas)
