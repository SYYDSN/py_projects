#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module


ObjectId = orm_module.ObjectId
cache = orm_module.RedisCache()
cache_key = "real_time"


"""金10数据的持久化部分"""


def save_data(data):
    """
    :param data:
    :return:
    """
    cache.set(key=cache_key, value=data, timeout=300)


def load_data(to_str: bool = True) -> str:
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
    :param to_str:
    :return:
    """
    data = cache.get(key=cache_key)
    resp = "^^"
    if data is None:
        pass
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
    j.save()
    pass