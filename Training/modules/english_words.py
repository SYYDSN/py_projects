#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module


ObjectId = orm_module.ObjectId


"""英文单词模块"""


class EnglishWord(orm_module.BaseDoc):
    """
    英文单词类
    """
    _table_name = "english_word"
    type_dict = dict()
    type_dict['_id'] = str  # 英文单词
    type_dict['chinese'] = str  # 中文解释

