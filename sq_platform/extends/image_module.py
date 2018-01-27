# -*- coding: utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.split(sys.path[0])[0]
if project_dir not in sys.path:
    sys.path.append(project_dir)
from matplotlib import pyplot as plt
from io import BytesIO
import cv2
from mongo_db import reduce_list
import numpy as np
from log_module import get_logger


"""图像处理相关的工具"""


logger = get_logger()


def create_track_thumb_and_show(track_list: list) -> bytes:
    """
    生成一个缩略图,并显示,此函数仅仅为了演示.这个函数是基于matplotlib的
    :param track_list: 生成图片的数据
    :return: bytes  生成的文件的二进制内容
    """
    track_list = [sorted(x['loc']) for x in track_list]
    lng_list, lat_list = [], []  # 经度和纬度
    for x in track_list:
        lng_list.append(x[0])
        lat_list.append(x[1])
    # img = plt.imread("2017-11-08 13-49-52屏幕截图.png")
    # plt.imshow(img, alpha=0.5)
    plt.plot(lng_list, lat_list, linewidth=4)
    ax = plt.gca()
    ax.spines['top'].set_visible(False)  # 去掉上边框
    ax.spines['bottom'].set_visible(False)  # 去掉上边框
    ax.spines['left'].set_visible(False)  # 去掉上边框
    ax.spines['right'].set_visible(False)  # 去掉上边框
    # plt.grid(True)  # 显示网格
    # plt.xlabel("x label")  # 设置x轴标签
    # plt.ylabel("y label")  # 设置y轴标签
    # plt.title("i am title")  # 设置title
    plt.xticks([])  # 去x轴刻度
    plt.yticks([])  # 去y轴刻度
    # plt.show()
    fig = plt.gcf()
    fig.set_size_inches(2, 1.5)
    # fig.savefig('test2png.png', dpi=100)
    canvas = fig.canvas
    buffer = BytesIO()
    canvas.print_png(buffer)
    image_data = buffer.getvalue()
    buffer.close()
    return image_data


def create_track_thumb_and_save_by_matplotlib(track_list: list, save_path: str) -> None:
    """
    生成一个缩略图,并保存.这个函数是基于matplotlib的,此方法必须要有一个gui界面才能运行.
    :param track_list: 生成图片的数据 GPS/Track类的实例的数组
    :param save_path: 图片的保存路径
    :return:
    """
    track_list = [x.get_attr("loc")['coordinates'] for x in track_list]
    lng_list, lat_list = [], []  # 经度和纬度
    for x in track_list:
        lng_list.append(x[0])
        lat_list.append(x[1])
    plt.plot(lng_list, lat_list, linewidth=4)
    ax = plt.gca()
    ax.spines['top'].set_visible(False)  # 去掉上边框
    ax.spines['bottom'].set_visible(False)  # 去掉上边框
    ax.spines['left'].set_visible(False)  # 去掉上边框
    ax.spines['right'].set_visible(False)  # 去掉上边框
    # plt.grid(True)  # 显示网格
    # plt.xlabel("x label")  # 设置x轴标签
    # plt.ylabel("y label")  # 设置y轴标签
    # plt.title("i am title")  # 设置title
    plt.xticks([])  # 去x轴刻度
    plt.yticks([])  # 去y轴刻度
    # plt.show()
    fig = plt.gcf()
    fig.set_size_inches(2, 1.5)
    fig.savefig(save_path, dpi=100)
    print("图片保存位置：{}".format(save_path))
    plt.close()


def return_result(current, max_value, step, bottom) -> int:
    """
    opencv转换坐标空间的函数
    :param current:
    :param max_value:
    :param step:
    :param bottom:
    :return:
    """
    res = 0 if step == 0 else int(abs((max_value - current)) / step) + bottom
    return res


def create_track_thumb_and_save_by_opencv(track_list: list, save_path: str) -> None:
    """
        生成一个缩略图,并保存.这个函数是基于opencv的,
        :param track_list: 生成图片的数据 GPS/Track类的实例的数组
        :param save_path: 图片的保存路径
        :return:
        """
    track_list = reduce_list(track_list, 500)
    track_list = [x.get_attr("loc")['coordinates'] for x in track_list]
    img = np.empty((600, 800, 3), np.float32)
    img[::] = 200  # 填充背景色
    track_list = np.array(track_list, dtype=np.float32)
    max_tuple = np.amax(track_list, axis=0)
    min_tuple = np.amin(track_list, axis=0)
    step_01 = (max_tuple[0] - min_tuple[0]) / 750
    step_02 = (max_tuple[1] - min_tuple[1]) / 550
    try:
        track_list = np.array([[return_result(x, min_tuple[0], step_01, 25), return_result(y, max_tuple[1], step_02, 25)]
                      for x, y in track_list])
        cv2.polylines(img, [track_list], False, (230, 100, 100), 6, cv2.LINE_AA)
    except ValueError as e:
        ms = "create_track_thumb_and_save_by_opencv Error! " \
             "track_list:{}   save_path:{} max_tuple:{} min_tuple:{}, step_01:{}, step_02:{}".\
            format(track_list, save_path, max_tuple, min_tuple, step_01, step_02)
        logger.exception(ms)
        raise e
    # cv2.imshow('image', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    cv2.imwrite(save_path, img)


if __name__ == "__main__":
    # p = 'D:/pycharm-workspace/sq_platform\\static\\thumb\\track\\59cda964ad01be237680e29d\\5a0f668c91576d1430b9107{}1.png'
    from api.data.item_module import GPS
    from mongo_db import get_datetime_from_str, DBRef, ObjectId
    begin_date = get_datetime_from_str('2017-11-15 00:00:00')
    end_date = get_datetime_from_str('2017-11-15 23:59:59')
    user_id = DBRef('user_info', ObjectId('59cda964ad01be237680e29d'), 'platform_db')
    filter_dict = {
        "user_id": user_id,
        "time": {"$gte": begin_date, "$lte": end_date}
    }
    sort_dict = {"time": 1}
    gps_list = GPS.find_plus(filter_dict=filter_dict, sort_dict=sort_dict)
    # for x in range(10):
    #     create_track_thumb_and_save(gps_list, p.format(x))
    ###################################################################################
    create_track_thumb_and_save_by_opencv(gps_list, "xx.png")
    pass