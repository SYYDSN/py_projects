# -*- coding:utf-8 -*-
# from gevent import monkey
# monkey.patch_all()
import pymongo
from pymongo import monitoring
import warnings
import datetime
import calendar
import hashlib
import functools
from flask import request
from uuid import uuid4
from bson.objectid import ObjectId
from bson.dbref import DBRef
from bson.code import Code
from bson.errors import InvalidId
from bson.son import SON
from bson.binary import Binary
import numpy as np
import re
import math
from mail_module import send_mail
from pymongo.client_session import ClientSession
from werkzeug.contrib.cache import RedisCache
from werkzeug.contrib.cache import SimpleCache
from pymongo import WriteConcern
from pymongo.collection import Collection
from log_module import get_logger
from pymongo import ReturnDocument
from pymongo.results import *
import gridfs
from flask import Flask
from werkzeug.routing import Map
from werkzeug.routing import Rule
from pymongo.errors import *


"""
MongoDB4+ 的持久化类   2018-10-11
"""

version = "0.0.3"

print("ORM模块当前版本号: {}".format(version))


cache = RedisCache()         # 使用redis的缓存.数据的保存时间由设置决定
s_cache = SimpleCache()      # 使用内存的缓存,重启/关机就清空了.
logger = get_logger()
# user = "test_root"              # 数据库用户名
# password = "Test@1314"       # 数据库密码
# db_name = "test_db"        # 库名称
# mechanism = "SCRAM-SHA-1"      # 加密方式，注意，不同版本的数据库加密方式不同。
#
# """mongodb配置信息"""
# """
# 注意,使用连接池就不能使用mongos load balancer
# mongos load balancer的典型连接方式: client = MongoClient('mongodb://host1,host2,host3/?localThresholdMS=30')
# """
# mongodb_setting = {
#     "host": "47.99.105.196:27017",   # 数据库服务器地址
#     "localThresholdMS": 30,  # 本地超时的阈值,默认是15ms,服务器超过此时间没有返回响应将会被排除在可用服务器范围之外
#     "maxPoolSize": 100,  # 最大连接池,默认100,不能设置为0,连接池用尽后,新的请求将被阻塞处于等待状态.
#     "minPoolSize": 0,  # 最小连接池,默认是0.
#     "waitQueueTimeoutMS": 30000,  # 连接池用尽后,等待空闲数据库连接的超时时间,单位毫秒. 不能太小.
#     "authSource": db_name,  # 验证数据库
#     'authMechanism': mechanism,  # 加密
#     "readPreference": "primaryPreferred",  # 读偏好,优先从盘,如果是从盘优先, 那就是读写分离模式
#     # "readPreference": "secondaryPreferred",  # 读偏好,优先从盘,读写分离
#     "username": user,       # 用户名
#     "password": password    # 密码
# }
db_name = "query_db"
mongodb_setting = {
    "host": "127.0.0.1:27017",   # 数据库服务器地址
    "localThresholdMS": 30,  # 本地超时的阈值,默认是15ms,服务器超过此时间没有返回响应将会被排除在可用服务器范围之外
    "maxPoolSize": 100,  # 最大连接池,默认100,不能设置为0,连接池用尽后,新的请求将被阻塞处于等待状态.
    "minPoolSize": 2,  # 最小连接池,默认是0.
    "waitQueueTimeoutMS": 30000,  # 连接池用尽后,等待空闲数据库连接的超时时间,单位毫秒. 不能太小.
    "authSource": db_name,  # 验证数据库
}


class DBCommandListener(monitoring.CommandListener):
    """
    监听数据库执行的命令,注意所有监听器都是同步执行的!!!
    1.没必要不要使用,因为多少对性能有影响.
    2.必须要使用的情况下,注意不要对性能造成影响.
    """
    def started(self, event):
        # command_name = event.command_name
        # command_dict = event.command
        # database_name = event.database_name
        # ms = "{} 数据库的 {} 命令开始,参数:{}".format(database_name, command_name, command_dict)
        # print(ms)
        # logger.info(ms)
        pass

    def succeeded(self, event):
        pass

    def failed(self, event):
        # command_name = event.command_name
        # command_dict = event.command
        # database_name = event.database_name
        # ms = "Error: {} 数据库的 {} 命令执行失败,参数:{}".format(database_name, command_name, command_dict)
        # print(ms)
        # logger.exception(ms)
        failure = event.failure
        error_msg = failure.get("errmsg")
        if error_msg is None:
            pass
        elif error_msg == "Authentication failed.":
            """登录失败"""
            title = "{}数据库登录失败! {}".format(db_name, datetime.datetime.now())
            send_mail(title=title)
        else:
            pass
        pass


class DBServerListener(monitoring.ServerListener):
    """
    数据库服务器状态改变监听器
    注意所有监听器都是同步执行的!!!
    1.没必要不要使用,因为多少对性能有影响.
    2.必须要使用的情况下,注意不要对性能造成影响.
    """
    def opened(self, event):
        # ms = "Warning: server {} is opened!".format(":".join([str(x) for x in event.server_address]))
        # logger.info(ms)
        # print(ms)
        pass

    def description_changed(self, event):
        previous_server_type = event.previous_description.server_type
        new_server_type = event.new_description.server_type
        # if new_server_type != previous_server_type:
        #     ms = "Warning: server description changed: from {} to {}".format(previous_server_type, new_server_type)
        #     logger.info(ms)
        # else:
        #     pass

    def closed(self, event):
        ms = "Warning: Server {0.server_address} removed from topology {0.topology_id}".format(event)
        logger.info(ms)


class DBHeartBeatListener(monitoring.ServerHeartbeatListener):
    """
    数据库心跳监听器.
    注意所有监听器都是同步执行的!!!
    1.没必要不要使用,因为多少对性能有影响.
    2.必须要使用的情况下,注意不要对性能造成影响.
    """
    def started(self, event):
        # ms = "Heartbeat sent to server {0.connection_id}".format(event)
        # logger.info(ms)
        pass

    def succeeded(self, event):
        # ms = "Heartbeat to server {0.connection_id} succeeded with reply {0.reply.document}".format(event)
        # logger.info(ms)
        pass

    def failed(self, event):
        ms = "Warning: Heartbeat to server {0.connection_id} failed with error {0.reply}".format(event)
        logger.info(ms)


class DBTopologyListener(monitoring.TopologyListener):
    """
    数据库拓扑变化监听器.
    注意所有监听器都是同步执行的!!!
    1.没必要不要使用,因为多少对性能有影响.
    2.必须要使用的情况下,注意不要对性能造成影响.
    """
    def opened(self, event):
        # ms = "Topology with id {0.topology_id} opened".format(event)
        # logger.info(ms)
        pass

    def description_changed(self, event):
        # ms = "Topology description updated for topology id {0.topology_id}".format(event)
        # logger.info(ms)
        previous_topology_type = event.previous_description.topology_type
        new_topology_type = event.new_description.topology_type
        # if new_topology_type != previous_topology_type:
        #     ms = "Topology {0.topology_id} changed type from {0.previous_description.topology_type_name} " \
        #          "to {0.new_description.topology_type_name}".format(event)
        #     logger.info(ms)
        #
        # if not event.new_description.has_writable_serv/er():
        #     ms = "Warning: No writable servers available."
        #     logger.warning(ms)
        #
        # if not event.new_description.has_readable_server():
        #     ms = "Warning: No readable servers available."
        #     logger.warning(ms)

    def closed(self, event):
        # ms = "Warning: Topology with id {0.topology_id} closed".format(event)
        # logger.info(ms)
        pass


"""注册全局监听器"""
monitoring.register(DBCommandListener())
monitoring.register(DBServerListener())
monitoring.register(DBHeartBeatListener())
monitoring.register(DBTopologyListener())


class DB:
    """自定义单例模式客户端连接池"""
    def __new__(cls):
        if not hasattr(cls, "instance"):
            conns = pymongo.MongoClient(**mongodb_setting)
            cls.instance = conns

        return cls.instance


def get_client() -> pymongo.MongoClient:
    """
    获取一个MongoClient(一般用于生成客户端session执行事物操作)
    :return:
    """
    mongo_client = DB()
    return mongo_client


def get_schema(database: str = None):
    """
    获取一个针对db_name对应的数据库的的连接，一般用于ORM方面。比如构建一个类。
    :param database: 数据库名
    :return: 一个Database对象。
    """
    db_client = get_client()
    if database is None:
        schema = db_client[db_name]
    else:
        schema = db_client[database]
    return schema


def get_write_concern(w: (str, int) = "majority", j: bool = True) -> WriteConcern:
    """
    获取一个写关注对象
    :param w:
    :param j:
    :return:
    """
    res = WriteConcern(w=w, j=j)
    return res


