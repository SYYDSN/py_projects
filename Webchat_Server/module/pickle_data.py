# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
from log_module import get_logger
import re
import pandas as pd
import math


"""
计算数据的模块
"""


Series = pd.Series
DataFrame = pd.DataFrame
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
cache = mongo_db.RedisCache()
logger = get_logger()
p_list = ['加元', '白银', '澳元', '日元', '英镑', '欧元', '恒指', '原油', '黄金']


def draw_data_dict_from_db(begin: datetime.datetime = None, end: datetime.datetime = None) -> dict:
    """
    细分产品种类，从数据库获取分析师的喊单信号。以老师名为一级key,产品名为二级key打包成dict并返回
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    records = dict()
    now = datetime.datetime.now()
    f = {
        "each_profit": {"$exists": True, "$ne": None},
        "exit_price": {"$exists": True, "$ne": None},
        "update_time": {"$exists": True, "$type": 9}
    }
    if isinstance(begin, datetime.datetime) and isinstance(end, datetime.datetime):
        if end <= begin:
            pass
        else:
            f['datetime'] = {
                "$exists": True, "$type": 9,
                "$lte": end, "$gte": begin
            }
    elif isinstance(begin, datetime.datetime) and end is None:
        f['datetime'] = {
            "$exists": True, "$type": 9,
            "$lte": now, "$gte": begin
        }
    elif isinstance(end, datetime.datetime) and begin is None:
        f['datetime'] = {"$exists": True, "$type": 9, "$lte": end}
    else:
        pass

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


def draw_data_dict_from_db_mix(begin: datetime.datetime = None, end: datetime.datetime = None) -> dict:
    """
    不细分产品种类，从数据库获取分析师的喊单信号。以老师名为一级key,产品名为二级key打包成dict并返回
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    records = dict()
    now = datetime.datetime.now()
    f = {
        "each_profit": {"$exists": True, "$ne": None},
        "exit_price": {"$exists": True, "$ne": None},
        "update_time": {"$exists": True, "$type": 9}
    }
    if isinstance(begin, datetime.datetime) and isinstance(end, datetime.datetime):
        if end <= begin:
            pass
        else:
            f['datetime'] = {
                "$exists": True, "$type": 9,
                "$lte": end, "$gte": begin
            }
    elif isinstance(begin, datetime.datetime) and end is None:
        f['datetime'] = {
            "$exists": True, "$type": 9,
            "$lte": now, "$gte": begin
        }
    elif isinstance(end, datetime.datetime) and begin is None:
        f['datetime'] = {"$exists": True, "$type": 9, "$lte": end}
    else:
        pass

    ses = mongo_db.get_conn("signal_info")
    signals = ses.find(filter=f)
    count = 0
    if signals.count() > 0:
        for x in signals:
            if x.get("product") in p_list:
                count += 1
                teacher = ObjectId(x['creator_id']) if isinstance(x['creator_id'], str) else x['creator_id']
                t_value = records.get(teacher)
                t_value = list() if t_value is None else t_value
                t_value.append(x)
                records[teacher] = t_value
            else:
                pass

    print("共计{}条记录".format(count))
    return records


