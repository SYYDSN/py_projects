#  -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
from log_module import get_logger
import mongo_db
from send_moudle import *
from pymongo import ReturnDocument
import requests
import datetime


ObjectId = mongo_db.ObjectId
app_key = 'gavQrjmjxekfyK4qeZAI0usSZmZq0oww'
headers = {'Authorization': 'Bearer {}'.format(app_key)}


"""简道云相关的模块"""


class RefreshInfo(mongo_db.BaseDoc):
    """
    记录刷新时间
    """
    _table_name = "refresh_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['table_name'] = str
    type_dict['time'] = datetime.datetime  # 刷新时间

    @classmethod
    def get_prev(cls, table_name: str) -> (datetime.datetime, None):
        """
        获取上一次的刷新信息
        :param table_name: 表名
        :return:
        """
        f = {"table_name": table_name}
        r = cls.find_one_plus(filter_dict=f, instance=False)
        if r is None:
            pass
        else:
            return r['time']

    @classmethod
    def update_time(cls,  table_name: str) -> None:
        """
        更新刷新时间
        :param table_name:
        :return:
        """
        f = {"table_name": table_name}
        u = {"$set": {"time": datetime.datetime.now()}}
        cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)


def listen_api(**kwargs):
    """
    监听简道云通过.api推送过来的消息
    :param kwargs:
    :return:
    """


def process_praise(**kwargs) -> None:
    """
    处理简道云发送过来的战报海报消息
    :param kwargs:
    :return:
    """


if __name__ == "__main__":
    pass



