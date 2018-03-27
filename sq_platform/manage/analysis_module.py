#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from manage.company_module import Employee
import mongo_db
import datetime
from pandas import Series
from pandas import DataFrame
import pandas as pd


"""分析模块"""


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


def get_user_data(filter_dict: dict = None):
    """
    获取用户的注册信息,用于数据分析
    :param filter_dict:
    :return:
    """
    if filter_dict is None:
        filter_dict = {'create_date': {"$gte": mongo_db.get_datetime_from_str("2018-3-20 0:0:0")}}
    users = Employee.find_plus(filter_dict=filter_dict, to_dict=True)
    objs = list()
    for user in users:
        obj = Series(user)
        objs.append(obj)
    frame = DataFrame(data=objs, index=range(len(objs)))
    return frame


if __name__ == "__main__":
    res = get_user_data()
    print(res)
    pass