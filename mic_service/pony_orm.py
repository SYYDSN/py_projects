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
from  pony.orm import *
from decimal import Decimal
import json
import warnings


"""
数据库连接模块
"""

version = "0.0.1"

print("PonyORM模块当前版本号: {}".format(version))


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
    :return: md5加密后的
    """
    if not isinstance(raw, str):
        ms = "原始密码必须是str类型，期待一个str，得到一个{}".format(type(raw))
        raise TypeError(ms)
    else:
        return hashlib.md5(raw.encode(encoding="utf-8")).hexdigest()


def update_dict(dict1: dict, dict2: dict) -> dict:
    """
    把两个字典合并成一个字典。并返回
    :param dict1: 参与合并的字典1
    :param dict2: 参与合并的字典2
    :return: 合并的结果
    """
    dict1.update(dict2)
    return dict1


def unique_str_in_box(box: list, a_str: str) -> bool:
    """
    检查一个字符串是否在box中唯一.
    如果唯一,就把字符串加入box,返回True,否则直接返回False
    :param box:
    :param a_str:
    :return: 唯一返回True,否则返回False
    """
    if a_str not in box:
        box.append(a_str)
        return True
    else:
        return False


def join_composite_keys(doc: dict, keys: list, separator: str = "") -> str:
    """
    把一个字典类型的文档的复合键取出来.
    :param doc: 待提取复合键的文档
    :param keys: 复合键名的序列,这个应该是去重后的序列
    :param separator: 分割符,默认为空字符
    :return: 组合后的复合键的字符串
    """
    a_list = [(k, str(v)) for k, v in doc.items() if k in keys]
    a_list.sort(key=lambda obj: obj[0])
    return separator.join([x[-1] for x in a_list])


def check_composite_keys(raw_doc, keys: (list, tuple, set) = None) -> list:
    """
    检查一组拥有复合键的字典类型的文档,去掉从重复的文档
    :param raw_doc: 可能存在重复情况的拥有复合键的字典对象
    :param keys:  复合键的序列,
    :return:
    """
    result = list()
    if len(raw_doc) > 1:
        keys = keys if isinstance(keys, set) else set(keys)
        keys = list(keys)
        temp_list = list()
        result = [x for x in raw_doc if unique_str_in_box(box=temp_list, a_str=join_composite_keys(doc=x, keys=keys))]
    else:
        result = raw_doc
    return result


logger = logging.getLogger("PonyORM")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
host = "rm-bp11oah59lpcl62l42o.mysql.rds.aliyuncs.com"
user = "yilu2018"
password = "KsYl888Parasite"
setting = {
    "provider": "mysql",
    "host": host,
    "port": 3306,
    "database": "walle_test",
    "user": user,
    "password": password
}

db = Database()
db.bind(**setting)


class EntityExtends(db.Entity):
    """
    db.Entity的方法扩展.
    1. 使用多继承来扩展实体类的方法.
    2. 使用@property装饰器来扩展属性和限制对属性值的值(混合方法/属性)
    """

    @classmethod
    @db_session
    def add_instance(cls, **kwargs) -> dict:
        """
        添加一个对象
        :param kwargs:
        :return:
        """
        mes = {"message": "success"}
        obj = None
        try:
            obj = cls(**kwargs)
        except ValueError as e:
            logger.exception(e)
            print(e)
            mes['message'] = "参数的值错误"
        except TypeError as e:
            logger.exception(e)
            print(e)
            mes['message'] = "参数的类型错误"
        except Exception as e:
            logger.exception(e)
            print(e)
            mes['message'] = "未知错误: {}".format(e)
        finally:
            if isinstance(obj, cls):
                obj.flush()
                obj_id = obj.id
                mes['id'] = obj_id
            else:
                pass
            return mes


class Demo2(db.Entity):
    table_ = "demo2"  # 定义表名


class Demo(db.Entity):
    """
    一个类构建的示例
    """
    _table_ = "demo"  # 定义表名

    id = PrimaryKey(int, auto=True, size=16, unsigned=True)  # 主键,  16位,自增
    rand = Required(py_type=int, size=16, unsigned=True)  # 16位无符号整数
    name = Required(py_type=str, max_len=40, unique=True)
    price = Required(py_type=Decimal, precision=10, scale=2)  # 10进制,保留2位小数
    gender = Required(py_type=str, autostrip=True)  # 自动剔除空格,
    # composite_index(name, "b")   # 复合索引
    job = Required(str, column="job", default="worker")  # 指定列名
    age = Required(int, default=20, min=16, max=40)  # 默认值, 最小值,最大值
    desc = Required(str, lazy=True)  # lazy是懒加载
    brother = Optional(str, nullable=True)
    brother2 = Optional(str, nullable=False)
    city = Required("Demo1", column="city2")  # 外键 参数是类名
    # child = Set("Child", reverse="parent")   # 一对多, 双方都设置的话就是多对多
    money = Required(float, py_check=lambda val: val > 5000)  # 值检查函数
    create = Required(py_type=datetime.datetime, precision=6)  # mysql特殊参数,设置为6可以保存小数秒

    def before_delete(self):
        """
        触发器. 共计6个
        after_delete
        after_insert
        after_update
        before_delete
        before_insert
        before_update
        :return:
        """
        pass


class Demo1(db.Entity):
    table_ = "demo1"  # 定义表名
    name = Required(str, default="张三")
    demo = Set("Demo")    # 配合city = Required(Demo1)设置外键


class Person(db.Entity):
    name = Required(str)
    age = Required(int)

    @classmethod
    @db_session
    def add(cls, name: str, age: int) -> dict:
        """
        添加
        :param name:
        :param age:
        :return:
        """
        mes = {"message": "success"}
        p = cls(name=name, age=age)
        p.flush()
        return mes


db.generate_mapping(create_tables=True)


if __name__ == "__main__":
    # init = {
    #
    # }
    # with db_session:
    #     demo = Demo1.get(id=1)
    #     demo.name = "李四2"
    #     demo = Demo1()
    #     print(flush())
    # Person.add_instance(name="dfdf", age=datetime.datetime.now())
    pass
