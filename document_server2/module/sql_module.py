#  -*- coding: utf-8 -*-
import os
import sys

__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import datetime
import re
import hashlib
import calendar
import logging
from uuid import uuid4
from peewee import *
import json
import warnings
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import model_to_dict

"""
数据库连接模块
"""

version = "0.0.2"

print("Peewee ORM模块当前版本号: {}".format(version))


def expand_list(set_list: (list, tuple)) -> list:
    """
    展开嵌套的数组或者元组
    :param set_list: 嵌套的元组或者数组
    :return: 数组
    调用方式 result = expand_list([1,2,[3,4],[5,6,7]])
    """
    res = list()
    for arg in set_list:
        if isinstance(arg, (list, tuple)):
            res.extend(expand_list(arg))
        else:
            res.append(arg)
    return res


def other_can_json(obj):
    """
    把其他对象转换成可json,是to_flat_dict的内部函数
    v = v.strftime("%F %H:%M:%S.%f")是v = v.strftime("%Y-%m-%d %H:%M:%S")的
    简化写法，其中%f是指毫秒， %F等价于%Y-%m-%d.
    注意，这个%F只可以用在strftime方法中，而不能用在strptime方法中
    """
    if isinstance(obj, datetime.datetime):
        if obj.hour == 0 and obj.minute == 0 and obj.second == 0 and obj.microsecond == 0:
            return obj.strftime("%F")
        else:
            return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, datetime.date):
        return obj.strftime("%F")
    elif isinstance(obj, list):
        return [other_can_json(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: other_can_json(v) for k, v in obj.items()}
    else:
        return obj


def to_flat_dict(a_dict, ignore_columns: list = list()) -> dict:
    """
    转换成可以json的字典,这是一个独立的方法
    :param a_dict: 待处理的doc.
    :param ignore_columns: 不需要返回的列
    :return:
    """
    return {other_can_json(k): other_can_json(v) for k, v in a_dict.items() if k not in ignore_columns}


def last_day_of_month(the_date: datetime.datetime) -> int:
    """
    求这个月的最后一天
    :param the_date:
    :return:
    """
    y = the_date.year
    m = the_date.month
    return calendar.monthrange(y, m)[-1]


def prev_month(the_date: datetime.datetime = None) -> tuple:
    """
    给定一个时间,返回上个月的年和月的信息
    :param the_date:
    :return:
    """
    if not isinstance(the_date, datetime.datetime):
        ms = "the_date类型错误,使用当前日期替代,错误原因:期待一个datetime.datetime对象,获得了一个{}对象".format(type(the_date))
        warnings.warn(ms)
        the_date = datetime.datetime.now()
    y = the_date.year
    m = the_date.month
    the_date = datetime.datetime.strptime("{}-{}-1".format(y, m), "%Y-%m-%d") - datetime.timedelta(days=1)
    res = (the_date.year, the_date.month)
    return res


def get_datetime_from_str(date_str: str) -> datetime.datetime:
    """
    根据字符串返回datetime对象
    :param date_str: 表示时间的字符串."%Y-%m-%d %H:%M:%S  "%Y-%m-%d %H:%M:%S.%f 或者 "%Y-%m-%d
    :return: datetime.datetime对象
    """
    if date_str is None:
        pass
    elif isinstance(date_str, (datetime.datetime, datetime.date)):
        return date_str
    elif isinstance(date_str, str):
        date_str.strip()
        search = re.search(r'\d{4}.\d{1,2}.*\d', date_str)
        if search:
            date_str = search.group()
            pattern_0 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d$')  # 时间匹配2017-01-01
            pattern_1 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d$')  # 时间匹配2017-01-01 12:00
            pattern_2 = re.compile(
                r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d$')  # 时间匹配2017-01-01 12:00:00
            pattern_3 = re.compile(
                r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d\.\d+$')  # 时间匹配2017-01-01 12:00:00.000
            pattern_4 = re.compile(
                r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d\s\d+$')  # 时间匹配2017-01-01 12:00:00 000
            pattern_5 = re.compile(
                r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d$')  # 时间匹配2017-01-01T12:00:00
            pattern_6 = re.compile(
                r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\.\d+$')  # 时间匹配2017-01-01T12:00:00.000
            pattern_7 = re.compile(
                r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\.\d{1,3}Z$')  # 时间匹配2017-01-01T12:00:00.000Z
            pattern_8 = re.compile(
                r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\s\d+$')  # 时间匹配2017-01-01T12:00:00 000

            if pattern_8.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S %f")
            elif pattern_7.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            elif pattern_6.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            elif pattern_5.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            elif pattern_4.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %f")
            elif pattern_3.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
            elif pattern_2.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            elif pattern_1.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            elif pattern_0.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d")
            else:
                ms = "get_datetime_from_str() 参数 {} 时间字符串格式不符合要求 2017-01-01或者2917-01-01 12:00:00".format(date_str)
                print(ms)
                logger.info(ms, exc_info=True, stack_info=True)
        else:
            ms = "get_datetime_from_str() 参数 {} 时间字符串格式匹配失败".format(date_str)
            print(ms)
            logger.info(ms, exc_info=True, stack_info=True)
    else:
        ms = "get_datetime_from_str() 参数 {} 格式错误，期待str，得到一个 {}".format(date_str, type(date_str))
        print(ms)
        logger.info(ms, exc_info=True, stack_info=True)


def generator_password(raw: str) -> str:
    """
    生成密码，使用md5加密
    :param raw: 原始密码
    :return: md5加密后的秘密啊
    """
    if not isinstance(raw, str):
        ms = "原始密码必须是str类型，期待一个str，得到一个{}".format(type(raw))
        raise TypeError(ms)
    else:
        return hashlib.md5(raw.encode(encoding="utf-8")).hexdigest()


def merge_dict(dict1: dict, dict2: dict) -> dict:
    """
    把两个字典合并成一个字典。和update方法不同,键相同的值不进行替换而是进行合并, 目的是保留尽可能多的信息
    一些合并时候的规则如下
    1. 有数据>''>None
    2. 数据长度大保留
    3. 数组格式合并去重
    4. 字典格式递归
    :param dict1: 参与合并的字典1
    :param dict2: 参与合并的字典2
    :return: 合并的结果
    """
    keys = list(dict1.keys())
    keys.extend(list(dict2.keys()))
    res = dict()
    for key in keys:
        v1 = dict1.get(key)
        v2 = dict2.get(key)
        if v1 is None:
            res[key] = v2
        elif v2 is None:
            res[key] = v1
        else:
            if isinstance(v1, list) and isinstance(v2, list):
                v1.extend(v2)
                res[key] = v1
            elif isinstance(v1, dict) and isinstance(v2, dict):
                res[key] = merge_dict(v1, v2)
            elif isinstance(v1, str) and isinstance(v2, str):
                res[key] = v1 if len(v1) > len(v2) else v2
            else:
                res[key] = v1
    return res


class JSONField(Field):
    """
    自定义的JSON类型
    """
    field_type = 'json'

    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        return json.loads(value)


logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
host = "rm-bp11oah59lpcl62l42o.mysql.rds.aliyuncs.com"
user = "yilu2018"
password = "KsYl888Parasite"
host = "127.0.0.1"
if host == "127.0.0.1":
    user = "root"
    password = "123456"
setting = {
    "host": host,
    "port": 3306,
    "max_connections": 100,
    "stale_timeout": 300,
    "database": "doc_server_db",
    "user": user,
    "password": password
}

db = PooledMySQLDatabase(**setting)


class BaseModel(Model):
    """
    自定义ORM模型基类.
    建议:
    1. 定义外键的时候,最好定义为xxx_id的形式,否则peewee会自动加_id后缀,引起列名不一致的情况.
    2. 没有查询到结果时会抛出 class.DoseNotExist(Person.DoseNotExist)异常
    3. 有关返回值,如果你查询一条记录,直接调用get_dict即可,如果查询多条记录,那就是[x.get_dict() for x in result]
    4. 如果你要自定义一个非自增长的int主键或者uuid主键,请不要使用PrimaryKeyField,而是id = IntegerField(primary_key=True)

    """

    """
    这里定义字段,例如: 
    id = PrimaryKeyField(int)
    name = CharField(unique=True)
    """

    class Meta:
        database = db  # 可被继承
        table_name = "base_model"  # 定义表名,不定义的话直接是类名转成小写. 不可被继承

    def get_dict(self, recurse: bool = False, backrefs: bool = False,projection: list = None, exclude: list = None,
                 max_depth: int = None, mm: bool = False, flat: bool = False) -> dict:
        """
        :param recurse:  是否递归外键
        :param backrefs:  是否递归相关对象的列表
        :param projection:  投影
        :param exclude:  排除的字段
        :param max_depth:  最大递归深度. 0表示不限制
        :param mm:  many to many 是否处理多对多
        :param flat:  是否进行json序列化检查
        :return:
        """
        data = model_to_dict(model=self, recurse=recurse, backrefs=backrefs, only=projection, exclude=exclude,
                             max_depth=max_depth, manytomany=mm)
        if flat:
            data = to_flat_dict(data)
        return data

    @classmethod
    def all_fields(cls) -> list:
        """
        返回所有定义的field
        :return:
        """
        return cls._meta.sorted_fields

    @classmethod
    def all_field_names(cls) -> list:
        """
        返回所有定义的field_name
        :return:
        """
        return cls._meta.sorted_field_names


# models = [BaseModel]
# db.create_tables(models=models)

if __name__ == "__main__":
    pass