def get_conn(table_name: str, database: str = None, db_client: pymongo.MongoClient = None,
             write_concern: (WriteConcern, dict) = None) -> Collection:
    """
    获取一个针对table_name对应的表的的连接，一般用户直接对数据库进行增删查改等操作。
    如果你要进行事务操作,请传入db_client参数以保证事务种所有的操作都在一个pymongo.MongoClient的session之下.
    :param table_name: collection的名称，对应sql的表名。必须。
    :param database: 数据库名
    :param db_client: 数据库的pymongo的客户端 transaction专用选项,用于保持数据库会话的一致性
    :param write_concern: 写关注级别. example: write_concern = {"w": 1, j: True}
    写关注有 w和j 两个选项.
    w: 写关注级别选项.w mongodb的默认w的值是1.
    j: 写关注日志选项.w mongodb的j的选项没有默认值.由其他地方的设置决定. False是关闭日志,True是打开日志.

    w: 0 int,     不关注写
    w: 1  int,    关注写,确保写动作执行完毕就算写成功.也是默认值
    w: >1 int,    关注写,大于1的数值是值,在副本集中,写入了几个节点才算写成功?  比如设置为3,那就是至少副本集种有3个节点写入了此数据才算有效.
    w: majority   字符串.当字符集取这个值的时候,标识只有副本集的绝大多数机器都写入了才算写成功.
    w: (tag_name, ...) 集合类型,内部的元素都是mongodb实例的标签名,只有拥有这些标签名的所有结点都写入后才算写入成功.
    j: None      不设置, 是否开启日志由其他地方的设置决定.
    j: False      关闭日志,哪怕已经在其他地方的设置中开启了日志.这里也可以关闭.
    j: True      开启日志,哪怕已经在其他地方的设置中关闭了日志.这里也可以开启.

    return: pymongo.collection.Collection
    """
    if table_name is None or table_name == '':
        raise TypeError("表名不能为空")
    else:
        cur_db_name = database if database else db_name
        if db_client is None:
            cur_db = get_schema(cur_db_name)
        else:
            cur_db = db_client[cur_db_name]
        conn = cur_db[table_name]
        if isinstance(write_concern, WriteConcern):
            conn = conn.with_options(write_concern=write_concern)
        elif isinstance(write_concern, dict):
            cur = dict()
            cur['w'] = write_concern.get("w")
            cur['j'] = write_concern.get("j")
            cur = {k: v for k, v in cur.items()}
            if len(cur) == 0:
                pass
            else:
                write_concern = WriteConcern(**cur)
                conn = conn.with_options(write_concern=write_concern)
        else:
            pass
        return conn


def collection_exists(database_name: str = None, table_name: str = None, auto_create: bool = False) -> bool:
    """
    根据表名检查一个表是否存在?
    :param database_name:
    :param table_name:
    :param auto_create: 如果表不存在,是否自动创建表?
    :return:
    """
    if isinstance(table_name, str) and table_name.strip() != '':
        table_name = table_name.strip()
        database_name = db_name if database_name is None else database_name
        database = get_client()
        schema = database[database_name]
        names = schema.list_collection_names()
        if table_name in names:
            return True
        else:
            if auto_create:
                col = Collection(database=schema, name=table_name, create=True)
                if isinstance(col, Collection):
                    return True
                else:
                    raise RuntimeError("创建Collection失败, table_name={}".format(table_name))
            else:
                return False
    else:
        raise ValueError("表名错误: {}".format(table_name))


def get_fs(table_name: str, database: str = None) -> gridfs.GridFS:
    """
    获取一个GridFS对象
    :param table_name: collection名
    :param database: 数据库名
    :return:
    """
    return gridfs.GridFS(database=get_schema(database), collection=table_name)


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
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, DBRef):
        return str(obj.id)
    elif isinstance(obj, datetime.datetime):
        if obj.hour == 0 and obj.minute == 0 and obj.second == 0 and obj.microsecond == 0:
            return obj.strftime("%F")
        else:
            return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, datetime.date):
        return obj.strftime("%F")
    elif isinstance(obj, list):
        return [other_can_json(x) for x in obj]
    elif isinstance(obj, dict):
        keys = list(obj.keys())
        if len(keys) == 2 and "coordinates" in keys and "type" in keys:
            """这是一个GeoJSON对象"""
            return obj['coordinates']  # 前经度后纬度
        else:
            return {k: other_can_json(v) for k, v in obj.items()}
    else:
        return obj


def other_can_save(obj):
    """
    把其他对象转换成可以保存进mongodb的类型
    v = v.strftime("%F %H:%M:%S.%f")是v = v.strftime("%Y-%m-%d %H:%M:%S")的
    简化写法，其中%f是指毫秒， %F等价于%Y-%m-%d.
    注意，这个%F只可以用在strftime方法中，而不能用在strptime方法中
    """
    if isinstance(obj, (int, float, str, bytes, bool, ObjectId, DBRef, datetime.datetime, datetime.date)):
        return obj
    elif obj is None:
        return obj
    elif isinstance(obj, (list, tuple, set)):
        return [other_can_save(x) for x in obj]
    elif isinstance(obj, dict):
        keys = list(obj.keys())
        if len(keys) == 2 and "coordinates" in keys and "type" in keys:
            """这是一个GeoJSON对象"""
            return obj['coordinates']  # 前经度后纬度
        else:
            return {k: other_can_save(v) for k, v in obj.items()}
    elif isinstance(obj, type) and hasattr(obj, '__init__'):
        """类构造器cls"""
        return obj.__name__ + ".cls"
    elif isinstance(obj, BaseDoc):
        """BaseFile子类的实例"""
        return obj.__class__.__name__ + ".instance"
    else:
        return str(obj)


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


def get_datetime(number=0, to_str=True) -> (str, datetime.datetime):
    """获取日期和时间，以字符串类型返回，格式为：2016-12-19 14:33:03
    number是指在当前日期上延后多少天，默认是0,可以是负值
    to_str 是指是否转换为字符串格式
    :return : str / datetime.datetime
    """
    now = datetime.datetime.now() + datetime.timedelta(days=number)
    if to_str:
        return now.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return now


def get_date_from_str(date_str: str) -> datetime.date:
    """
    根据字符串返回date对象
    :param date_str: 表示时间的字符串."%Y-%m-%d  "%Y/%m/%d或者 "%Y_%m_%d
    :return: datetime.date对象
    """
    the_date = None
    pattern = re.compile(r'^[1-2]\d{3}\D[0-1]?\d\D[0-3]?\d\D?$')
    if date_str is None:
        ms = "日期字符串不能为None"
        logger.exception(ms)
    elif pattern.match(date_str):
        print("date_str is {}".format(date_str))
        year = re.compile(r'^[1-2]\d{3}').match(date_str)
        month = re.compile(r'[0-1]?\d').match(date_str, pos=year.end() + 1)
        day = re.compile(r'[0-3]?\d').match(date_str, pos=month.end() + 1)
        the_str = "{}-{}-{}".format(year.group(), month.group(), day.group())
        the_date = datetime.datetime.strptime(the_str, "%Y-%m-%d").date()
    else:
        ms = "错误的日期格式:{}".format(date_str)
        logger.info(ms)
    return the_date


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
            pattern_2 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d$')  # 时间匹配2017-01-01 12:00:00
            pattern_3 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d\.\d+$') # 时间匹配2017-01-01 12:00:00.000
            pattern_4 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d\s\d+$') # 时间匹配2017-01-01 12:00:00 000
            pattern_5 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d$')  # 时间匹配2017-01-01T12:00:00
            pattern_6 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\.\d+$') # 时间匹配2017-01-01T12:00:00.000
            pattern_7 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\.\d{1,3}Z$')  # 时间匹配2017-01-01T12:00:00.000Z
            pattern_8 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\s\d+$')  # 时间匹配2017-01-01T12:00:00 000

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


def round_datetime(the_datetime: datetime.datetime) -> datetime.datetime:
    """
    对一个datetime进行取整,去掉小时分和毫秒,只保留年月日
    :param the_datetime: 待取整的对象
    :return: 取整后的对象
    """
    if isinstance(the_datetime, datetime.datetime):
        return datetime.datetime.strptime(the_datetime.strftime("%F"), "%Y-%m-%d")
    else:
        raise TypeError("期待一个datetime.datetime类型,的到一个{}类型".format(type(the_datetime)))


def reduce_list(resource_list: list, max_length: int = 100) -> (list, None):
    """
    削减数组(减少数组的长度),保留开始和结尾.
    :param resource_list: 原始数组
    :param max_length: 数组的最大长度
    :return: 削减后的数组
    """
    if isinstance(resource_list, list):
        try:
            max_length = max_length if isinstance(max_length, int) else int(max_length)
        except Exception:
            max_length = 100
        finally:
            l = len(resource_list)
            if l <= max_length:
                return resource_list
            else:
                step = math.ceil(l / max_length)
                res = [x for i, x in enumerate(resource_list) if i == 0 or i == (l - 1) or (i % step) == 0]
                return res
    else:
        ms = "resource_list不是一个数组, resource_list: {}".format(resource_list)
        logger.exception(ms)
        raise ValueError(ms)


def camel_to_pep8(name_str: str)->str:
    """
    把驼峰式命名的字符串转换为pep8格式命名的字符串
    :param name_str: 驼峰式命名的字符串
    :return: pep8格式命名的字符串
    """
    if isinstance(name_str, str) and len(name_str.strip()) > 1:
        name_str = name_str.strip()
        flag = True
        while flag:
            search_result = re.search("[A-Z]", name_str)
            # print(search_result)
            if search_result is None:
                return name_str
            else:
                old = search_result.group()
                new = "_{}".format(search_result.group().lower())
                name_str = name_str.replace(old, new, 1)
    else:
        return name_str


def get_collection_unique_index_info(ses: pymongo.collection.Collection) -> dict:
    """
    检查一个ｃｏｌｌｅｃｔｉｏｎ对象，获取所有唯一索引信息
    :param ses: 一个ｐｙｍｏｎｇｏ的连接对象
    :return: dict,索引名,索引列名的list组成的字典．
    """
    if not isinstance(ses, pymongo.collection.Collection):
        ms = "期待一个Collection对象，得到一个 {} 对象".format(type(ses))
        raise TypeError(ms)
    else:
        index_list = ses.list_indexes()
        result = dict()
        for x in index_list:
            unique = x.get('unique')  # 是否是唯一索引
            index_name = x['name']
            keys = x['key'].keys()  # 索引涉及的列的名称列表
            if unique or index_name == "_id_":
                if keys not in result.values():
                    result[index_name] = keys
                else:
                    pass
            else:
                pass
        return result


