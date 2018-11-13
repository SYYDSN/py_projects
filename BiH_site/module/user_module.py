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


class UserInfo(mongo_db.BaseDoc):
    _table_name = "user_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['phone'] = str
    type_dict['nick_name'] = str
    type_dict['password'] = str
    type_dict['last_login'] = datetime.datetime
    type_dict['create_date'] = datetime.datetime

    @classmethod
    def register(cls, phone: str, password: str) -> dict:
        """
        注册
        :param phone:
        :param password:
        :return:
        """
        mes = {"message": "success"}
        cli = mongo_db.get_client()
        col = mongo_db.get_conn(table_name=cls.get_table_name(), db_client=cli)
        with cli.start_session(causal_consistency=True) as session:
            with session.start_transaction():
                f = {"phone": phone}
                r = col.find_one(filter=f, session=session)
                if isinstance(r, dict):
                    mes['message'] = "手机号码重复"
                else:
                    f['password'] = password
                    now = datetime.datetime.now()
                    f['create_date'] = now
                    r = col.insert_one(document=f, session=session)
                    if r is None:
                        mes['message'] = "插入失败"
                    else:
                        pass
        return mes

    @classmethod
    def login(cls, phone: str, password: str) -> dict:
        """
        登录
        :param phone:
        :param password:
        :return:
        """
        mes = {"message": "success"}
        cli = mongo_db.get_client()
        col = mongo_db.get_conn(table_name=cls.get_table_name(), db_client=cli)
        with cli.start_session(causal_consistency=True) as session:
            with session.start_transaction():
                f = {"phone": phone}
                r = col.find_one(filter=f, session=session)
                if r is None:
                    mes['message'] = "手机号码未注册"
                else:
                    pw2 = r['password']
                    if password != pw2:
                        mes['message'] = '密码错误'
                    else:
                        now = datetime.datetime.now()
                        f = dict()
                        f['_id'] = r['_id']
                        u = {"$set": {"last_login": now}}
                        # 更新最后的登录时间
                        col.find_one_and_update(filter=f, update=u, session=session)
        return mes


if __name__ == "__main__":
    pass