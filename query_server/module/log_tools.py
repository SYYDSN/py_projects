# -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
import datetime


"""使用数据库的日志模块"""


ObjectId = orm_module.ObjectId


class SystemLog(orm_module.BaseDoc):
    """记录运行日志"""
    _table_name = "system_log"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['file'] = str  # py文件名
    type_dict['func'] = str  # 函数名
    type_dict['log_type'] = str  # 日志类型
    type_dict['content'] = str  # 日志内容
    type_dict['time'] = datetime.datetime

    @classmethod
    def log(cls, **kwargs):
        """
        记录日志
        :return:
        """
        kwargs['time'] = datetime.datetime.now()
        cls.insert_one(doc=kwargs)


if __name__ == "__main__":
    pass