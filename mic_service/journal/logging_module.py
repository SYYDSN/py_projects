#  -*- coding: utf-8 -*-
import os
import sys

__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from nosql_module import *
from auth.auth_tools import *



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

    def test(self, num: int):
        return "ok {}".format(num)

    @classmethod
    def before_request(cls, doc: dict) -> dict:
        """记录操作的入日志"""
        authorization = doc.get("authorization", "")
        resp = check_token(authorization)
        e = doc.get("exception", "")
        e = "业务逻辑代码未正确相应" if e == "" else e
        doc['exception'] = e
        doc['enter_time'] = datetime.datetime.now()
        obj_id = cls.insert_one(doc=doc, write_concern=get_write_concern())
        resp['event_id'] = str(obj_id)
        return resp

    @classmethod
    def after_response(cls, doc: dict) -> None:
        """记录操作的出日志"""
        doc['exit_time'] = datetime.datetime.now()
        f = {"_id": ObjectId(doc.pop("_id"))}
        u = {"$set": doc}
        cls.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)


class ErrorLog(BaseDoc):
    """
    错误日志表.
    """
    _table_name = "error_log"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['error'] = str
    type_dict['file'] = str
    type_dict['func'] = str
    type_dict['time'] = datetime.datetime

    @classmethod
    def record(cls, doc: dict) -> str:
        doc['time'] = datetime.datetime.now()
        obj_id = cls.insert_one(doc=doc, write_concern=get_write_concern())
        return str(obj_id)


class Server1:
    """rpc服务类"""

    def record_error(self, doc: dict) -> None:
        """记录错误额日志"""
        ErrorLog.record(doc=doc)

    def before_request(self, doc: dict):
        """记录用户操作的入日志"""
        return GlobalJournal.before_request(doc)

    def after_response(self, doc: dict):
        """记录用户操作的出日志"""
        return GlobalJournal.after_response(doc)


if __name__ == "__main__":
    pass
