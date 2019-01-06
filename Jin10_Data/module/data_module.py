#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
import json
import datetime


ObjectId = orm_module.ObjectId
cache = orm_module.RedisCache()
cache_key = "real_time"


"""金10数据的持久化部分"""


class JinTenData(orm_module.BaseDoc):
    """
    jin10新闻的数据类
    """
    _table_name = "jin10_data"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['data'] = dict   # 数据
    type_dict['last_update'] = datetime.datetime  # 最近一条新闻的时间,用作判断更新.
    type_dict['time'] = datetime.datetime  # 写入时间

    @classmethod
    def record(cls, data: dict, last_update: datetime.datetime, clear_prev: int = 1) -> None:
        """
        比对last_update决定是否更新时间?如果last_update一致,就只更新最后一条记录的time,
        否则新插入一条记录.
        :param data:
        :param last_update:
        :param clear_prev: 清除几个小时之前的记录?(因为单条记录可能很大,所以需要清除一下)
        :return:
        """
        s = [("time", -1)]
        r = cls.find_one(sort=s)
        now = datetime.datetime.now()
        if isinstance(r, dict) and last_update == r['last_update']:
            u = {"$set": {"time": now}}
            cls.find_one_and_update(filter_dict={"_id": r['_id']}, update_dict=u)
        else:
            prev = now - datetime.timedelta(hours=clear_prev)
            cls.delete_many(filter_dict={"time": {"$lt": prev}})
            doc = {"data": data, "time": now, "last_update": last_update}
            cls.insert_one(doc=doc)


def save_data(data, last_date):
    """
    :param data:
    :param last_date: 最新一条新闻的日期,用于判断是否需要更新
    :return:
    """
    current_date = "{} {}".format(last_date, ("0:0:0" if len(data['news']) == 0 else data['news'][0]['time']))
    current_date = datetime.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S")
    JinTenData.record(data=data, last_update=current_date)
    cache.set(key=cache_key, value=data, timeout=300)


def load_data(to_json: bool = True) -> str:
    """
    数据格式:
    接口地址: http://news.91master.cn:7999/info
    方法: GET/POST
    字符集: UTF-8
    返回类型: 字符串
    返回类型的说明:
    返回的字符串中依次包含三种类型数据:
    1. 策略
    2. 数据日历
    3. 新闻
    三类数据以"^"分割(目前策略类型数据为空)
    三类数据都包含多条信息,每条信息之间用"*"分割.
    每条信息包含多个字段信息.字段之间的信息使用"|"分割.每条信息内部的字段分割如下:
    策略: 空缺
    新闻:  时间|新闻内容
    数据日历:   时间|标题|重要性|前值|预测值|公布值|影响
    :param to_json:
    :return:
    """
    data = cache.get(key=cache_key)
    resp = "^^"
    if data is None:
        pass
    else:
        if to_json:
            resp = json.dumps(data)
        else:
            strategy = data.get("strategy", [])  # 策略
            news = data.get("news", [])          # 新闻
            calendar = data.get("calendar", [])  # 数据日历
            strategy_str = "*".join(strategy)
            news = ["|".join([x['time'], x['text']]) for x in news]
            news_str = "*".join(news)
            cs = ["|".join([
                x['time'], x['title'], str(x['star']), x['prev'], x['forecast'], x['publish'], x['effect']
            ]) for x in calendar]
            cs_str = "*".join(cs)
            resp = "{}^{}^{}".format(strategy_str, cs_str, news_str)
    return resp


if __name__ == "__main__":
    pass