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
        "exit_price": {"$exists": True, "$ne": None},
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
    count = 0
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
            count += 1
    print("共计{}条记录".format(count))
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
        "exit_price": {"$exists": True, "$ne": None},
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
            each_profit = signal['each_profit']
            enter_time = signal['datetime']
            exit_time = signal['update_time']
            win = 1 if each_profit >= 0 else 0
            temp = dict()
            temp['teacher'] = teacher
            temp['product'] = product
            temp['each_profit'] = each_profit  # 每手实际盈利
            temp['enter_date'] = enter_time.strftime("%F")  # 进场日
            temp['exit_date'] = exit_time.strftime("%F")  # 出场日
            temp['win'] = win
            records.append(temp)
    else:
        pass
    print("共计{}条记录".format(len(records)))
    return records


def calculate_win_per_by_teacher(begin: str = None, end: str = None) -> dict:
    """
    以老师为分组依据计算的胜率
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


def calculate_win_per_by_product(begin: str = None, end: str = None) -> dict:
    """
    以产品为分组依据计算的胜率
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    begin = mongo_db.get_datetime_from_str(begin)
    end = mongo_db.get_datetime_from_str(end)
    raw = draw_data_dict_from_db(begin, end)
    res = dict()
    for t_name, t_value in raw.items():
        for p_name, p_value in t_value.items():
            out_dict = res.get(p_name)
            out_dict = dict() if out_dict is None else out_dict
            """计算单个产品的胜率"""
            inner_dict = dict()
            p_win_count = 0
            for record in p_value:
                if record['each_profit'] >= 0:
                    p_win_count += 1
                else:
                    pass
            p_count = len(p_value)
            p_win_per = p_win_count / p_count

            inner_dict["per"] = p_win_per
            inner_dict['count'] = p_count
            out_dict[t_name] = inner_dict
            res[p_name] = out_dict
    return res


def query_chart_data(chart_type: str = "teacher", begin: str = None, end: str = None) -> dict:
    """
    查询分析老师胜率的图表的数据
    :param chart_type: 图表的分组类型,默认是 bar(柱状图)以老师分组
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    res = dict()
    if chart_type == "teacher":
        """以老师分组"""
        res = calculate_win_per_by_teacher(begin=begin, end=end)
    elif chart_type == "product":
        """以产品分组"""
        res = calculate_win_per_by_product(begin=begin, end=end)
    elif chart_type == "summary":
        """返回原始数组,让前端自己分组"""
        res = draw_data_list_from_db(begin=begin, end=end)
    else:
        pass
    return res


if __name__ == "__main__":
    # calculate_win_per_by_product()
    draw_data_list_from_db()
    pass