def generator_password(raw: str)->str:
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


def get_datetime_from_timestamp(timestamp_str: str)->datetime.datetime:
    """
    从一个时间戳字符串转换成datetime格式,如果失败,会调用通用的函数.
    :param timestamp_str: 时间戳字符串。
    :return: datetime.datetime.instance
    """
    try:
        timestamp_val = float(timestamp_str)
        if len(str(int(timestamp_str))) == 10:
            return datetime.datetime.fromtimestamp(timestamp_val)
        elif len(str(int(timestamp_str))) > 10:
            return datetime.datetime.fromtimestamp(timestamp_val / 1000)

        else:
            raise ValueError("{} 不能转换为合法的timestamp对象".format(timestamp_str))
    except ValueError as e:
        print(e)
        return get_datetime_from_str(timestamp_str)


def get_obj_id(object_id):
    """
    根据object_id获取一个ObjectId的对象。
    :param object_id: ObjectId / str
    :return: ObjectId的实例
    """
    if isinstance(object_id, (str, ObjectId)):
        if isinstance(object_id, ObjectId):
            return object_id
        else:
            try:
                obj_id = ObjectId(object_id)
                return obj_id
            except InvalidId as e:
                print(e)
                ms = "{}不能转换为ObjectId".format(object_id)
                logger.info(ms)
                raise ValueError(ms)
    else:
        ms = "object_id的类型错误，允许的是ObjectId和str,得到一个{}".format(type(object_id))
        logger.exception(ms)
        raise TypeError(ms)


class GeoJSON(dict):
    """GeoJSON对象，用于标示"""

    def __init__(self, type_name, values):
        """
        构造器
        :param type_name: GeoJSON对象的类型，实际上可包含的类型如下：
            Point 点 一对浮点的数组
            LineString 线 由2个 Point 组成的长度为2的数组的数组  2个点组成一条直线
            Polygon 多边形  由3个以上的Point组成的长度大于2的数组的数组。注意这些点是连通或者嵌套连通的
            MultiPoint  多个点 这些点 可以是散落的点，多个Point组成的数组。
            MultiLineString  多条线 多个LineString组成的数组。
            MultiPolygon  多个多边形 多个Polygon组成的数组。
            GeometryCollection 混合几何形状。 可以是由上面任意一种或者多种形状组合而已。注意
            混合集合形状的value的格式不再是简单的数组的数组了，而是由其他的6种形状的dict组成的数组，
            举例如下：
            {
              type: "GeometryCollection",
              geometries: [
                 {
                   type: "MultiPoint",
                   coordinates: [
                      [ -73.9580, 40.8003 ],
                      [ -73.9498, 40.7968 ],
                      [ -73.9737, 40.7648 ],
                      [ -73.9814, 40.7681 ]
                   ]
                 },
                 {
                   type: "MultiLineString",
                   coordinates: [
                      [ [ -73.96943, 40.78519 ], [ -73.96082, 40.78095 ] ],
                      [ [ -73.96415, 40.79229 ], [ -73.95544, 40.78854 ] ],
                      [ [ -73.97162, 40.78205 ], [ -73.96374, 40.77715 ] ],
                      [ [ -73.97880, 40.77247 ], [ -73.97036, 40.76811 ] ]
                   ]
                 }
              ]
            }
        :param values:根据type_name参数而有所不同，一般的名字是coordinates,如果
        type_name是GeometryCollection ,那么这里的名字是geometries。
        """

        temp_dict = {
            "Point": "coordinates", "LineString": "coordinates", "Polygon": "coordinates",
            "MultiPoint": "coordinates", "MultiLineString": "coordinates", "MultiPolygon": "coordinates",
            "GeometryCollection": "geometries"}
        keys = temp_dict.keys()
        if type_name in keys:
            if isinstance(values, (list, tuple)):
                args = {"type": type_name, temp_dict[type_name]: values}
                super(GeoJSON, self).__init__(**args)
            else:
                try:
                    raise ValueError("值错误！期待一个list，得到一个{},{} 不是一个合法的GeoJSON的{}的值".format(type(values),
                                                                                         str(values), type_name))
                except ValueError as e:
                    logger.error("Init Error:", exc_info=True, stack_info=True)
                    raise e
        else:
            try:
                raise ValueError("{} 不是一个合法的GeoJSON的类型".format(type_name))
            except ValueError as e:
                logger.error("Init Error:", exc_info=True, stack_info=True)
                raise e

    @classmethod
    def get_instance(cls, a_dict):
        """
        把字典转化为GeoJSON对象，
        :param a_dict: 字典
        :return: GeoJSON对象
        """
        if isinstance(a_dict, GeoJSON):
            return a_dict
        else:
            if isinstance(a_dict, dict):
                if "type" in a_dict and "coordinates" in a_dict:
                    obj = GeoJSON(a_dict['type'], a_dict['coordinates'])
                    return obj
                else:
                    type_name = a_dict.get("type_name")
                    values = a_dict.get("values")
                    obj = GeoJSON(type_name, values)
                    return obj
            else:
                try:
                    raise TypeError("a_dict是{}对象，不是期待的dict对象".format(type(a_dict)))
                except TypeError as e:
                    logger.error("TypeError:", exc_info=True, stack_info=True)
                    raise e


class MyCache:
    """缓存类,这是一个非持久化的类,需要redis的支持"""
    def __init__(self, cache_name: str):
        """
        初始化
        :param cache_name: cache的key名字的前缀,用于区分是缓存哪个表/类的对象/属性.用来组合key,一般常使用类的表名
        """
        global cache
        if isinstance(cache, RedisCache):
            pass
        else:
            cache = RedisCache()
        self.cache = RedisCache()
        self.cache_name = cache_name

    def set_value(self, key, value, timeout: int = 1800) -> bool:
        """
        设置一个值到缓存中
        :param key: 缓存key,一般是str类型
        :param value: 缓存值,可以是任何类型
        :param timeout: 老化时间,默认是半个小时
        :return:
        """
        r = False
        try:
            cache = self.cache
            key = "{}.{}".format(self.cache_name, key)
            cache.set(key, value, timeout=timeout)
            r = True
        except Exception as e:
            logger.exception()
            raise e
        finally:
            return r

    def get_value(self, key):
        """
        从缓存里取一个值出来
        :param key: 缓存key,一般是str类型
        :return: None/object
        """
        r = False
        try:
            cache = self.cache
            key = "{}.{}".format(self.cache_name, key)
            r = cache.get(key)
        except Exception as e:
            logger.exception()
            raise e
        finally:
            return r

    def delete_value(self, key):
        """
        从缓存里删除一个值出来
        :param key: 缓存key,一般是str类型
        :return: None
        """
        try:
            cache = self.cache
            key = "{}.{}".format(self.cache_name, key)
            cache.delete(key)
        except Exception as e:
            logger.exception()
            raise e
        finally:
            return


