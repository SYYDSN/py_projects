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
    def import_images(cls, image_dir: str = None) -> int:
        """
        批量导入文件
        :param image_dir: 路径，相对于项目根目录的路径
        :return:
        """
        if image_dir is None:
            image_dir = os.path.join("static", "image", "animal")
            names = os.path.dirname(image_dir)
            for name in names:
                the_name = name.split(".")[0]
                file_path = os.path.join(image_dir, name)
                with open(file_path, "rb") as f:
                    cls.save_cls(f)
