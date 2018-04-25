# -*- coding:utf-8 -*-
import os
import sys
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if project_dir not in sys.path:
    sys.path.append(project_dir)
import mongo_db
from api.data.item_module import *
import matplotlib.patches as mpatches
from amap_module import position_distance
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdate


matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设定全局字体，前提是安装了微软雅黑字体


"""gps和各种传感器信息的计算函数"""


def draw_ploy_line(data_x: list, data_y: list, x_name: str = "", y_name: str = "", title: str = "") -> None:
    """
    根据数组绘制一个曲线
    :param data_x: x轴数据
    :param data_y: y轴数据
    :param x_name: x轴名字
    :param y_name: y轴名字
    :param title: 标题
    :return:
    """
    red_patch = mpatches.Patch(color='red', label='The red data', lw=0)  # 一个图示
    plt.legend(handles=[red_patch])
    plot = plt.plot(data_x, data_y, 'c')  # x轴数据，y轴数据，颜色
    plt.grid(True)  # 显示网格
    plt.xlabel(x_name)  # 设置x轴标签
    plt.ylabel(y_name)  # 设置y轴标签
    plt.title(title)  # 设置title
    plt.show()


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


def find_gps(user_id: (str, ObjectId), date_str: str) -> list:
    """
    查询某用户某天全部的gps数据
    :param user_id:   用户id ObjectId类型
    :param date_str: 2017-1-1 格式的字符串
    :return:   gps的字典的list
    """
    user_id = mongo_db.get_obj_id(user_id)
    dbref = mongo_db.DBRef(collection="user_info", id=user_id, database="platform_db")
    filter_dict = {
        "user_id": dbref,
        "time": {
            "$gte": mongo_db.get_datetime_from_str("{} 0:0:0.000".format(date_str)),
            "$lte": mongo_db.get_datetime_from_str("{} 23:59:59.999".format(date_str))
        }
    }
    sort_dict = {"time": 1}
    projection = ['loc', "time", "speed"]
    res = GPS.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, projection=projection, to_dict=True)
    return res


def draw_speed_contrast(u_id, date_str, title: str = None) -> None:
    """绘制gps传感器的speed数据和计算出来的speed数据的差别"""
    data = find_gps(u_id, date_str)
    if len(data) == 0:
        ms = "用户: {} , {} 没有数据".format(u_id, date_str)
        print(ms)
    else:
        x, y, z = [], [], []
        prev = None
        for item in data:
            cur_t = item['time']
            x.append(cur_t)
            y.append(item['speed'])
            temp = dict()
            temp['loc'] = item['loc']['coordinates']
            temp['time'] = cur_t
            if prev is None:
                v = 0
            else:
                mileage = position_distance(pos_01=item['loc']['coordinates'], pos_02=prev['loc'])
                seconds = (cur_t - prev['time']).total_seconds()
                if seconds == 0:
                    continue
                else:
                    v = (mileage / seconds) * 60 * 60
            temp['speed'] = v
            prev = temp
            if v > 100:
                print("high speed: user_id={}, time={}, speed={}".format(user_id, cur_t, v))
            z.append(v)

        a_data = {
            "title": date_str if title is None else title,
            "data": [
                {
                    "label": "传感器记录",
                    "lw": 0,
                    "data_x": x,
                    "data_y": y
                },
                {
                    "label": "计算的结果",
                    "lw": 0,
                    "data_x": x,
                    "data_y": z
                }
            ]
        }
        draw_multiple_ploy_line(a_data)


if __name__ == "__main__":
    """绘制gps传感器的speed数据和计算出来的speed数据的差别"""
    user_ids = [
        "59cda57bad01be0912b352da",
        "59cda964ad01be237680e29d",
        "59cda886ad01be237680e28e"
    ]
    a_dict = dict(zip(user_ids, ("刘成刚", "栾新军", "薛飞")))
    a_dict = dict(zip(user_ids, ("栾新军")))
    for user_id in user_ids:
        if str(user_id) == "59cda886ad01be237680e28e":
            now = mongo_db.get_datetime_from_str("2017-10-18")
            for i in range(10):
                delta = datetime.timedelta(days=i + 1)
                d = (now - delta).strftime("%F")
                draw_speed_contrast(user_id, d, "{} on {}".format(a_dict[user_id], d))


