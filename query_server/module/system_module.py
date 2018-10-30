#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
from pymongo import WriteConcern
import datetime
from hashlib import md5


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
    type_dict['role_name'] = str
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
    def add_user(cls, user_name: str, password: str, shell: bool = False) -> bool:
        """
        添加管理员.此函数应该只在命令行运行
        :param user_name:
        :param password:
        :param shell: 是否是在命令行执行?
        :return:
        """
        if shell:
            pwd = md5(password.encode()).hexdigest()
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
                        r = conn.insert_one(args)
                        if r is None:
                            ms = "保存管理员账户失败"
                            raise ValueError(ms)
                        else:
                            resp = True
            return resp
        else:
            ms = "只能在命令行下运行此方法!"
            raise RuntimeError(ms)

    @classmethod
    def login(cls, user_name: str, password: str) -> dict:
        """
        管理员登录检查
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


if __name__ == "__main__":
    rule = orm_module.FlaskUrlRule.find_one(filter_dict={"_id": ObjectId("5bd6d8aa18bda6f2e14b6f55")})
    rule['desc'] = "登录页面和登录api.无论是否登录,所有人都可以访问对应的页面的api接口"
    orm_module.FlaskUrlRule.save_doc(doc=rule)
    pass