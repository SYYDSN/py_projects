#  -*- coding: utf-8 -*-
import os
import sys
__project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if __project_dir not in sys.path:
    sys.path.append(__project_dir)
import mongo_db
from log_module import get_logger


"""跟数据库有关的操作"""


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
logger = get_logger()


