#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import requests
import datetime
import warnings
import re


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


"""公司相关的模型"""


class Company(mongo_db.BaseDoc):
    """公司用户"""
    _table_name = "company"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['full_name'] = str
    type_dict['sort_name'] = str
    type_dict['desc'] = str              # 公司简介
    type_dict['user_name'] = str         # 公司账户的登录名,全局唯一
    type_dict['user_password'] = str
    type_dict['create_date'] = datetime.datetime

    def __init__(self, **kwargs):
        from_create_func = kwargs.pop("from_create_func", False)
        if isinstance(from_create_func, bool) and from_create_func:
            pass
        else:
            ms = "你正在直接调用Company的初始化函数,请自行检查user_name属性的唯一性"
            warnings.warn(message=ms)
        if "full_name" not in kwargs:
            kwargs['full_name'] = ''
        if "sort_name" not in kwargs:
            kwargs['sort_name'] = ''
        if "desc" not in kwargs:
            kwargs['desc'] = ''
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        user_name = kwargs.pop("user_name", "")
        if isinstance(user_name, str) and len(user_name) > 1:
            kwargs['user_name'] = user_name
        else:
            ms = "用户名必须是一个有效的字符串,不能是 {}".format(user_name)
            raise ValueError(ms)
        user_password = kwargs.pop("user_password", "")
        if isinstance(user_password, str) and len(user_password) == 32:
            kwargs['user_password'] = user_password
        else:
            ms = "密码格式错误"
            raise ValueError(ms)
        super(Company, self).__init__(**kwargs)

    @classmethod
    def create(cls, save: bool = False, **kwargs) -> object:
        """
        推荐的创建实例的方法,会检查user_name参数是否唯一?
        :param save: 是否创建实例后立即保存?
        :param kwargs:
        :return: 实例对象
        """
        if "from_create_func" not in kwargs:
            kwargs['from_create_func'] = True   # 此参数告诉self.__init__函数,调用者是cls.create函数
        user_name = kwargs.pop("user_name", "")
        if isinstance(user_name, str) and len(user_name) > 1:
            kwargs['user_name'] = user_name
            """查询user_name是否唯一?"""
            f = {"user_name": user_name}
            r = cls.find_one_plus(filter_dict=f, instance=False, can_json=False)
            if r:
                ms = "用户名已存在"
                raise ValueError(ms)
            else:
                pass
        else:
            pass
        instance = cls(**kwargs)
        if save:
            r = instance.save_plus()
            if not isinstance(r, ObjectId):
                ms = "实例保存失败"
                raise ValueError(ms)
            else:
                pass
        return instance

    @classmethod
    def login(cls, user_name: str, user_password: str) -> dict:
        """
        公司用户的登录
        :param user_name:
        :param user_password:
        :return:
        """
        mes = {"message": "success"}
        f = {"user_name": user_name}
        projection = ['_id', 'user_name', 'user_password', 'full_name', 'short_name', 'desc']
        one = cls.find_one_plus(filter_dict=f, projection=projection, instance=False)
        if one:
            pw = one.get('user_password', "")
            if isinstance(user_password, str) and user_password.lower() == pw.lower():
                one.pop("user_password", "")
                mes['data'] = one
            else:
                mes['message'] = "密码错误"
        else:
            mes['message'] = "用户名不存在"
        return mes


if __name__ == "__main__":
    pass