class BaseFile:
    """
    保存文件到mongodb数据库的GridFS操作基础类,
    这一类函数都不推荐使用init创建实例.而是使用
    cls.save_cls以及其延伸的方法cls.save_flask_file来保存文件.
    """
    _table_name = "base_file"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['owner'] = ObjectId   # 拥有者id,一般是指向user_info的_id
    type_dict['file_name'] = str
    type_dict['file_type'] = str  # 文件类型
    type_dict['description'] = str
    type_dict['uploadDate'] = datetime.datetime
    type_dict['length'] = int
    type_dict['chunkSize'] = int
    type_dict['md5'] = str
    type_dict['data'] = bytes

    def __init__(self, **kwargs):
        _id = kwargs.pop("_id", None)
        if _id is None:
            pass
        elif isinstance(_id, ObjectId):
            kwargs['_id'] = _id
        elif isinstance(_id, str) and len(_id) == 24:
            kwargs['_id'] = ObjectId(_id)
        else:
            ms = "_id参数不合法:{}".format(_id)
            raise ValueError(ms)
        owner = kwargs.get("owner", None)
        if not isinstance(owner, ObjectId):
            ms = "owner只能是ObjectId类型,期待ObjectId得到:{}".format(type(owner))
            raise ValueError(ms)
        else:
            pass
        if "file_name" not in kwargs:
            ms = "file_name arg is require!"
            raise ValueError(ms)
        if "file_type" not in kwargs:
            ms = "file_type参数缺失.未知的文件类型"
            raise ValueError(ms)
        if "description" not in kwargs:
            kwargs['description'] = ""
        for k, v in kwargs.items():
            type_dict = self.type_dict
            if k in type_dict:
                if isinstance(v, type_dict[k]):
                    self.__dict__[k] = v
                else:
                    the_type = self.type_dict[k]
                    if the_type.__name__ == 'datetime':
                        self.__dict__[k] = get_datetime_from_str(v)
                    else:
                        self.__dict__[k] = the_type(v)
            else:
                self.__dict__[k] = v

    def table_name(self):
        return self._table_name

    def get_dbref(self):
        """获取一个实例的DBRef对象"""
        obj = DBRef(self._table_name, self._id, db_name)
        return obj

    @classmethod
    def get_table_name(cls):
        return cls._table_name

    @classmethod
    def fs_cls(cls, collection: str = None) -> gridfs.GridFS:
        """
        返回一个GridFS对象.
        :param collection:
        :return:
        """
        collection = collection if collection else cls.get_table_name()
        return get_fs(collection)

    @classmethod
    def save_cls(cls, file_obj, collection: str = None, **kwargs) -> (str, ObjectId, None):
        """
        保存文件.类中最底层的保存文件的方法.
        :param file_obj: 一个有read方法的对象,比如一个就绪状态的BufferedReader对象.
        :param collection:
        :param kwargs:  metadata参数,会和文件一起保存,也可以利用这些参数进行查询.
        :return: 失败返回None,成功返回_id/str
        """
        fs = cls.fs_cls(collection)
        r = fs.put(data=file_obj, **kwargs)
        try:
            file_obj.close()
        except Exception as e:
            print(e)
        finally:
            return r

    @classmethod
    def save_flask_file(cls, req: request, collection: str = None, arg_name: str = None, **kwargs) -> (str, ObjectId, None):
        """
        保存文件. cls.save_cls的包装方法,专门针对flask.request进行了封装.
        :param req: 一个有flask.request对象.
        :param collection:
        :param arg_name: 保存在flask.request.files里面的文件的参数名,如果不指明这个参数名,将只会取出其中的第一个对象进行保存.
        :param kwargs:  metadata参数,会和文件一起保存,也可以利用这些参数进行查询.
        :return: 失败返回None,成功返回_id/str
        """
        res = None
        if arg_name is None:
            for key_name, file_storage in req.files.items():
                if file_storage is not None:
                    file_name = file_storage.filename
                    file_suffix = file_name.split(".")[-1]
                    content_type = file_storage.content_type
                    mime_type = file_storage.mimetype
                    kwargs['file_name'] = file_name
                    kwargs['file_suffix'] = file_suffix
                    kwargs['content_type'] = content_type
                    kwargs['mime_type'] = mime_type
                    res = cls.save_cls(file_obj=file_storage, collection=collection, arg_name=key_name, **kwargs)
                    if res is None:
                        pass
                    else:
                        break
        else:
            file_storage = req.files.items.get(arg_name, None)
            if file_storage is None:
                pass
            else:
                file_name = file_storage.filename
                file_suffix = file_name.split(".")[-1]
                content_type = file_storage.content_type
                mime_type = file_storage.mimetype
                kwargs['file_name'] = file_name
                kwargs['file_suffix'] = file_suffix
                kwargs['content_type'] = content_type
                kwargs['mime_type'] = mime_type
                res = cls.save_cls(file_obj=file_storage, collection=collection, arg_name=arg_name, **kwargs)
        return res

    @staticmethod
    def get_dict_from_fs(return_obj: gridfs.GridFS) -> dict:
        """
        从一个gridfs.GridFS对象中取回完整的字典。
        :param return_obj:
        :return:
        """
        r = return_obj._file
        r['data'] = return_obj.read()
        return r

    @classmethod
    def find_one_cls(cls, filter_dict: dict, sort_dict: dict = None, instance: bool = False, collection: str = None)\
            -> (dict, None):
        """
        查找一个文件.cls.get_one_data的底层方法,
        :param filter_dict: 查找条件
        :param sort_dict: 排序条件
        :param instance: 是否返回实例?
        :param collection:
        :return: object/doc
        """
        fs = cls.fs_cls(collection)
        if isinstance(sort_dict, dict) and len(sort_dict) > 0:
            s = [(k, v) for k, v in sort_dict.items()]
            one = fs.find_one(filter=filter_dict, sort=s)
        else:
            one = fs.find_one(filter=filter_dict)
        if one is None:
            pass
        else:
            r = cls.get_dict_from_fs(one)
            one.close()
            return cls(**r) if instance else r

    def data(self) -> bytes:
        """返回数据"""
        return self.__dict__['data']

    @classmethod
    def get_one_data(cls, filter_dict: dict, sort_dict: dict = None, collection: str = None) -> bytes:
        """
        根据条件,查询一个文件,cls.find_one_cls的包装函数,和cls.find_one_cls不同,前者返回的是文档或者实例.本
        函数只返回文件的内容(bytes).
        :param filter_dict: 查找条件
        :param sort_dict: 排序条件
        :param collection: 排序条件
        :return:
        """
        r = cls.find_one_cls(filter_dict=filter_dict, sort_dict=sort_dict, collection=collection)
        if r is None:
            pass
        else:
            return r['data']

    @classmethod
    def format_url(cls, file_id: (str, ObjectId), file_name: str, collection: str = None) -> str:
        """
        格式化file对象的url, 这个函数仅仅被cls.transform调用.
        对于不同的class,你可能需要重载此方法以自定义file的url
        :param file_id:
        :param file_name:
        :param collection:
        :return:
        """
        file_id = file_id if isinstance(file_id, str) else str(file_id)
        collection = collection if collection else cls.get_table_name()
        return '/manage/fs/{}/{}/{}'.format(collection, file_id, file_name)

    @classmethod
    def transform(cls, doc: dict, include_data: bool = False, collection: str = None) -> dict:
        """
        转换字典成为:
        1. files部分的BDRef转为url
        2. 除data外,都转为适合json的类型.
        :param doc:
        :param include_data: 是否包含data?
        :param collection:
        :return:
        """
        f_data = doc.pop("data", None)
        temp = to_flat_dict(doc)
        if include_data and f_data is not None:
            temp['data'] = f_data
        f_url = cls.format_url(file_id=temp['_id'], file_name=temp['file_name'], collection=collection)
        temp['url'] = f_url
        return temp

    @classmethod
    def query_by_page(cls, filter_dict: dict, sort_dict: dict = None, projection: list = None, page_size: int = 10,
                      ruler: int = 5, page_index: int = 1, func: object = None) -> dict:
        """
        分页查询,注意这个方法和BaseDoc.query_by_page方法不同，本方法没有to_dict和can_json参数，
        但默认传入这两个参数，目的是因为处理分页查询图片主要是为了前端呈现，这样是简化操作。
        :param filter_dict:  查询条件字典
        :param sort_dict:  排序条件字典
        :param projection:  投影数组,决定输出哪些字段?
        :param page_size:  一页有多少条记录?
        :param ruler: 翻页器最多显示几个页码？
        :param page_index: 页码(当前页码)
        :param func: 额外的处理函数.这种函数用于在返回数据前对每条数据进行额外的处理.会把doc或者实例当作唯一的对象传入
        :return: 字典对象.
        查询结果示范:
        {
            "total_record": record_count,
            "total_page": page_count,
            "data": res,
            "current_page": page_index,
            "pages": pages
        }
        """
        if isinstance(page_size, int):
            pass
        elif isinstance(page_size, float):
            page_size = int(page_size)
        elif isinstance(page_size, str) and page_size.isdigit():
            page_size = int(page_size)
        else:
            page_size = 10
        page_size = 1 if page_size < 1 else page_size

        if isinstance(page_index, int):
            pass
        elif isinstance(page_index, float):
            page_index = int(page_index)
        elif isinstance(page_index, str) and page_index.isdigit():
            page_index = int(page_index)
        else:
            page_size = 1
        page_index = 1 if page_index < 1 else page_index

        skip = (page_index - 1) * page_size
        if sort_dict is not None:
            sort_list = [(k, v) for k, v in sort_dict.items()]  # 处理排序字典.
        else:
            sort_list = None
        table_name = cls._table_name
        ses = get_conn(table_name="{}.files".format(table_name))
        args = {
            "filter": filter_dict,
            "sort": sort_list,  # 可能是None,但是没问题.
            "projection": projection,
            "skip": skip,
            "limit": page_size
        }
        args = {k: v for k, v in args.items() if v is not None}
        """开始计算分页数据"""
        record_count = ses.count_documents(filter=filter_dict)
        page_count = math.ceil(record_count / page_size)  # 共计多少页?
        delta = int(ruler / 2)
        range_left = 1 if (page_index - delta) <= 1 else page_index - delta
        range_right = page_count if (range_left + ruler - 1) >= page_count else range_left + ruler - 1
        pages = [x for x in range(range_left, int(range_right) + 1)]
        """开始查询页面"""
        res = list()
        ses = cls.fs_cls()
        r = ses.find(**args)
        if r is None:
            pass
        else:
            if func:
                res = [func(cls.transform(doc=cls.get_dict_from_fs(x))) for x in r]
            else:
                res = [cls.transform(doc=cls.get_dict_from_fs(x)) for x in r]
        resp = {
            "total_record": record_count,
            "total_page": page_count,
            "data": res,
            "current_page": page_index,
            "pages": pages
        }
        return resp


