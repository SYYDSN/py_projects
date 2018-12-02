#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module



"""金10数据的持久化部分"""


class JinTen(orm_module.BaseDoc):
    """
    金10 数据,包含日历和新闻数据
    """