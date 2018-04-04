#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db


"""用户模块"""


class User(mongo_db.BaseDoc):
    """用户"""
    _table_name = "user_info"
    type_dict = dict()  # 属性字典
    type_dict['_id'] = mongo_db.ObjectId  # id,唯一
    type_dict['real_name'] = str  # 真实姓名
    type_dict['phone'] = str  # 手机号码　登录用
    type_dict['password'] = str  # 登录密码

    @classmethod
    def login(cls, phone: str, password: str) -> dict:
        """
        用户登录
        {"phone": "15026826913", "password": "xundie@789"}
        :param phone: 手机号
        :param password: 密码
        :return:
        """
        mes = {"message": "success"}
        filter_dict = {"phone": phone, "password": password}
        res = cls.find_one_plus(filter_dict=filter_dict, instance=False)
        if res is None:
            mes['message'] = "用户名或密码错误"
        else:
            mes['data'] = res
        return mes


if __name__ == "__main__":
    args = {"phone": "15026826913", "password": "a21f914b336c14f503998d658c6d7c5d"}
    u = User(**args)
    u.save()