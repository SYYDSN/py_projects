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


class Root(orm_module.BaseDoc):
    """管理员"""
    _table_name = "root_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_name'] = str
    type_dict['password'] = str
    type_dict['time'] = datetime.datetime

    @classmethod
    def add_user(cls, user_name: str, password: str, shell: bool = False) -> bool:
        """
        添加用户.此函数应该只在命令行运行
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
        登录检查
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


class User(orm_module.BaseDoc):
    """用户表"""


if __name__ == "__main__":
    print(Root.add_user("root", "123456", True))
    pass