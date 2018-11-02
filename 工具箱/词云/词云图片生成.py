# -*- coding: utf-8 -*-
import os
from scipy.misc import imread
from wordcloud import WordCloud
from wordcloud import ImageColorGenerator
from PIL import Image


pro_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # 项目目录路径
font_path = os.path.join(pro_dir, 'resource', 'fonts', 'YaHei.ttf')


def create_image(img_path: str, text: str) -> None:
    """
    生成词云图片
    :param img_path:  图片路径
    :param text: 词文本
    :return:
    """
    raw = Image.open(img_path)
    width, height = raw.size
    background = imread(img_path)
    """
    mask 是词云的图形.要求是白底.
    """
    wc = WordCloud(background_color="white", mask=imread(img_path),
                   width=width, height=height,
                   max_font_size=36,
                   font_path=font_path)
    res = list()
    with open(text, "r", encoding='utf-8') as f:
        lines = f.read().split("\n")
        words = [x for x in lines if x.strip() not in ['', '', '\n']]
        for x in words:
            t = x.split(" ")
            res.extend(t)
    text = " ".join(res)
    wc.generate(text)
    colors = ImageColorGenerator(background)
    wc = wc.recolor(color_func=colors)
    wc.to_file("11.png")  # 保存图片
    img = wc.to_image()  # 转换成PIL.Image对象
    img.show()         # 显示


if __name__ == "__main__":
    md_path = "/home/walle/文档/官网/site/index.html"
    create_image(img_path="2.png", text=md_path)
    pass