def draw_data_dict_from_db_mix2(t_id: (str, ObjectId), begin: datetime.datetime = None, end: datetime.datetime = None) -> dict:
    """
    不细分产品种类，从数据库trade获取分析师的喊单信号。
    :param t_id:
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    records = dict()
    now = datetime.datetime.now()
    f = {
        "teacher_id": ObjectId(t_id) if isinstance(t_id, str) else t_id,
        "each_profit": {"$exists": True, "$ne": None},
        "exit_price": {"$exists": True, "$ne": None},
        "exit_time": {"$exists": True, "$type": 9}
    }
    if isinstance(begin, datetime.datetime) and isinstance(end, datetime.datetime):
        if end <= begin:
            pass
        else:
            f['exit_time'] = {
                "$exists": True, "$type": 9,
                "$lte": end, "$gte": begin
            }
    elif isinstance(begin, datetime.datetime) and end is None:
        f['exit_time'] = {
            "$exists": True, "$type": 9,
            "$lte": now, "$gte": begin
        }
    elif isinstance(end, datetime.datetime) and begin is None:
        f['exit_time'] = {"$exists": True, "$type": 9, "$lte": end}
    else:
        pass

    ses = mongo_db.get_conn("trade")
    s = [('exit_time', -1)]
    signals = ses.find(filter=f, sort=s)
    signals = [x for x in signals]
    print("共计{}条记录".format(len(signals)))
    return signals


def draw_data_list_from_db(t_id: (str, ObjectId) = None, begin: datetime.datetime = None, end: datetime.datetime = None) -> list:
    """
    从数据库获取分析师的(已经close)喊单信号。返回数据的list对象
    :param t_id: 老师id
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    table_name = "trade"
    # table_name = "signal_info"
    records = list()
    now = datetime.datetime.now()
    if isinstance(t_id, ObjectId) or (isinstance(t_id, str) and len(t_id) == 24):
        if table_name == "signal_info":
            f = {
                "creator_id": str(t_id) if isinstance(t_id, ObjectId) else t_id,
                "each_profit": {"$exists": True, "$ne": None},
                "exit_price": {"$exists": True, "$ne": None},
                "update_time": {"$exists": True, "$type": 9}
            }
        else:
            f = {
                "teacher_id": ObjectId(t_id) if isinstance(t_id, str) else t_id,
                "each_profit": {"$exists": True, "$ne": None},
                "exit_price": {"$exists": True, "$ne": None},
                "exit_time": {"$exists": True, "$type": 9}
            }
    else:
        if table_name == "signal_info":
            f = {
                "each_profit": {"$exists": True, "$ne": None},
                "exit_price": {"$exists": True, "$ne": None},
                "update_time": {"$exists": True, "$type": 9}
            }
        else:
            f = {
                "each_profit": {"$exists": True, "$ne": None},
                "exit_price": {"$exists": True, "$ne": None},
                "exit_time": {"$exists": True, "$type": 9}
            }
    if isinstance(begin, datetime.datetime) and isinstance(end, datetime.datetime):
        if end <= begin:
            pass
        else:
            if table_name == "signal_info":
                f['datetime'] = {
                    "$exists": True, "$type": 9,
                    "$lte": end, "$gte": begin
                }
            else:
                f['enter_time'] = {
                    "$exists": True, "$type": 9,
                    "$lte": end, "$gte": begin
                }
    elif isinstance(begin, datetime.datetime) and end is None:
        if table_name == "signal_info":
            f['datetime'] = {
                "$exists": True, "$type": 9,
                "$lte": now, "$gte": begin
            }
        else:
            f['enter_time'] = {
                "$exists": True, "$type": 9,
                "$lte": now, "$gte": begin
            }
    elif isinstance(end, datetime.datetime) and begin is None:
        if table_name == "signal_info":
            f['datetime'] = {"$exists": True, "$type": 9, "$lte": end}
        else:
            f['enter_time'] = {"$exists": True, "$type": 9, "$lte": end}
    else:
        pass

    ses = mongo_db.get_conn(table_name=table_name)
    if table_name == "signal_info":
        s = [("update_time", -1)]
    else:
        s = [("exit_time", -1)]
    signals = ses.find(filter=f, sort=s)
    if signals.count() > 0:
        signals = [x for x in signals if x.get("product") in p_list]
        for signal in signals:
            if table_name == "signal_info":
                teacher = signal.get('creator_id')
            else:
                teacher = signal.get('teacher_id')
            product = signal['product']
            each_profit = signal['each_profit']
            if table_name == "signal_info":
                enter_time = signal['datetime']
            else:
                enter_time = signal['enter_time']
            if table_name == "signal_info":
                exit_time = signal['update_time']
            else:
                exit_time = signal['exit_time']
            win = 1 if each_profit >= 0 else 0
            temp = dict()
            temp['teacher'] = teacher
            temp['product'] = product
            temp['direction'] = signal['direction']
            temp['enter_price'] = signal['enter_price']
            temp['exit_price'] = signal['exit_price']
            temp['each_profit'] = round(each_profit, 1)  # 每手实际盈利
            temp['enter_time'] = enter_time.strftime("%F")  # 进场日
            temp['exit_time'] = exit_time.strftime("%F")  # 出场日
            temp['timestamp'] = exit_time.timestamp()  # 出场日的timestamp对象，用于排序
            week_list = exit_time.isocalendar()
            temp['week'] = "{}年{}周".format(week_list[0], week_list[1])
            temp['win'] = win
            records.append(temp)
    else:
        pass
    print("共计{}条记录".format(len(records)))
    return records


