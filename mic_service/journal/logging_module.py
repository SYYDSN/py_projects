#  -*- coding: utf-8 -*-
import os
import sys

__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from nosql_module import *
from auth.auth_tools import *


"""全局日志模块"""


class AuthMapping:

        @classmethod
        def log_req(cls, used_auth: str, event_id: ObjectId) -> None:
            """
            把本次入请求使用的authorization和ObjectId的
            对应关系写入缓存, 方便请求返回时调用查找对应关系
            入请求和出请求最大间隔30分钟.超时视为操作失败.
            :param used_auth: 使用过的token
            :param event_id: 入事件的记录ObjectId
            :return:
            """
            key = "used_{}".format(used_auth)
            cache.set(key=key, value=event_id, timeout=1800)

        @classmethod
        def log_resp(cls, used_auth: str) -> ObjectId:
            """
            记录返回参数,跟据本次请求使用的authorization查找对应的日志
            的ObjectId,修改记录.
            行为:
             在缓存中查找authorization对应的ObjectId.
            :param used_auth:
            :return: objectId
            """
            key = "used_{}".format(used_auth)
            event_id = cache.get(key=key)
            if isinstance(event_id, ObjectId):
                """在缓存中找到"""
                cache.delete(key=key)
            else:
                pass
            return event_id


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
    type_dict['validate_result'] = str
    type_dict['new_authorization'] = str
    type_dict['user_id'] = int
    type_dict['hotel_id'] = int
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
        resp = check_token(authorization=authorization)
        validate_result = resp['message']
        e = "业务逻辑代码未正确相应"
        doc['exception'] = e
        doc['validate_result'] = validate_result
        doc['enter_time'] = datetime.datetime.now()
        new_authorization = resp.get("new_authorization")
        doc['new_authorization'] = new_authorization
        user_info = resp.get("user_info")
        if isinstance(user_info, dict):
            doc.update(user_info)
        obj_id = cls.insert_one(doc=doc, write_concern=get_write_concern())
        AuthMapping.log_req(used_auth=authorization, event_id=obj_id)
        return resp

    @classmethod
    def after_response(cls, doc: dict) -> dict:
        """记录操作的出日志,返回新的authorization"""
        used_auth = doc.get("authorization",  "")
        mes = {"message": "success"}
        if isinstance(used_auth, str) and len(used_auth) == 32:
            """正确的used_auth"""
            update = dict()
            event_id = AuthMapping.log_resp(used_auth=used_auth)
            if isinstance(event_id, ObjectId):
                f = {"_id": event_id}
            else:
                f = {"authorization": used_auth}
                update['exit_time'] = datetime.datetime.now()

            update['exception'] = "业务代码已执行完毕"
            update['response'] = doc
            u = {"$set": update}
            projection = ['_id', "authorization", "new_authorization"]
            result = cls.find_one_and_update(filter_dict=f, update_dict=u, projection=projection, upsert=True)
            mes['new_authorization'] = result['new_authorization']

        else:
            mes['message'] = "返回体中缺乏有效的authorization信息"
        return mes


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

    def before_request(self, doc: dict) -> dict:
        """记录用户操作的入日志"""
        return GlobalJournal.before_request(doc)

    def after_response(self, doc: dict) -> dict:
        """记录用户操作的出日志,返回new_authorization"""
        return GlobalJournal.after_response(doc)


if __name__ == "__main__":
    pass
