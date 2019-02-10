#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from orm_unit.orm_module import *

"""全局日志模块"""


class GlobalJournal(BaseDoc):
    """
    基础日志表.
    目前所有日志都记录在一个表中.
    将来日志会按照类型记录.
    """
    _table_name = "global_journal"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['ip'] = str
    type_dict['user_agent'] = str
    type_dict['authorization'] = str
    type_dict['user_id'] = int
    type_dict['host'] = str
    type_dict['path'] = str
    type_dict['method'] = str
    type_dict['web_framework'] = str
    type_dict['get_args'] = dict
    type_dict['post_args'] = dict
    type_dict['json_args'] = dict
    type_dict['response'] = dict
    type_dict['exception'] = str
    type_dict['enter_time'] = datetime.datetime
    type_dict['exit_time'] = datetime.datetime

    @classmethod
    def test(cls):
        return "ok"

    @classmethod
    def before_request(cls, **kwargs) -> ObjectId:
        kwargs['enter_time'] = datetime.datetime.now()
        obj_id = cls.insert_one(doc=kwargs, write_concern=get_write_concern())
        return obj_id


if __name__ == "__main__":
    pass