def draw_hold_list_from_db(t_id: (str, ObjectId) = None, begin: datetime.datetime = None, end: datetime.datetime = None) -> list:
    """
    从数据库获取分析师的持仓。返回数据的list对象 ,不再建议使用,请使用hold_info_from_db
    :param t_id: 老师id
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    table_name = "trade"
    # table_name = "signal_info"
    records = list()
    now = datetime.datetime.now()
    if isinstance(t_id, ObjectId) or (isinstance(t_id, str) and len(t_id) == 24):
        if table_name == "signal_info":
            f = {
                "creator_id": str(t_id) if isinstance(t_id, ObjectId) else t_id,
                "exit_price": {"$exists": False}

            }
        else:
            f = {
                "teacher_id": ObjectId(t_id) if isinstance(t_id, str) else t_id,
                "exit_price": {"$exists": False}
            }
    else:
        if table_name == "signal_info":
            f = {
                "exit_price": {"$exists": False}
            }
        else:
            f = {
                "exit_price": {"$exists": False}
            }
    if isinstance(begin, datetime.datetime) and isinstance(end, datetime.datetime):
        if end <= begin:
            pass
        else:
            if table_name == "signal_info":
                f['datetime'] = {
                    "$exists": True, "$type": 9,
                    "$lte": end, "$gte": begin
                }
            else:
                f['enter_time'] = {
                    "$exists": True, "$type": 9,
                    "$lte": end, "$gte": begin
                }
    elif isinstance(begin, datetime.datetime) and end is None:
        if table_name == "signal_info":
            f['datetime'] = {
                "$exists": True, "$type": 9,
                "$lte": now, "$gte": begin
            }
        else:
            f['enter_time'] = {
                "$exists": True, "$type": 9,
                "$lte": now, "$gte": begin
            }
    elif isinstance(end, datetime.datetime) and begin is None:
        if table_name == "signal_info":
            f['datetime'] = {"$exists": True, "$type": 9, "$lte": end}
        else:
            f['enter_time'] = {"$exists": True, "$type": 9, "$lte": end}
    else:
        pass

    ses = mongo_db.get_conn(table_name=table_name)
    if table_name == "signal_info":
        s = [("create_time", -1)]
    else:
        s = [("enter_time", -1)]
    signals = ses.find(filter=f, sort=s)
    if signals.count() > 0:
        signals = [x for x in signals if x.get("product") in p_list]
        for signal in signals:
            if table_name == "signal_info":
                teacher = signal.get('creator_id')
            else:
                teacher = signal.get('teacher_id')
            product = signal['product']
            each_profit = signal['each_profit']
            if table_name == "signal_info":
                enter_time = signal['datetime']
            else:
                enter_time = signal['enter_time']
            if table_name == "signal_info":
                exit_time = signal.get('update_time')
            else:
                exit_time = signal['exit_time']
            win = 1 if each_profit >= 0 else 0
            temp = dict()
            temp['teacher'] = teacher
            temp['product'] = product
            temp['direction'] = signal['direction']
            temp['each_profit'] = each_profit  # 每手实际盈利
            temp['enter_time'] = enter_time
            temp['enter_time_str'] = enter_time.strftime("%F")  # 进场日
            temp['hold_hour'] = round((now - enter_time).total_seconds() / 3600, 0)  # 持仓时间
            temp['enter_price'] = signal['enter_price']
            temp['exit_date'] = exit_time
            temp['exit_date_str'] = exit_time.strftime("%F")  # 出场日
            temp['timestamp'] = exit_time.timestamp()  # 出场日的timestamp对象，用于排序
            week_list = exit_time.isocalendar()
            temp['week'] = "{}年{}周".format(week_list[0], week_list[1])
            temp['win'] = win
            records.append(temp)
    else:
        pass
    print("共计{}条记录".format(len(records)))
    return records


def hold_info_from_db(t_id: (str, ObjectId) = None, begin: datetime.datetime = None,
                      end: datetime.datetime = None, h_id: (str, ObjectId) = None) -> list:
    """
    从数据库获取分析师的持仓。,替代draw_hold_list_from_db函数.
    如果h_id是None,返回全部数据的list对象,否则返回对应的记录的list(单个元素的list)
    :param t_id: 老师id
    :param begin: 开始时间
    :param end:  截至时间
    :param h_id:  持仓Trade的_id
    :return:
    """
    table_name = "trade"
    records = list()
    now = datetime.datetime.now()
    if isinstance(t_id, ObjectId) or (isinstance(t_id, str) and len(t_id) == 24):
        f = {
            "teacher_id": ObjectId(t_id) if isinstance(t_id, str) else t_id,
            "exit_price": {"$exists": False}
        }
    else:
        f = {
            "exit_price": {"$exists": False}
        }
    if isinstance(begin, datetime.datetime) and isinstance(end, datetime.datetime):
        if end <= begin:
            pass
        else:
            f['enter_time'] = {
                "$exists": True, "$type": 9,
                "$lte": end, "$gte": begin
            }
    elif isinstance(begin, datetime.datetime) and end is None:
        f['enter_time'] = {
            "$exists": True, "$type": 9,
            "$lte": now, "$gte": begin
        }
    elif isinstance(end, datetime.datetime) and begin is None:
        f['enter_time'] = {"$exists": True, "$type": 9, "$lte": end}
    else:
        pass
    if isinstance(h_id, str) and len(h_id) == 24:
        f['_id'] = ObjectId(h_id)
    ses = mongo_db.get_conn(table_name=table_name)
    if table_name == "signal_info":
        s = [("create_time", -1)]
    else:
        s = [("enter_time", -1)]
    signals = ses.find(filter=f, sort=s)
    if signals.count() > 0:
        signals = [x for x in signals if x.get("product") in p_list]
        for signal in signals:
            teacher = signal.get('teacher_id')
            product = signal['product']
            code = signal.get("code", "")
            lots = signal.get("lots", 1)
            each_profit = signal['each_profit']
            enter_time = signal['enter_time']
            win = 1 if each_profit >= 0 else 0
            temp = dict()
            temp['_id'] = signal['_id']
            temp['teacher'] = teacher
            temp['product'] = product
            temp['lots'] = lots
            temp['code'] = code
            temp['direction'] = signal['direction']
            temp['each_profit'] = each_profit  # 每手实际盈利
            temp['enter_time'] = enter_time
            temp['enter_time_str'] = enter_time.strftime("%F")  # 进场日
            temp['hold_hour'] = round((now - enter_time).total_seconds() / 3600, 0)  # 持仓时间
            temp['enter_price'] = signal['enter_price']
            temp['timestamp'] = enter_time.timestamp()  # 出场日的timestamp对象，用于排序
            week_list = enter_time.isocalendar()
            temp['week'] = "{}年{}周".format(week_list[0], week_list[1])
            temp['win'] = win
            records.append(temp)
    else:
        pass
    print("共计{}条记录".format(len(records)))
    return records



def calculate_win_per_by_teacher(begin: str = None, end: str = None) -> dict:
    """
    以老师为分组依据计算的胜率，分每个产品的胜率
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