class BaseDoc:
    """所有存储到mongo的类都应该继承此类"""
    type_dict = dict()
    """
    用于检查属性类型的容器 需要在子类中被重写,一般的重写方法如下：
    type_dict = dict()
    type_dict['user_name'] = str
    type_dict['age'] = int
    type_dict['job'] = list
    """

    _table_name = "table_name"
    """定义表名，需要在子类中被重写
    _table_name = "table_name"  
    """

    def table_name(self) -> str:
        """获取表名"""
        return self._table_name

    @classmethod
    def get_table_name(cls) -> str:
        """获取表名"""
        return cls._table_name

    def __init__(self, **kwargs):
        """构造器"""
        for k, v in kwargs.items():
            k = camel_to_pep8(k)  # 转换驼峰到pep8
            if k in self.type_dict:
                if isinstance(v, self.type_dict[k]):
                    self.__dict__[k] = v
                else:
                    type_name = self.type_dict[k]
                    try:
                        if type_name.__name__ == "datetime":
                            temp = None
                            try:
                                temp = get_datetime_from_str(v)
                            except ValueError as e:
                                print(e)
                                try:
                                    """可能是时间戳"""
                                    temp = get_datetime_from_timestamp(v)
                                except ValueError as e1:
                                    print(e1)
                                    logger.info("datetime transform error", exc_info=True, stack_info=True)
                                    raise e1
                            finally:
                                if temp is not None:
                                    self.__dict__[k] = temp
                                else:
                                    pass
                        elif type_name.__name__ == "date":
                            temp = get_date_from_str(v)
                            if temp is not None:
                                self.__dict__[k] = temp
                            else:
                                pass
                        elif type_name.__name__ == "DBRef" and v is None:
                            """允许初始化时为空"""
                            pass
                        elif type_name.__name__ == "ObjectId" and v is None:
                            pass
                        elif type_name.__name__ == "GeoJSON" and isinstance(v, dict):
                            self.__dict__[k] = GeoJSON(v['type'], v['coordinates'])
                        elif v is None and k != "_id":
                            """空值不处理,防止None被初始化"""
                            pass
                        else:
                            self.__dict__[k] = type_name(v)
                    except ValueError as e:
                        print(e)
                        raise e

            else:
                if k != "_id" and (v is None or (isinstance(v, str) and v.lower() == "null")):
                    pass
                else:
                    self.__dict__[k] = v

    def __str__(self):
        return str(self.__dict__)

    def get_id(self):
        """返回_id"""
        return self._id

    def get_attr(self, attr_name, default=None):
        """获取某一个属性的值"""
        res = self.__dict__.get(attr_name)
        return default if res is None else res

    def add_attr(self, attr_name, attr_value):
        """添加一个属性"""
        self.__dict__[attr_name] = attr_value

    def pop_attr(self, attr_name, default=None):
        """弹出一个属性,同时删除对应的值"""
        return self.__dict__.pop(attr_name, default)

    def remove_attr(self, attr_name):
        """移除一个属性"""
        self.__dict__.pop(attr_name, None)

    def set_attr(self, attr_name: str, attr_value) -> bool:
        """设置属性"""
        res = False
        try:
            self.__dict__[attr_name] = attr_value
            res = True
        except TypeError as e:
            raise e
        except KeyError as e:
            raise e
        finally:
            return res

    def get_dict(self, ignore: list = None) -> dict:
        """
        获取self.__dict__
        :param ignore: 忽略的字段名
        :return:
        """
        if ignore is None or len(ignore) == 0:
            return self.__dict__
        else:
            return {k: v for k, v in self.__dict__.items() if k not in ignore}

    def save(self, ignore: list = None, upsert: bool = True) -> (None, ObjectId):
        """
        更新
        :param ignore: 忽略的更新的字段,一般是有唯一性验证的字段
        :param upsert:  在查找对象不存在的情况下,是否查询?
        :return: ObjectId
        """
        if isinstance(ignore, list):
            if "_id" in ignore:
                pass
            else:
                ignore.append("_id")
        else:
            ignore = ["_id"]
        ses = get_conn(self.table_name())
        doc = self.__dict__
        _id = doc.get("_id", None)
        doc = {k: v for k, v in doc.items() if k not in ignore}
        if _id is None:
            return ses.insert_one(document=doc)
        else:
            f = {"_id": _id}
            res = None
            try:
                res = ses.replace_one(filter=f, replacement=doc, upsert=upsert)
            except Exception as e:
                ms = "error_cause:{},filter:{}, replacement:{}".format(e, f, doc)
                print(ms)
                logger.exception(ms)
                raise e
            if res is None:
                return res
            else:
                """
                insert的情况
                UpdateResult = {
                    ....
                    acknowledged: True,
                    matched_count: 0,
                    modified_count: 0,
                    raw_result: {
                                  'n': 1, 'updatedExisting': False, 
                                  'nModified': 0, 'ok': 1, 
                                  'upserted': ObjectId('5b051532c55c281e882494e0')
                                }
                    upserted_id: ObjectId("5b051532c55c281e882494e0")
                }
                update的情况
                UpdateResult = {
                    ....
                    acknowledged: True,
                    matched_count: 1,
                    modified_count: 1,
                    raw_result: {
                                  'nModified': 1, 
                                  'updatedExisting': True, 
                                  'ok': 1, 'n': 1
                                }
                    upserted_id: None
                }
                如果是插入新的对象,res.upserted_id就是新对象的_id,
                如果是修改旧的对象,res.upserted_id对象为空,这时返回的结果中不包含被修改的对象的id(另行查找),
                本例是以_id查找,在修改旧对象的情况下,不用另行查找也能获得被修改对象的id.
                """
                return _id if res.upserted_id is None else res.upserted_id

    def delete_self(self, obj=None):
        """删除自己"""
        obj = self if obj is None else obj
        table_name = obj.table_name()
        ses = get_conn(table_name=table_name)
        o_id = self._id
        result = ses.delete_one({"_id": o_id})
        if result.deleted_count == 1:
            return True
        else:
            return False

    def in_list(self, attr_name, current_obj):
        """
        检查某个对象是否在self的list类型的属性中？
        如果不在就插入，如果在就pass
        :param attr_name:  list类型的属性的名称。
        :param current_obj: 被检测的对象,某个类的实例
        :return: None
        """
        current_id = current_obj.get_id()
        if current_id is None:
            current_id = current_obj.insert()
            current_obj._id = current_id
        old_dbref_list = self.__dict__.get(attr_name)
        dbref_obj = current_obj.get_dbref()
        if old_dbref_list is None:
            old_dbref_list = [dbref_obj]
        elif current_id not in [x.id for x in old_dbref_list]:
            old_dbref_list.append(dbref_obj)
        else:
            pass
        self.__dict__[attr_name] = old_dbref_list

    def to_flat_dict(self, ignore_columns: list = None):
        """
        进行把对象都转换成数字或者字符串这种可以进行json序列化的类型
        :param ignore_columns: 被忽略的列名的数组
        :return:
        """
        result_dict = to_flat_dict(self.get_dict(), ignore_columns=ignore_columns)
        return result_dict

    @classmethod
    def exec(cls, exe_name: str, write_concern: (dict, WriteConcern) = None, *args, **kwargs) -> ObjectId:
        """
        执行Collection的原生命令
        :param exe_name:
        :param write_concern: 写关注
        :param args:
        :param kwargs:
        :return:
        """
        conn = cls.get_collection(write_concern=write_concern)
        if hasattr(conn, exe_name):
            handler = getattr(conn, exe_name)
            handler(*args, **kwargs)
        else:
            ms = "pymongo.Collection没有{}这个方法".format(exe_name)
            raise RuntimeError(ms)

    @classmethod
    def replace_one(cls, filter_dict: dict, replace_dict: dict, upsert: bool = False) -> bool:
        """
        替换一个文档.
        :param filter_dict: 过滤器
        :param replace_dict:  替换字典
        :param upsert: 不存在是否插入?
        :return:
        """
        ses = get_conn(cls.get_table_name())
        res = ses.replace_one(filter=filter_dict, replacement=replace_dict, upsert=upsert)
        return res

    @staticmethod
    def simple_doc(doc_dict: dict, ignore_columns: list = None) -> dict:
        """
        把doc转换成可被json序列化的格式
        :param doc_dict: 等待被精简的doc,一般是to_flat_dict方法处理过的实例
        :param ignore_columns: 不需要的列名
        :return: 精简过的doc
        """
        ignore_columns = [] if ignore_columns is None else ignore_columns
        result = to_flat_dict(doc_dict, ignore_columns)
        return result

    @classmethod
    def find_one_and_insert(cls, **kwargs):
        """
        检查一个对象是否存在？不存在就插入，存在就返回这个对象的ObjectId
        :param kwargs: 匹配参数
        :return: ObjectId或者None
        """
        obj = cls.find_one(**kwargs)
        if obj is None:
            return obj.insert(**kwargs)
        else:
            return obj._id

    def push_one(self, col_name, col_val):
        """
        向一个数组形式的列中追加一个对象。
        :param col_name: 需要插入数据的列名
        :param col_val: 等待插入的值
        :return:Boolean
        """
        o_id = self.get_id()
        ses = get_conn(self._table_name)
        res = ses.update_one(filter={"_id": o_id}, update={"$push": {col_name: col_val}})
        if res.raw_result['ok'] == 1:
            return True
        else:
            return False

    def push_batch(self, col_name, col_val):
        """
        向一个数组形式的列中追加多个对象。
        :param col_name: 需要插入数据的列名
        :param col_val: 等待插入的值的list对象
        :return:Boolean
        """
        o_id = self.get_id()
        ses = get_conn(self._table_name)
        res = ses.update_one(filter={"_id": o_id}, update={"$pushAll": {col_name: col_val}})
        if res.raw_result['ok'] == 1:
            return True
        else:
            return False

    def pull(self, col_name, col_val):
        """
        向一个数组形式的列中删除对象所有等于co_val值的col_name的子元素都将被删除。
        :param col_name: 需要插入数据的列名
        :param col_val: 等待插入的值
        :return:Boolean
        """
        o_id = self.get_id()
        ses = get_conn(self._table_name)
        res = ses.update_one(filter={"_id": o_id}, update={"$pull": {col_name: col_val}})
        if res.raw_result['ok'] == 1:
            return True
        else:
            return False

    @classmethod
    def get_collection(cls, write_concern: (WriteConcern, dict) = None):
        """
        获取一个collection对象,这个对象可以执行绝大多数对数据库的操作.
        可以看作这是一个万能的数据库操作handler.只是略微复杂点而已.
        :param write_concern: 写关注
        :return:
        """
        table_name = cls.get_table_name()
        conn = get_conn(table_name=table_name, write_concern=write_concern)
        return conn

    @classmethod
    def insert_one(cls, doc: dict, write_concern: (WriteConcern, dict) = None) -> ObjectId:
        """
        把参数转换为对象并插入
        :param doc: 待插入文档
        :param write_concern: 写关注. {w:'majority', j:True}
        :return: ObjectId
        """
        result = None
        wc = dict()
        if write_concern is None:
            pass
        elif isinstance(write_concern, dict):
            wc = dict()
            if "w" in write_concern:
                wc['w'] = write_concern['w']
            if "j" in write_concern:
                wc['j'] = write_concern['j']
            if len(wc) > 0:
                wc = WriteConcern(**wc)
        elif isinstance(write_concern, WriteConcern):
            wc = write_concern
        else:
            pass
        if isinstance(wc, WriteConcern):
            col = cls.get_collection(write_concern=wc)
        else:
            col = cls.get_collection()
        res = None
        try:
            res = col.insert_one(document=doc)
        except Exception as e:
            logger.exception(msg=e)
            raise e
        finally:
            if isinstance(res, InsertOneResult):
                result = res.inserted_id
            else:
                pass
            return result

    @classmethod
    def insert_many_and_return_doc(cls, input_list: list) -> list:
        """
        retry_insert_many_after_error  的辅助函数,批量插入,并返回成功和失败的结果.
        :param input_list: 待处理的数据ｌｉｓｔ．是ｄｏｃ(有_id的,)．不能是dict或者cls的实例.
        :return: 插入成功的Object的list
        """
        if len(input_list) == 0:
            return []
        else:
            ses = get_conn(cls.get_table_name())
            return_doc = []
            length = len(input_list)
            step = 4000
            if len(input_list) > step:
                """切割大数组"""
                raw = list()
                begin = 0
                end = step
                while begin < length:
                    sub = input_list[begin: end]
                    raw.append(sub)
                    begin += step
                    end += step
            else:
                raw = [input_list]
            for sub in raw:
                success_ids = []
                try:
                    inserted_results = ses.insert_many(sub, ordered=False)  # 无序写,希望能返回所有出错信息.默认有序
                    success_ids = inserted_results.inserted_ids
                except pymongo.errors.BulkWriteError as e:
                    ms = "insert_many_and_return_doc func Error:{}, args={}".format(e, input_list)
                    logger.info(ms)
                    raise e
                except Exception as e1:
                    success_ids = []
                    ms = "retry_insert_many_after_error Error: {}".format(e1)
                    logger.exception(ms)
                    raise e1
                finally:
                    if len(success_ids) > 0:
                        return_doc.extend(success_ids)
            return return_doc

    @classmethod
    def insert_many(cls, doc_list: list)->list:
        """
        批量插入，如果插入失败，就会变成save，如果save失败，会抛出异常。
        :param doc_list: mongodb的doc组成的数组，也是dict的list
        :return: 插入成功的doc组成的list,插入失败，将返回[]
        """

        """ 原始方法,先注销  
        if not structured:
            doc_list = [cls(**x).__dict__ for x in doc_list if x.get('ts') != "0"]  # x.get('ts') != "0"防止错误的时间戳
        else:
            doc_list = [x.__dict__ for x in doc_list]
        """
        if len(doc_list) == 0:
            return list()
        else:
            is_instance = isinstance(doc_list[0], cls)
            """如果是实例的数组,那就转成"""
            doc_list = doc_list if is_instance else [cls(**doc).__dict__ for doc in doc_list]  # 可以把实例的数组转成doc/dict的数组.
            success_doc_list = cls.insert_many_and_return_doc(input_list=doc_list)
            return success_doc_list

    @classmethod
    def delete_many(cls, filter_dict: dict) -> None:
        """
        批量删除
        :param filter_dict:
        :return:
        """
        if filter_dict is None or len(filter_dict) == 0:
            pass
        else:
            ses = get_conn(cls.get_table_name())
            ses.delete_many(filter=filter_dict)

    @classmethod
    def create_dbref(cls, object_id):
        """
        通过一个object_id获取一个对象的DBRef对象
        :param object_id: _id ，ObjectId/str格式
        :return:  DBRef的实例
        """
        object_id = get_obj_id(object_id)
        obj = DBRef(cls._table_name, object_id, db_name)
        return obj

    @classmethod
    def statistics(cls, map_func: Code, reduce_func: Code, full_response: bool = True) -> dict:
        """
        map-reduce函数，注意两个函数的写法
        :param map_func:
        :param reduce_func:
        :param full_response:
        :return:

        """
        """函数写法示意"""
        # map_func = Code("""function(){
        #     emit(this.key, this.number);
        # }""")
        # reduce_func = Code("""function(key, values){
        #     var sum = 0;
        #     var l = values.length;
        #     for(var i=0; i<l; i++){
        #         var temp = values[i];
        #         sum += temp.
        #     }
        #     return sum;
        # }""")
        table_name = cls.get_table_name()
        ses = get_conn(table_name)
        result = ses.map_reduce(map=map_func, reduce=reduce_func, out="map_reduce_result", full_response=True)
        return result

    @classmethod
    def count(cls, filter_dict: dict, session: ClientSession = None, **kwargs):
        """统计
        :param filter_dict: 过滤器字典
        :param session: pymongo.client_session.ClientSession 实例
        :return:
        """
        table_name = cls.get_table_name()
        ses = get_conn(table_name)
        result = ses.count(filter=filter_dict, session=session, **kwargs)
        return result

    @classmethod
    def distinct(cls, filter_dict: dict = None, key: str = None):
        """
        去重查找
        :param filter_dict: 过滤器字典
        :param key: 输出区域的字段,也是去重的字段
        :return:
        """
        table_name = cls.get_table_name()
        ses = get_conn(table_name)
        result = ses.distinct(key=key, filter=filter_dict)
        return result

    @classmethod
    def find_by_id(cls, o_id: (str, ObjectId), to_dict: bool = False, can_json: bool = False, debug: bool = False):
        """查找并返回一个对象，这个对象是o_id对应的类的实例
        :param o_id: _id可以是字符串或者ObjectId
        :param to_dict: 是否转换结果为字典?
        :param can_json: 是否转换结果为可json化的字典?注意如果can_json为真,to_dict参数自动为真
        :param debug: debug模式,开启后会记录所有的参数和返回结果.
        return cls.instance
        """
        raw_args = {"_id": o_id}
        o_id = get_obj_id(o_id)
        ses = get_conn(cls._table_name)
        result = ses.find_one({"_id": o_id})  # 返回的是文档
        if debug:
            record = {"doc": result}
            record.update(raw_args)
            logger.exception(msg=str(record))
        if result is None:
            return result
        else:
            if can_json:
                to_dict = True
            if to_dict:
                if can_json:
                    return to_flat_dict(result)
                else:
                    return result
            else:
                return cls(**result)

    @classmethod
    def find(cls, can_json=False, *args, **kwargs) -> list:
        """
        find的增强版本,根据条件查找对象,返回多个对象的实例
        :param can_json:       是否调用to_flat_dict函数转换成可以json的字典?
        :return: list of doc
        """
        ses = cls.get_collection()
        res = ses.find(*args, **kwargs)
        if can_json:
            result = [to_flat_dict(x) for x in res]
        else:
            result = [x for x in res]
        return result

    @classmethod
    def find_one(cls, filter_dict: dict = None, *args, **kwargs) -> dict:
        """
        根据条件查找对象,返回单个对象的实例
        :param filter_dict:
        :param args:
        :param kwargs:
        :return:
        """
        ses = cls.get_collection()
        result = ses.find_one(filter=filter_dict, *args, **kwargs)
        return result

    @classmethod
    def find_one_plus(cls, filter_dict: dict, sort_dict: dict = None, projection: list = None,
                      instance: bool = False, can_json: bool = False):
        """
        find_one的增强版，有sort的功能，在查询一个结果的时候，比sort效率高很多
        同理也需要一个find_plus作为find的增强版
        :param filter_dict:  查询的条件，
        :param sort_dict: 排序的条件  比如: {"time": -1}  # -1表示倒序
        :param projection:    投影数组,决定输出哪些字段?
        :param instance: 返回的是实例还是doc对象？默认是doc对象
        :param can_json: 是否转为可json 的dict?这个有联动性,can_json为真instance一定未假
        :return: None, dict,实例或者doc对象。
        """
        if can_json:
            instance = False
        table_name = cls._table_name
        ses = get_conn(table_name=table_name)
        if sort_dict is None or len(sort_dict) == 0:
            result = ses.find_one(filter=filter_dict)
        else:
            sort_list = [(k, v) for k, v in sort_dict.items()]
            args = {
                "filter": filter_dict,
                "sort": sort_list,  # 可能是None,但是没问题.
                "projection": projection
            }
            args = {k: v for k, v in args.items() if v is not None}
            result = ses.find_one(**args)
        if result is None:
            return result
        else:
            if not instance:
                if can_json:
                    return to_flat_dict(result)
                else:
                    return result
            else:
                return cls(**result)

    @classmethod
    def find_one_and_delete(cls, filter_dict: dict, sort_dict: dict = None, projection: list = None,
                            instance: bool = False) -> (dict, None):
        """
        找到并删除一个对象
        :param filter_dict:  查询的条件，
        :param sort_dict: 排序的条件  比如: {"time": -1}  # -1表示倒序
        :param projection:    投影数组,决定输出哪些字段?
        :param instance: 返回的是实例还是doc对象？默认是doc对象
        :return: None, 实例或者doc对象。
        """
        table_name = cls._table_name
        ses = get_conn(table_name=table_name)
        if sort_dict is not None:
            sort_list = [(k, v) for k, v in sort_dict.items()]  # 处理排序字典.
        else:
            sort_list = None
        args = {
            "filter": filter_dict,
            "sort": sort_list,  # 可能是None,但是没问题.
            "projection": projection
        }
        args = {k: v for k, v in args.items() if v is not None}
        res = ses.find_one_and_delete(**args)
        if instance:
            res = cls(**res)
        return res

    @classmethod
    def find_one_and_update(cls, filter_dict: dict, update_dict: dict, projection: list = None, sort_dict: dict = None, upsert: bool = True,
                            return_document: str="after"):
        """
        本方法是find_one_and_update和find_alone_and_update的增强版.推荐使用本方法!
        和本方法相比find_one_and_update和find_alone_and_update更简单易用.
        本方法更灵活,只是在设置参数时要求更高.
        找到一个文档然后更新它，(如果找不到就插入)
        :param filter_dict: 查找时匹配参数 字典
        :param update_dict: 更新的数据，字典,注意例子中参数的写法,有$set和$inc两种更新方式.
        :param projection: 输出限制列  projection={'seq': True, '_id': False} 只输出seq，不输出_id
        :param upsert: 找不到对象时是否插入新的对象 布尔值
        :param sort_dict: 排序列字典,举例: {"time": -1}  # -1表示倒序,注意排序字典参数的处理
        :param return_document: 返回update之前的文档还是之后的文档？ after 和 before
        :return:  doc或者None
        example:
        filter_dict = {"something": ...}
        update_dict = {"$set": {"prev_date": datetime.datetime.now(),
                                "last_query_result_id": last_query_result_id},
                       "$inc": {"online_query_count": 1, "all_count": 1,
                                "today_online_query_count": 1}}
        self.find_one_and_update(filter_dict=filter_dict, update=update_dict)
        """
        if sort_dict is not None:
            sort_list = [(k, v) for k, v in sort_dict.items()]
        else:
            sort_list = None
        table_name = cls._table_name
        ses = get_conn(table_name=table_name)
        args = {
            "filter": filter_dict,
            "sort": sort_list,   # 可能是None,但是没问题.
            "projection": projection,
            "update": update_dict,
            "upsert": upsert,
            "return_document": ReturnDocument.BEFORE if return_document.lower() != "after" else ReturnDocument.AFTER

        }
        args = {k: v for k, v in args.items() if v is not None}
        result = None
        try:
            result = ses.find_one_and_update(**args)
        except Exception as e:
            ms = "args: {}".format(args)
            logger.exception(ms)
            raise e
        return result

    @classmethod
    def update_many_plus(cls, filter_dict: dict, update_dict: dict, upsert: bool = False,
                         document_validation: bool = False) -> (list, None):
        """
        根据条件查找对象,进行批量更新
        :param filter_dict: 查找时匹配参数 字典
        :param update_dict: 更新的数据，字典,注意例子中参数的写法,有$set和$inc两种更新方式.
        :param upsert: 更新对象不存在的时候是否插入新的数据?
        :param document_validation: 是否启用文档验证机制?(前提是你这个表设置了文档验证器)
        :return:  pymongo.results.UpdateResult
        example:
        filter_dict = {"something": ...}
        update_dict = {"$set": {"prev_date": datetime.datetime.now(),
                                "last_query_result_id": last_query_result_id},
                       "$inc": {"online_query_count": 1, "all_count": 1,
                                "today_online_query_count": 1}}
        self.find_one_and_update(filter_dict=filter_dict, update=update_dict)
        """
        table_name = cls._table_name
        ses = get_conn(table_name=table_name)
        args = {
            "filter": filter_dict,
            "update": update_dict,
            "upsert": upsert,
            "bypass_document_validation": document_validation,
            "collation": None
        }
        res = ses.update_many(**args)
        return res

    @classmethod
    def near_by_point(cls, the_class: type = None, col: str = "loc",
                      min_distance: [float, int] = 0.0,
                      max_distance: [float, int] = 0.0,
                      limit: int = 50,
                      geometry: GeoJSON = None) -> list:
        """
        基于地理位置的计算：根据一个点，找到附近的点。
        :param the_class: 待查找的类本身。type类型。用于取得对应的表名。
        :param col: 储存geo信息的列的名称。
        :param min_distance: 最小距离，float/int类型。单位是米
        :param max_distance: 最大距离，float/int类型。单位是米
        :param limit: 输出数量限制，int类型。
        :param geometry: 基准点，一个GeoJSON对象或者可以转化为GeoJSON对象的字典/数组。
        :return: 结果dict组成的list
        """
        try:
            limit = int(limit)
        except ValueError as e:
            print(e)
            limit = 50
        finally:
            if limit == 0:
                limit = 50
            elif limit > 500:
                limit = 500
            else:
                pass

        the_cls = cls  # 类（的构造器）
        if the_class is not None and isinstance(the_class, type):
            """如果the_class确实是一个类"""
            the_cls = the_class
        table_name = the_cls.get_table_name()  # 取表名
        """判断列是是否是GeoJSON类型"""
        col_type = the_cls.type_dict.get(col)
        """检查类定义的列类型"""
        if col_type != "GeoJSON" and col_type is not None:
            try:
                raise TypeError("{}的定义不是一个GeoJSON对象,期待GeoJSON，得到{}".format(col, col_type))
            except TypeError as e:
                logger.error("Init Error:", exc_info=True, stack_info=True)
                raise e
        else:
            """转换GeoJSON对象"""
            if isinstance(geometry, GeoJSON):
                pass
            else:
                geometry = GeoJSON.get_instance(geometry)
            ses = get_conn(table_name)
            ses = get_conn("geo_test_info", "my_training")
            """开始组装查询字典"""
            query_dict = {col: {"$near": {
                "$geometry": geometry,
                "$maxDistance": max_distance,
                "$min_Distance": min_distance}}}
            res = ses.find(query_dict).limit(limit)
            if res is None:
                return None
            else:
                return [x for x in res]

    @classmethod
    def query_by_page(cls, filter_dict: dict, sort_cond: (dict, list) = None, projection: list = None, page_size: int = 10,
                      ruler: int = 5, page_index: int = 1, to_dict: bool = True, can_json: bool = False,
                      func: object = None, target: str = "dict") -> dict:
        """
        分页查询
        :param filter_dict:  查询条件字典
        :param sort_cond:  排序条件字典/数组,如果是数组,那就是[(name, 1),(time,-1),...]这样的样式
        :param projection:  投影数组,决定输出哪些字段?
        :param page_size: 每页多少条记录
        :param ruler: 翻页器最多显示几个页码？
        :param page_index: 页码(当前页码)
        :param to_dict: 返回的元素是否转成字典(默认就是字典.否则是类的实例)
        :param can_json: 是否调用to_flat_dict函数转换成可以json的字典?
        :param func: 额外的处理函数.这种函数用于在返回数据前对每条数据进行额外的处理.会把doc或者实例当作唯一的对象传入
        :param target: 和func参数配合使用,指明func是对实例本身操作还是对doc进行操作(instance/dict)
        :return: 字典对象.
        查询结果示范:
        {
            "total_record": record_count,
            "total_page": page_count,
            "data": res,
            "current_page": page_index,
            "pages": pages
        }
        """
        if isinstance(page_size, int):
            pass
        elif isinstance(page_size, float):
            page_size = int(page_size)
        elif isinstance(page_size, str) and page_size.isdigit():
            page_size = int(page_size)
        else:
            page_size = 10
        page_size = 1 if page_size < 1 else page_size

        if isinstance(page_index, int):
            pass
        elif isinstance(page_index, float):
            page_index = int(page_index)
        elif isinstance(page_index, str) and page_index.isdigit():
            page_index = int(page_index)
        else:
            page_size = 1
        page_index = 1 if page_index < 1 else page_index

        skip = (page_index - 1) * page_size
        if can_json:
            to_dict = True
        if sort_cond is not None:
            if isinstance(sort_cond, dict):
                sort_list = [(k, v) for k, v in sort_cond.items()]  # 处理排序字典.
            else:
                sort_list = sort_cond
        else:
            sort_list = None
        table_name = cls._table_name
        ses = get_conn(table_name=table_name)
        args = {
            "filter": filter_dict,
            "sort": sort_list,   # 可能是None,但是没问题.
            "projection": projection,
            "skip": skip,
            "limit": page_size
        }
        args = {k: v for k, v in args.items() if v is not None}
        """开始计算分页数据"""
        record_count = ses.count(filter=filter_dict)
        page_count = math.ceil(record_count / page_size)  # 共计多少页?
        delta = int(ruler / 2)
        range_left = 1 if (page_index - delta) <= 1 else page_index - delta
        range_right = page_count if (range_left + ruler - 1) >= page_count else range_left + ruler - 1
        pages = [x for x in range(range_left, int(range_right) + 1)]
        """开始查询页面"""
        res = list()
        r = ses.find(**args)
        if r is None:
            pass
        else:
            if r.count() > 0:
                if to_dict:
                    if func and target == "dict":
                        if can_json:
                            res = [to_flat_dict(func(x)) for x in r]
                        else:
                            res = [func(x) for x in r]
                    else:
                        if can_json:
                            res = [to_flat_dict(x) for x in r]
                        else:
                            res = [x for x in r]
                else:
                    if func and target == "instance":
                        res = [func(cls(**x)) for x in r]
                    else:
                        res = [cls(**x) for x in r]
            else:
                pass
        resp = {
            "total_record": record_count,
            "total_page": page_count,
            "data": res,
            "current_page": page_index,
            "pages": pages
        }
        return resp


