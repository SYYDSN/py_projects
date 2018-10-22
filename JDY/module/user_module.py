#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import datetime


ObjectId = mongo_db.ObjectId



"""用户模块"""


class LoginLog(mongo_db.BaseDoc):
    """
    登录日志
    """
    _table_name = "login_log"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['phone'] = str
    type_dict['password'] = str
    type_dict['success'] = bool
    type_dict['ip'] = str
    type_dict['agent'] = str  # 浏览器信息
    type_dict['time'] = datetime.datetime

    @classmethod
    def log(cls, info: dict):
        """
        记录后台登录的事件
        :param info:
        :return:
        """
        a_args = dict()
        a_args['_id'] = ObjectId()
        a_args['phone'] = info.get("phone", "")
        a_args['password'] = info.get("password", "")
        a_args['success'] = info.get("success", False)
        a_args['ip'] = info.get("ip", "")
        a_args['agent'] = info.get("agent", "")
        a_args['time'] = info.get("time", datetime.datetime.now())
        cls.insert_one(**a_args)


class User(mongo_db.BaseDoc):
    """用户"""
    _table_name = "user_info"
    type_dict = dict()  # 属性字典
    type_dict['_id'] = mongo_db.ObjectId  # id,唯一
    type_dict['real_name'] = str  # 真实姓名
    type_dict['phone'] = str  # 手机号码　登录用
    type_dict['status'] = int  # 0 不能登录,1 可以登录
    type_dict['password'] = str  # 登录密码

    @classmethod
    def login(cls, phone: str, password: str) -> dict:
        """
        用户登录
        {"phone": "18640375070", "password": "Kaiyang@9856"} 废止 2018-9-19
        新的用户账户和密码   platform_root/Sh@xundie-0919
        :param phone: 手机号
        :param password: 密码
        :return:
        """
        mes = {"message": "success"}
        filter_dict = {"phone": phone, "password": password, "status": 1}
        res = cls.find_one_plus(filter_dict=filter_dict, instance=False)
        if res is None:
            mes['message'] = "用户名或密码错误"
        else:
            mes['data'] = res
        return mes


if __name__ == "__main__":
    args = {"phone": "15026826913", "password": "a21f914b336c14f503998d658c6d7c5d"}
    u = User(**args)
    u.save_plus()