def calculate_win_per_by_teacher_mix(begin: str = None, end: str = None) -> dict:
    """
    以老师为分组依据计算的胜率,不再细分每个产品的胜率，而是统一计算
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    if end is None:
        end = datetime.datetime.now()
    else:
        end = mongo_db.get_datetime_from_str(end)
    if begin is None:
        begin = end - datetime.timedelta(days=30)
    else:
        begin = mongo_db.get_datetime_from_str(begin)

    raw = draw_data_dict_from_db_mix(begin, end)
    res = dict()
    for t_id, t_value in raw.items():
        t_dict = dict()
        p_win_count = 0
        for record in t_value:
            if record['each_profit'] >= 0:
                p_win_count += 1
            else:
                pass
        p_count = len(t_value)
        p_win_per = p_win_count / p_count
        p_win_per = round(p_win_per * 100, 1)
        t_dict["win"] = p_win_per
        t_dict['count'] = p_count
        res[t_id] = t_dict
    return res


def calculate_win_per_by_teacher_mix(t_id: (str, ObjectId), begin: str = None, end: str = None) -> dict:
    """
    计算老师的胜率和应利率,不再细分每个产品的胜率，而是统一计算
    :param t_id:
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    if end is None:
        end = datetime.datetime.now()
    else:
        end = mongo_db.get_datetime_from_str(end)
    if begin is None:
        begin = end - datetime.timedelta(days=30)
    else:
        begin = mongo_db.get_datetime_from_str(begin)

    raw = draw_data_dict_from_db_mix2(t_id, begin, end)
    res = dict()
    p_win_count = 0
    p_count = len(raw)
    for x in raw:
        if x['each_profit'] >= 0:
            p_win_count += 1
        else:
            pass
    p_win_per = p_win_count / p_count
    p_win_per = round(p_win_per * 100, 1)
    res['t_id'] = t_id
    res['win_ratio'] = p_win_per
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


