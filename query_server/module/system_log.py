#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
from pymongo import WriteConcern
import datetime
from hashlib import md5


ObjectId = orm_module.ObjectId


"""系统日志模块"""


class JavascriptLog(orm_module.BaseFile):
    """
    执行js脚本出错的日志
    """
    _table_name = "javascript_log"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['args'] = str
    type_dict['url'] = str
    type_dict['error'] = str
    type_dict['error_time'] = datetime.datetime
