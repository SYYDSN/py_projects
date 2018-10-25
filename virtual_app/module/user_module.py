#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
import datetime
from tools_module import get_logger


"""用户模块"""


logger = get_logger()
ObjectId = orm_module.ObjectId
WriteConcern = orm_module.WriteConcern


class AppUser(orm_module.BaseDoc):
    """app用户"""
    _table_name = "news_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_name'] = str
    type_dict['password'] = str
    type_dict['sign'] = str               # 签名
    type_dict['reg_time'] = datetime.datetime  # 注册时间

    @classmethod
    def reg(cls, user_name: str, password: str) -> dict:
        """
        用户注册
        :param user_name:
        :param password:
        :return:
        """
        mes = {"message": "success"}
        db_client = orm_module.get_client()
        write_concern = WriteConcern(w="majority", j=True)
        con = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client, write_concern=write_concern)
        with db_client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=write_concern):
                f = {"user_name": user_name}
                r = con.find_one(filter=f)
                if r is None:
                    f['password'] = password
                    insert = con.insert_one(document=f)
                else:
                    mes['message'] = "用户名已被占用"
        return mes


if __name__ == "__main__":
    AppUser.reg("jack", "1234324")
    pass