def calculate_win_per_by_month(begin: str = None, end: str = None) -> dict:
    """
    以时间（月）切分，以老师为分组依据， 以产品分类计算的胜率
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    begin = mongo_db.get_datetime_from_str(begin)
    end = mongo_db.get_datetime_from_str(end)
    raw = draw_data_list_from_db(begin, end)
    res = dict()
    pattern = re.compile(r'^20\d{2}-\d{2}')
    for record in raw:
        p_name = record['product']
        t_name = record['teacher']

        p_dict = res.get(p_name)
        p_dict = dict() if p_dict is None else p_dict
        t_dict = p_dict.get(t_name)
        t_dict = dict() if t_dict is None else t_dict
        month = re.match(pattern, record['enter_date']).group()
        m_dict = dict() if t_dict.get(month) is None else t_dict[month]

        win_count = 0 if m_dict.get("win_count") is None else m_dict['win_count']
        all_count = 0 if m_dict.get("all_count") is None else m_dict['all_count']
        all_count += 1
        if record['win'] == 1:
            win_count += 1
        else:
            pass
        m_dict['win_count'] = win_count
        m_dict['all_count'] = all_count
        t_dict[month] = m_dict
        p_dict[t_name] = t_dict
        res[p_name] = p_dict

    return res


def calculate_win_per_by_week(begin: str = None, end: str = None) -> dict:
    """
    以时间（周）切分，以老师为分组依据， 以产品分类计算的胜率
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    begin = mongo_db.get_datetime_from_str(begin)
    end = mongo_db.get_datetime_from_str(end)
    raw = draw_data_list_from_db(begin, end)
    res = dict()
    pattern = re.compile(r'^20\d{2}-\d{2}')
    for record in raw:
        p_name = record['product']
        t_name = record['teacher']

        p_dict = res.get(p_name)
        p_dict = dict() if p_dict is None else p_dict
        t_dict = p_dict.get(t_name)
        t_dict = dict() if t_dict is None else t_dict
        week = record['week']
        w_dict = dict() if t_dict.get(week) is None else t_dict[week]

        win_count = 0 if w_dict.get("win_count") is None else w_dict['win_count']
        all_count = 0 if w_dict.get("all_count") is None else w_dict['all_count']
        all_count += 1
        if record['win'] == 1:
            win_count += 1
        else:
            pass
        w_dict['win_count'] = win_count
        w_dict['all_count'] = all_count
        t_dict[week] = w_dict
        p_dict[t_name] = t_dict
        res[p_name] = p_dict

    return res


