#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
from pymongo import WriteConcern
import random
import datetime


ObjectId = orm_module.ObjectId


"""
系统管理员
系统日志
"""


class Company(orm_module.BaseDoc):
    """
    公司信息
    """
    _table_name = "company"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['company_name'] = str
    type_dict['short_name'] = str
    type_dict['desc'] = str


class Dept(orm_module.BaseDoc):
    """部门信息"""
    _table_name = "dept"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['company_id'] = ObjectId
    type_dict['parent_id'] = ObjectId  # 上级部门id
    type_dict['dept_name'] = str


class Role(orm_module.BaseDoc):
    """
    角色/权限组
    """
    _table_name = "role_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['role_name'] = str  # root 权限组只能有一个用户
    """
    rules是规则字典.
    {
        rule: {
            method: {desc: desc, filter: filter, operate: operate}}
        }
    }
    举例:
    {
        "/login":{
            {"get": {"desc": "登录页面", "filter": 0, "operate": 1}},
            {"post": {"desc": "登录验证函数", "filter": 0, "operate": 1}},
        }
    }
    rule 是视图函数的rule,唯一不重复.取自orm_module.FlaskUrlRule.rule
    method取自orm_module.FlaskUrlRule.method
    desc: 对视图函数的说明.
    operate: 是否能操作页面上的按钮.
        0: 不能操作任何按钮
        1: 可以操作一类按钮(查询,翻页)
        2: 可以操作二类按钮(编辑)
        3: 可以操作三类按钮(删除)
    filter: 过滤器,用于限制查找范围
        0: 不做任何限制,任何人都可以访问全部的数据
        1: 只能访问本人的数据.
        2: 只能访问本部门的数据
        3: 可以访问全公司的数据
    限制:    
    用户模型必须有
    1. dept_id   部门id,也可以用组id代替 部门id中有公司id
    2. role_id    角色id
    """
    type_dict['rules'] = dict


class User(orm_module.BaseDoc):
    """用户表"""
    _table_name = "user_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_name'] = str
    type_dict['password'] = str
    type_dict['nick_name'] = str
    type_dict['dept_id'] = ObjectId
    type_dict['role_id'] = ObjectId
    type_dict['last_update'] = datetime.datetime
    type_dict['create_time'] = datetime.datetime

    @classmethod
    def add_user(cls, **kwargs) -> bool:
        """
        添加用户
        :param kwargs:
        :return:
        """
        user_name = kwargs.get("user_name", '')
        pwd = kwargs.get("password", '')
        args = {"user_name": user_name, "password": pwd}
        db = orm_module.get_client()
        conn = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db)
        write_concern = WriteConcern(w=1, j=True)
        resp = False
        with db.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=write_concern):
                r = conn.find_one(filter={'user_name': user_name})
                if r is not None:
                    ms = "账户 {} 已存在!".format(user_name)
                    raise ValueError(ms)
                else:
                    """提取其他信息"""
                    role_id_str = kwargs.get("role_id", '')
                    if isinstance(role_id_str, str) and len(role_id_str) == 24:
                        role_id = ObjectId(role_id_str)
                    else:
                        role_id = ObjectId("5bdfae528e76d6efa7b92dca")   # 来宾权限组
                    args['role_id'] = role_id
                    args['create_time'] = datetime.datetime.now()  # 创建时间
                    nick_name = kwargs.get("nick_name", "")
                    if isinstance(nick_name, str) and len(nick_name) > 0:
                        pass
                    else:
                        nick_name = "guest_{}".format()
                    r = conn.insert_one(args)
                    if r is None:
                        ms = "保存用户账户失败"
                        raise ValueError(ms)
                    else:
                        resp = True
        return resp

    @classmethod
    def login(cls, user_name: str, password: str) -> dict:
        """
        管理员登录检查
        当前管理员: root/123456
        :param user_name:
        :param password:
        :return:
        """
        mes = {"message": "success"}
        f = {"user_name": user_name}
        conn = cls.get_collection()
        r = conn.find_one(filter=f)
        if r is None:
            mes['message'] = "用户名不存在"
        else:
            if password.lower() == r['password'].lower():
                mes['_id'] = r['_id']
            else:
                mes['message'] = '密码错误'
        return mes

    @classmethod
    def get_role(cls, user: dict) -> dict:
        """
        获取一个用户的权限组.权限组中有2个特殊的权限组
        root: 系统管理员.  拥有所有权限
        guest: 来宾   所有的访问权限都是最低
        :param user:
        :return:
        """
        mes = {"message": "success"}
        if isinstance(user, (User, dict)):
            user = user.get_dict() if isinstance(user, User) else user
            role_id = user.get("role_id", '')
            if role_id == "":
                mes['message'] = "用户缺少角色信息: user: {}".format(user)
            else:
                f = {"_id": role_id}
                ses = Role.get_collection()
                r = ses.find_one(filter=f)
                if r is None:
                    mes['message'] = "错误的角色id: {}".format(role_id)
                else:
                    mes['data'] = r
        else:
            mes['message'] = "参数错误: user:{}".format(user)
        return mes


if __name__ == "__main__":
    """添加一个管理员"""
    root_init = {
        "user_name": "root", "password": "e10adc3949ba59abbe56e057f20f883e",
        "role_id": ObjectId("5bdfad388e76d6efa7b92d9e"),
        "nick_name": "系统管理员"
    }
    print(User.add_user())
    pass