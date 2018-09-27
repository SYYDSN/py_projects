#  -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
from log_module import get_logger
import mongo_db
from send_moudle import *
import datetime


ObjectId = mongo_db.ObjectId


"""简道云相关的模块"""


class CustomerRelation(mongo_db.BaseFile):
    """
    客户和销售人员之间的对应关系
    """
    _table_name = "customer_relation"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['raw_id'] = ObjectId
    type_dict['mt4_account'] = str  # mt4账户,唯一
    type_dict['customer'] = str  # 客户名
    type_dict['sales'] = str  # 销售名
    type_dict['manager'] = str  # 经理名
    type_dict['director'] = str  # 总监名
    type_dict['platform'] = str  # 平台名
    type_dict['create_time'] = datetime.datetime  # 创建时间

    @classmethod
    def get_init(cls, **kwargs):
        """
        从简道云返回的数据中,生产初始化对象的参数集合
        :param kwargs:
        :return:
        """
        init = dict()
        init['raw_id'] = ObjectId(kwargs.get('_id', None))
        init['mt4_account'] = kwargs.get('_widget_1515400344933', '')
        init['customer'] = kwargs.get('_widget_1515400344920', '')
        init['sales'] = kwargs.get('_widget_1520476984707', '')
        init['manager'] = kwargs.get('_widget_1520476984720', '')
        init['director'] = kwargs.get('_widget_1520476984733', '')
        init['platform'] = kwargs.get('_widget_1517984569439', '')
        create_time = kwargs.get('createTime', '')
        a_time = mongo_db.get_datetime_from_str(create_time)
        init['create_time'] = a_time if isinstance(a_time, datetime.datetime) else create_time
        return init