class FlaskUrlRule(BaseDoc):
    """
        App所有的路由规则
    """
    _table_name = "flask_url_rule"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['methods'] = list  # 视图函数的方法
    type_dict['args'] = list  # 视图函数的参数
    type_dict['endpoint'] = str  # 视图函数的端点
    type_dict['rule'] = str  # 路由规则
    type_dict['desc'] = str  # 路由说明

    collection_exists(table_name=_table_name, auto_create=True)  # 自动创建表.事务不会自己创建表

    @classmethod
    def init(cls, flask_app: Flask) -> None:
        """
        注册flask的app的所有路由规则
        :param flask_app:
        :return:
        """
        rules = flask_app.url_map.iter_rules()
        ses = cls.get_collection(write_concern=get_write_concern())
        for a_rule in rules:
            methods = [x.lower() for x in a_rule.methods if x.lower() in ["post", 'get']]
            args = [x for x in a_rule.arguments]
            endpoint = a_rule.endpoint
            rule = a_rule.rule
            f = {"endpoint": endpoint}
            u = {"$set": {"args": args, "rule": rule, "methods": methods}}
            ses.find_one_and_update(filter=f, update=u, upsert=True)

    @classmethod
    def save_doc(cls, doc: dict) -> dict:
        """
        保存/更新
        :param doc:
        :return:
        """
        ses = cls.get_collection(write_concern=get_write_concern())
        if "_id" in doc:
            """有_id,这是在更新"""
            f = {"_id": doc.pop("_id")}
        else:
            """没有id,这是在插入"""
            endpoint = doc.pop("endpoint", None)
            if endpoint is None:
                ms = "{} 没有必须的属性 endpoint".format(doc)
                raise ValueError(ms)
            else:
                f = {"endpoint": endpoint}
        u = {"$set": doc}
        ses = cls.get_collection(write_concern=get_write_concern())
        re_doc = ses.find_one_and_update(filter=f, update=u, upsert=True, return_document=ReturnDocument.AFTER)
        return re_doc


