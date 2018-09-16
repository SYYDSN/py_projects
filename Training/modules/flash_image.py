#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from mongo_db import *


"""闪卡训练使用的图片模块"""


class FlashImage(BaseFile):
    """
    闪卡图片
    """
    _table_name = "flash_image"

    @classmethod
    def import_images(cls, series: str) -> None:
        """
        批量导入文件
        当前已知系列
        1. 动物
        :param series: 系列名，必须
        :return:
        """
        image_dir = os.path.join(__project_dir__, "static", "image")
        names = os.listdir(image_dir)
        for name in names:
            the_name = name.split(".")[0]  # 动物的名称
            file_path = os.path.join(image_dir, name)
            with open(file_path, "rb") as f:
                cls.save_cls(f, name=the_name, file_name=name, series=series)


class FlashItem(BaseDoc):
    """一个闪动的操作元素"""
    _table_name = "flash_item"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['image_list'] = list


if __name__ == "__main__":
    """导入图片"""
    # FlashImage.import_images("动物")
    """分页查询某系列的图片"""
    r = FlashImage.query_by_page(filter_dict={"series": "动物"})
    print(r)
    pass
