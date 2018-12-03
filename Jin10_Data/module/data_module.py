#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module


ObjectId = orm_module.ObjectId


"""金10数据的持久化部分"""


class JinTen(orm_module.BaseDoc):
    """
    金10 数据,包含日历和新闻数据
    """
    _table_name = "jin10_data"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['type'] = str   # 消息类型,2种, 新闻和日历 news/calendar



if __name__ == "__main__":
    j = JinTen(type="news")
    j.save()
    pass