class OperateLog(BaseDoc):
    """
    操作日志,使用装饰器记录@OperateLog.log,
    唯一的限制就是
    1. 函数中必须有一个handler参数
    2. handler必须是(用户)类的实例对象.
    否则无法记录函数是由什么类的实例调用的.
    """
    _table_name = "global_log"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['handler_class'] = str   # 操作者的类的名字
    type_dict['handler_collection'] = str   # 操作者的类的数据库表的名字
    type_dict['handler_id'] = ObjectId  # 操作者id,
    type_dict['func_class'] = str  # 函数所属的类名,可能为空(独立函数)
    type_dict['function_name'] = str  # 函数名
    type_dict['args'] = list  # 函数args参数
    type_dict['kwargs'] = dict  # 函数kwargs参数
    type_dict['time'] = datetime.datetime

    @classmethod
    def _log(cls, **kwargs) -> None:
        """
        记录操作的内部方法
        kwargs内部共有如下参数:
        :param handler_id:
        :param handler_collection:
        :param handler_class:
        :param func_class:
        :param function_name:
        :param args_list:
        :param kwargs_dict:
        :return:
        """
        if 'time' not in kwargs:
            kwargs['time'] = datetime.datetime.now()
        cls.insert_one(kwargs)

    @staticmethod
    def log(func):
        """
        记录操作的装饰器.@OperateLog.log,
        本方法理论上能记录所有的函数操作,唯一的限制就是
        1. 函数中必须有一个handler参数
        2. handler必须是(用户)类的实例对象.
        否则无法记录函数是由什么类的实例调用的.
        """
        @functools.wraps(func)
        def decorated_function(*args, **kwargs):
            """取日志需要记录的内容"""
            f_str = func.__str__()
            func_class = None
            class_name_str = f_str.split("at", 1)[0].split(" ")[1].strip()
            function_name = func.__name__
            if function_name in class_name_str and function_name != class_name_str:
                """类方法"""
                func_class = class_name_str.split(".")[0]
            else:
                pass
            kw = {"func_class": func_class, "function_name": function_name}
            handler = kwargs.get("handler", None)
            if isinstance(handler, BaseDoc):
                """可以采集信息"""
                handler_class = handler.__class__.__name__
                handler_collection = handler.table_name()
                handler_id = handler.get_id()
            else:
                handler_class = None
                handler_collection = None
                if isinstance(handler, dict) and "_id" in handler:
                    handler_id = handler['_id']
                else:
                    handler_id = None
            kw['handler_id'] = handler_id
            kw['handler_collection'] = handler_collection
            kw['handler_class'] = handler_class
            args2 = other_can_save(args)
            kw['args_list'] = args2
            kw2 = other_can_save(kwargs)
            kw['kwargs_dict'] = kw2
            OperateLog._log(**kw)
            """返回原函数"""
            return func(*args, **kwargs)

        return decorated_function


