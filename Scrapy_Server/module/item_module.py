#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
from log_module import get_logger


"""定义数据模型的模块"""


logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef

