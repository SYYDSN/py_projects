#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import datetime


"""图像类模块"""


ObjectId = mongo_db.ObjectId


class ImageFile(mongo_db.BaseFile):
    """
    图片存储类
    """
    _table_name = "image_file"