"""
 一些辅助的函数,2017-11-01之后添加,很多函数在tools_module里面也有一套,这里重复的原因是有时候引用tools_module模块
不是很方便,容易导致循环引用.
"""


def normal_distribution_range(bottom_value: (float, int), top_value: (float, int), list_length: int = 1000,
                              value_type: (type, str) = float, decimal_length: int = 1) -> list:
    """
    生成一个正态分布的数组
    :param bottom_value: 正态分布的最小值.
    :param top_value: 正态分布的最大值.
    :param list_length: 返回的数组的长度.
    :param value_type: 返回的数组的元素的类型,默认是float,如果设置为int,那么decimal_length参数将无效.
    :param decimal_length: value_type参数为float的情况下,返回的元素保留几位小数点?默认为1,value_type为int此参数无效.
    :return: 数组
    """
    if not isinstance(bottom_value, float):
        try:
            bottom_value = float(bottom_value)
        except ValueError as e:
            ms = "{}不能转换成一个float对象".format(bottom_value)
            raise ValueError(ms)
        except TypeError as e:
            ms = "{}不能转换成一个float对象".format(bottom_value)
            raise TypeError(ms)
        finally:
            pass
    if not isinstance(top_value, float):
        try:
            top_value = float(top_value)
        except ValueError as e:
            ms = "{}不能转换成一个float对象".format(top_value)
            raise ValueError(ms)
        except TypeError as e:
            ms = "{}不能转换成一个float对象".format(top_value)
            raise TypeError(ms)
        finally:
            pass
    if not isinstance(list_length, int):
        try:
            list_length = int(list_length)
        except ValueError as e:
            ms = "{}不能转换成一个int对象".format(list_length)
            raise ValueError(ms)
        except TypeError as e:
            ms = "{}不能转换成一个int对象".format(list_length)
            raise TypeError(ms)
        finally:
            if list_length < 0:
                raise ValueError("list_length必须是一个正整数.")
    if value_type == int or value_type == float:
        pass
    else:
        if isinstance(value_type, str):
            value_type = value_type.lower()
            if value_type == "int":
                value_type = int
            elif value_type == "float":
                value_type = float
            else:
                ms = "错误的value_type参数:{}".format(value_type)
                raise ValueError(ms)
        else:
            ms = "value_type参数类型错误,期待一个str/type,得到一个{}".format(type(value_type))
            raise TypeError(ms)
    if value_type == int:
        decimal_length = 0
    else:
        if isinstance(decimal_length, int):
            pass
        else:
            try:
                decimal_length = int(decimal_length)
            except ValueError as e:
                ms = "{}不能转换成一个int对象".format(decimal_length)
                raise ValueError(ms)
            except TypeError as e:
                ms = "{}不能转换成一个int对象".format(decimal_length)
                raise TypeError(ms)
            finally:
                if list_length < 0:
                    raise ValueError("decimal_length必须是一个正整数.")
    """开始生产数组"""
    if top_value == bottom_value:
        """等值数组"""
        value = round(float(top_value), decimal_length) if value_type == float else int(top_value)
        return [value] * list_length
    else:
        """开始计算中间值和步长"""
        middle_value = (bottom_value + (top_value - bottom_value) / 2) if top_value > bottom_value else (
            top_value + (bottom_value - top_value) / 2)
        step = abs((top_value - bottom_value)) / 10
    raw_range = np.random.randn(list_length)
    res = [float(str(round(middle_value + step * (-5 if i < -5 else (5 if i > 5 else i)),
                           decimal_length))) if value_type == float else int(
        middle_value + step * (-5 if i < -5 else (5 if i > 5 else i))) for i in raw_range]
    return res


if __name__ == "__main__":
    """
    多文档事务演示
    t1和t2请提前创建,事务不会自己创建collection,不然会报
    Cannot create namespace mq_db.t1 in multi-document transaction
    的错误
    """
    # class T1(BaseDoc):
    #     _table_name = "t1"
    #
    #
    # class T2(BaseDoc):
    #     _table_name = "t2"
    #
    #     def __init__(self, **kwargs):
    #         a = {}['name']
    #         super(T2, self).__init__(**kwargs)
    # client = get_client()
    # t1 = client[db_name]['t1']  # 操作t1表的collection,db_name是你的数据库名,你可以这么写client.db_name.collection_name
    # t2 = client[db_name]['t2']  # # 操作t2表的collection
    # with client.start_session(causal_consistency=True) as session:
    #     """事物必须在session下执行,with保证了session的正常关闭"""
    #     with session.start_transaction():
    #         """一旦出现异常会自动调用session.abort_transaction()"""
    #         t1.insert_one(document={"name": "jack"}, session=session)  # 注意多了session这个参数
    #         k = dict()['name']  # 制造一个错误,你会发现t1和t2的插入都不会成功.
    #         t2.insert_one(document={"name": "jack2"}, session=session)
    pass

