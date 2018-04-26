# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
from log_module import get_logger
from item_module import Signal
import pandas as pd


Series = pd.Series
DataFrame = pd.DataFrame
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
cache = mongo_db.RedisCache()
logger = get_logger()


def draw_data_dict_from_db(begin: datetime.datetime = None, end: datetime.datetime = None) -> dict:
    """
    从数据库获取分析师的喊单信号。以老师名为一级key,产品名为二级key打包成dict并返回
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    records = dict()
    now = datetime.datetime.now()
    f = {
        "each_profit": {"$exists": True, "$ne": None},
        "exit_price": {"$exists": True},
        "update_time": {"$exists": True, "$type": 9, "$lte": now}
    }
    if isinstance(begin, datetime.datetime) and isinstance(end, datetime.datetime):
        if end <= begin:
            pass
        else:
            f['update_time'] = {
                "$exists": True, "$type": 9,
                "$lte": end, "$gte": begin
            }
    elif isinstance(begin, datetime.datetime) and end is None:
        f['update_time'] = {
            "$exists": True, "$type": 9,
            "$lte": now, "$gte": begin
        }
    elif isinstance(end, datetime.datetime) and begin is None:
        f['update_time'] = {"$exists": True, "$type": 9, "$lte": end}
    else:
        pass
    p_list = ['加元', '白银', '澳元', '日元', '英镑', '欧元', '恒指', '原油', '黄金']
    ses = mongo_db.get_conn("signal_info")
    signals = ses.find(filter=f)
    if signals.count() > 0:
        signals = [x for x in signals if x.get("product") in p_list]
        for signal in signals:
            teacher = signal['creator_name']
            product = signal['product']
            t_value = records.get(teacher)
            t_value = dict() if t_value is None else t_value
            p_value = t_value.get(product)
            p_value = list() if p_value is None else p_value
            p_value.append(signal)
            t_value[product] = p_value
            records[teacher] = t_value
    print("共计{}条记录".format(len(signals)))
    return records


def draw_data_list_from_db(begin: datetime.datetime = None, end: datetime.datetime = None) -> list:
    """
    从数据库获取分析师的喊单信号。返回数据的list对象
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    records = list()
    now = datetime.datetime.now()
    f = {
        "each_profit": {"$exists": True, "$ne": None},
        "exit_price": {"$exists": True},
        "update_time": {"$exists": True, "$type": 9, "$lte": now}
    }
    if isinstance(begin, datetime.datetime) and isinstance(end, datetime.datetime):
        if end <= begin:
            pass
        else:
            f['update_time'] = {
                "$exists": True, "$type": 9,
                "$lte": end, "$gte": begin
            }
    elif isinstance(begin, datetime.datetime) and end is None:
        f['update_time'] = {
            "$exists": True, "$type": 9,
            "$lte": now, "$gte": begin
        }
    elif isinstance(end, datetime.datetime) and begin is None:
        f['update_time'] = {"$exists": True, "$type": 9, "$lte": end}
    else:
        pass
    p_list = ['加元', '白银', '澳元', '日元', '英镑', '欧元', '恒指', '原油', '黄金']
    ses = mongo_db.get_conn("signal_info")
    signals = ses.find(filter=f)
    if signals.count() > 0:
        records = [x for x in signals if x.get("product") in p_list]
    else:
        pass
    print("共计{}条记录".format(len(records)))
    return records


def calculate_win_per(begin: str = None, end: str = None) -> dict:
    """
    计算老师的胜率
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    begin = mongo_db.get_datetime_from_str(begin)
    end = mongo_db.get_datetime_from_str(end)
    raw = draw_data_dict_from_db(begin, end)
    res = dict()
    for t_name, t_value in raw.items():
        t_dict = dict()
        for p_name, p_value in t_value.items():
            """计算单个产品的胜率"""
            p_dict = dict()
            p_win_count = 0
            for record in p_value:
                if record['each_profit'] >= 0:
                    p_win_count += 1
                else:
                    pass
            p_count = len(p_value)
            p_win_per = p_win_count / p_count

            p_dict["per"] = p_win_per
            p_dict['count'] = p_count
            t_dict[p_name] = p_dict
        res[t_name] = t_dict
    return res

if __name__ == "__main__":
    calculate_win_per()