def calculate_win_per_by_week_single(t_id: (str, ObjectId) = None, begin: str = None, end: str = None) -> dict:
    """
    以时间（周）切分，查询单个老师的， 以产品分类计算的胜率
    :param t_id:
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    begin = mongo_db.get_datetime_from_str(begin)
    end = mongo_db.get_datetime_from_str(end)
    raw = draw_data_list_from_db(t_id, begin, end)
    hold = hold_info_from_db(t_id, begin, end)
    res = dict()
    for record in raw:
        p_name = record['product']
        t_id = record['teacher']

        p_dict = res.get(p_name)
        p_dict = dict() if p_dict is None else p_dict
        # t_dict = p_dict.get(t_id)
        # t_dict = dict() if t_dict is None else t_dict
        week = record['week']
        # w_dict = dict() if t_dict.get(week) is None else t_dict[week]
        w_dict = dict() if p_dict.get(week) is None else p_dict[week]

        win_count = 0 if w_dict.get("win_count") is None else w_dict['win_count']
        all_count = 0 if w_dict.get("all_count") is None else w_dict['all_count']
        all_count += 1
        if record['win'] == 1:
            win_count += 1
        else:
            pass
        w_dict['win_count'] = win_count
        w_dict['all_count'] = all_count
        w_dict['timestamp'] = record['timestamp']
        # t_dict[week] = w_dict
        p_dict[week] = w_dict
        # p_dict[t_id] = t_dict
        res[p_name] = p_dict
    r = list()
    for k, v in res.items():
        temp = dict()
        temp['_t_id'] = str(t_id)
        temp['product'] = k
        d = [{
            "week": k, "all_count": v['all_count'],
            "win_count": v['win_count'], "timestamp": v['timestamp'],
            "win_per": 0 if v['all_count'] == 0 else round((v['win_count'] / v['all_count']) * 100, 1)
            } for k, v in v.items()]
        d.sort(key=lambda obj: obj['timestamp'], reverse=True)
        temp['data'] = d
        r.append(temp)
    r.sort(key=lambda obj: len(obj['data']), reverse=True)
    data = {"chart": r, "history": raw[0: 20], "hold": hold[0: 10]}
    return data


def calculate_win_per_by_week_single2(t_id: (str, ObjectId) = None, begin: str = None, end: str = None) -> dict:
    """
    以时间（周）切分，查询单个老师的， 以产品分类计算的胜率
    和calculate_win_per_by_week_single函数不同，这个是指向trade表的
    :param t_id:
    :param begin: 开始时间
    :param end:  截至时间
    :return:
    """
    begin = mongo_db.get_datetime_from_str(begin)
    end = mongo_db.get_datetime_from_str(end)
    raw = draw_data_list_from_db(t_id, begin, end)
    hold = draw_hold_list_from_db(t_id, begin, end)
    res = dict()
    for record in raw:
        p_name = record['product']
        t_id = record['teacher']

        p_dict = res.get(p_name)
        p_dict = dict() if p_dict is None else p_dict
        # t_dict = p_dict.get(t_id)
        # t_dict = dict() if t_dict is None else t_dict
        week = record['week']
        # w_dict = dict() if t_dict.get(week) is None else t_dict[week]
        w_dict = dict() if p_dict.get(week) is None else p_dict[week]

        win_count = 0 if w_dict.get("win_count") is None else w_dict['win_count']
        all_count = 0 if w_dict.get("all_count") is None else w_dict['all_count']
        all_count += 1
        if record['win'] == 1:
            win_count += 1
        else:
            pass
        w_dict['win_count'] = win_count
        w_dict['all_count'] = all_count
        w_dict['timestamp'] = record['timestamp']
        # t_dict[week] = w_dict
        p_dict[week] = w_dict
        # p_dict[t_id] = t_dict
        res[p_name] = p_dict
    r = list()
    for k, v in res.items():
        temp = dict()
        temp['_t_id'] = str(t_id)
        temp['product'] = k
        d = [{
            "week": k, "all_count": v['all_count'],
            "win_count": v['win_count'], "timestamp": v['timestamp'],
            "win_per": 0 if v['all_count'] == 0 else round((v['win_count'] / v['all_count']) * 100, 1)
            } for k, v in v.items()]
        d.sort(key=lambda obj: obj['timestamp'], reverse=True)
        temp['data'] = d
        r.append(temp)
    r.sort(key=lambda obj: len(obj['data']), reverse=True)
    data = {"chart": r, "history": raw, "hold": hold}
    return data


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
    elif chart_type == "month":
        """以时间（月）切分，以老师为分组依据， 以产品分类"""
        res = calculate_win_per_by_month(begin=begin, end=end)
    elif chart_type == "week":
        """以时间（周）切分，以老师为分组依据， 以产品分类"""
        res = calculate_win_per_by_week(begin=begin, end=end)
    else:
        pass
    return res


def win_and_bar(t_id: (str, ObjectId)) -> dict:
    """
    查询老师的,状图表数据并计算胜率. 2018-9-17
    :param t_id:
    :return:
    db.trade.aggregate([
    {"$match":{"change": "raw", "enter_time":{$exists:true, $ne:null, "$gte":ISODate("2018-08-31T23:00:00.000Z")},"each_profit":{$exists: true}}},
    {
        "$project":
            {
                "teacher_id": "$teacher_id",
                "teacher_name": "$teacher_name",
                "enter_time": "$enter_time",
                "str":{$dateToString: {date:"$enter_time", format:"%G-%m-%d %H:%M:%S"}},
                "win":{$gte:["$each_profit", 0]}
            },
    },
    {$addFields:{"case":1, "w":{$cond:{if:{"$eq":["$win", true]},then:1,else:0}}}},
    {"$sort":{"enter_time":1}},
    {"$match": {"w": 0}}
    ])
    """


if __name__ == "__main__":
    # calculate_win_per_by_product()
    # calculate_win_per_by_teacher()
    # calculate_win_per_by_teacher_mix()
    calculate_win_per_by_week_single(ObjectId("5a1e680642f8c1bffc5dbd69"))
    pass

