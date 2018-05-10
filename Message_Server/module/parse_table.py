# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import pyquery
import datetime
from log_module import get_logger


"""解析每月的老师真实喊单报表"""


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
cache = mongo_db.RedisCache()
logger = get_logger()


def read_table(file_path: str = None) -> list:
    """
    读取老师真实邯郸数据
    :param file_path:
    :return:
    """
    if file_path is None:
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "2018-4")