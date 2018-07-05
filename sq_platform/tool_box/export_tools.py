# -*- coding: utf-8 -*-
import os
import sys
__project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir not in sys.path:
    sys.path.append(__project_dir)
import mongo_db
import datetime


"""
数据导出工具,目前实现的功能如下:
1. 导出指定用户,制定日期的行车事件.
"""


ObjectId = mongo_db.ObjectId


def export_alarm_event(user_id: (str, ObjectId), begin: (str, datetime.datetime),
                       end: (str, datetime.datetime) = None) -> list:
    """
    导出指定用户,制定日期的行车事件.
    :param user_id:
    :param begin:
    :param end:
    :return:
    """
    user_id = str(user_id) if isinstance(user_id, ObjectId) else user_id
    begin = mongo_db.get_datetime_from_str(begin) if isinstance(begin, str) else begin
    end = begin + datetime.timedelta(days=1) if end is None else end
    f = {"vehicle_id": user_id, "start_time": {"$gte": begin}, "end_time": {"$lte": end}}
