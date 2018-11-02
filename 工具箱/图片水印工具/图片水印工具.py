# -*- coding: utf-8 -*-
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy as np


"""为图片附加水印的工具"""


def get_paths(dir_path: str, file_type: list = None) -> list:
    """
    获取指定路径目录下的指定类型文件.如果指定路径是就是指定的文件,则直接返回这个路径作为唯一元素的list
    :param dir_path: 目录/文件绝对路径
    :param file_type: 允许的文件类型
    :return:
    """
    res = list()
    if isinstance(file_type, list) and len(file_type) > 0:
        pass
    else:
        file_type = ['jpg', 'jpeg', 'png']
    if os.path.isdir(dir_path):
        """是个目录"""
        names = os.listdir(dir_path)
        for name in names:
            cur_suffix = name.split(".")[-1].lower()
            if cur_suffix in file_type:
                p = os.path.join(dir_path, name)
                res.append(p)
            else:
                pass
    else:
        suffix = dir_path.split(".")[-1].lower()
        if suffix in file_type:
            res.append(dir_path)
        else:
            pass
    return res


def add_text(image_path: str, content: str = None, font_size: int = 48, position: (list, tuple) = None, rotate: int = 0,
             new_name: str = None, new_path: str = None, color: str = None) -> str:
    """
    往图片上加文字水印
    :param image_path: 待加水印的图片的绝对路径
    :param content:  水印文本, 如果这里传入了一个图片的绝对路径话,就会把这个图片当作水印加上去
    :param font_size:  水印字号
    :param position:  水印左上角的坐标
    :param rotate:  水印的旋转角度
    :param new_name: 水印图片新的文件名
    :param new_path: 水印图片新的保存路径
    :param color: 水印的颜色
    :return: 加上水印的图片保存的绝对路径
    """
    pro_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if os.path.isfile(image_path):
        parent = Image.open(image_path)
        parent = parent.convert("RGBA")
        p_width, p_height = parent.size
        font_path = os.path.join(pro_dir, 'resource', 'fonts', 'YaHei.ttf')
        font = ImageFont.truetype(font_path, size=font_size)
        content = "必弘信息" if content is None else content
        color = "#42a4e8" if color is None else color
        last = None
        if os.path.isfile(content):
            """传入的是图片的绝对路径"""
        else:
            """传入的是文本"""
            count = len(content)
            child = Image.new(mode="RGBA", size=(p_width, p_height), color="white")  # 无背景填充
            draw_c = ImageDraw.Draw(im=child)
            top_x = (p_width / 2) - font_size * (len(content) / 2)  # 计算文本左上角的x坐标
            top_y = (p_height / 2) - font_size / 2  # 计算文本左上角的y坐标
            draw_c.text(xy=(top_x, top_y), text=content, font=font, fill=color)
            # child = child.rotate(angle=rotate)
            last = Image.blend(im1=parent, im2=child, alpha=0.3)
        last.show()
        old_path = os.path.dirname(image_path)
        file_name = os.path.basename(image_path)
        new_path = old_path if new_path is None or new_path == "" else old_path
        new_name = file_name if new_name is None or new_name == "" else new_name
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        else:
            pass
        last.save(fp=os.path.join(new_path, new_name))
    else:
        ms = "路径{}不是一个文件".format(image_path)
        raise FileNotFoundError(ms)


if __name__ == "__main__":
    paths = get_paths(dir_path="/home/walle/work/vs_code_projects/项目管理说明/image/重庆工地")
    # add_text(paths[-1])
    pass