# -*- coding: utf-8 -*-
import os
import sys
__project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir not in sys.path:
    sys.path.append(__project_dir)
import mongo_db
import json
import datetime
import pandas as pd
from pandas import Series
from pandas import DataFrame
from log_module import get_logger


"""数据腌制工具"""


logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


def transform_type(in_dict: dict) -> dict:
    """
    转换doc的value的类型
    :param in_dict:
    :return:
    """
    res = dict()
    for k, v in in_dict.items():
        if isinstance(v, datetime.datetime):
            v = v.strftime("%Y-%m-%d %H:%M:%S.%f")
        elif isinstance(v, ObjectId):
            v = str(v)
        elif isinstance(v, DBRef):
            v = str(v.id)
        else:
            pass
        if k != "loc":
            if k == "pr":
                res['source'] = "gps"
            elif k == "be":
                res['declination'] = v
            else:
                res[k] = v
        else:
            pass
    return res


def rebuild_json():
    """从本机数据库创建json文件"""
    f = {"user_id": {"$exists": True, "$type": 3}, "pr": "gps"}
    ses = mongo_db.get_conn("gps_info")
    records = ses.find(filter=f)
    records = [transform_type(x) for x in records]
    d_path = os.path.join(__project_dir, "tool_box", "json")
    if not os.path.exists(d_path):
        os.makedirs(d_path)
    f_path = os.path.join(d_path, "all_gps.json")
    with open(f_path, mode="w", encoding="utf-8") as file:
        json.dump(records, file)


def read_json() -> list:
    """
    从本地读取json文件
    :return:
    """
    d_path = os.path.join(__project_dir, "tool_box", "json")
    f_path = os.path.join(d_path, "all_gps.json")
    with open(f_path, mode="r", encoding="utf-8") as file:
        data = json.load(file)
    data.sort(key=lambda obj: mongo_db.get_datetime_from_str(obj['time']), reverse=True)
    data_by_user = dict()
    count_by_user = dict()
    for x in data:
        u_id = x['user_id']
        if u_id not in data_by_user:
            data_by_user[u_id] = [x]
            count_by_user[u_id] = 1
        else:
            data_by_user[u_id].append(x)
            count = count_by_user[u_id]
            count += 1
            count_by_user[u_id] = count
    count_by_user = [{"id": k, "count": v} for k, v in count_by_user.items()]
    count_by_user.sort(key=lambda obj: obj['count'], reverse=True)
    ids = count_by_user[0: 3]
    dd_path = os.path.join(d_path, "single_by_user")
    if not os.path.exists(dd_path):
        os.makedirs(dd_path)
    ids = [x['id'] for x in ids]
    for i, id in enumerate(ids):
        name = "user_{}_gps.json".format(i + 1)
        v = data_by_user[id]
        with open(os.path.join(dd_path, name), mode="w", encoding="utf-8") as f:
            json.dump(v, f)


def record_digest():
    """获取文件摘要"""
    d_path = os.path.join(__project_dir, "tool_box", "json", "single_by_user")
    names = os.listdir(d_path)
    for name in names:
        p = os.path.join(d_path, name)
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        date_list = list()
        for x in data:
            the_date = x['time'].split(" ")[0]
            if the_date not in date_list:
                date_list.append(the_date)
        print(name)
        print(data[0]['user_id'])
        print(len(data))
        print(len(date_list))
        print(date_list)


if __name__ == "__main__":
    record_digest()
    pass