# -*- coding:utf-8 -*-
# from gevent import monkey
# monkey.patch_all()
import pymongo
from pymongo import monitoring
import warnings
import datetime
import hashlib
from uuid import uuid4
from bson.objectid import ObjectId
from bson.code import Code
from bson.errors import InvalidId
from bson.dbref import DBRef
from bson.son import SON
from bson.binary import Binary
import numpy as np
import re
import math
from pymongo import errors
from werkzeug.contrib.cache import RedisCache
from log_module import get_logger
from pymongo import ReturnDocument
from pymongo.errors import *
import warnings
from pymongo.errors import DuplicateKeyError


cache = RedisCache()
logger = get_logger()
user = "exe_root"              # 数据库用户名
password = "Try@Ex68769"       # 数据库密码
db_name = "platform_db"        # 库名称
mechanism = "SCRAM-SHA-1"      # 加密方式，注意，不同版本的数据库加密方式不同。

"""mongodb配置信息"""
"""
注意,使用连接池就不能使用mongos load balancer
mongos load balancer的典型连接方式: client = MongoClient('mongodb://host1,host2,host3/?localThresholdMS=30')
"""
mongodb_setting = {
    "host": "safego.org:20000",   # 数据库服务器地址            mongos 1
    # "host": "pltf.safego.org:7171",   # 数据库服务器地址          mongos 2
    # "host": "pltf.safego.org:8181",   # 数据库服务器地址        mongos 3
    "localThresholdMS": 30,  # 本地超时的阈值,默认是15ms,服务器超过此时间没有返回响应将会被排除在可用服务器范围之外
    "maxPoolSize": 800,  # 最大连接池,默认100,不能设置为0,连接池用尽后,新的请求将被阻塞处于等待状态.
    "minPoolSize": 0,  # 最小连接池,默认是0.
    "waitQueueTimeoutMS": 30000,  # 连接池用尽后,等待空闲数据库连接的超时时间,单位毫秒. 不能太小.
    "authSource": db_name,  # 验证数据库
    'authMechanism': mechanism,  # 加密
    # "readPreference": "secondaryPreferred",  # 读偏好,优先从盘,可以做读写分离,本例从盘不稳定.改为主盘优先
    # "readPreference": "primaryPreferred",  # 读偏好,优先从盘,可以做读写分离,本例从盘不稳定.改为主盘优先
    "readPreference": "secondaryPreferred",  # 读偏好,优先从盘,读写分离
    "username": user,       # 用户名
    "password": password    # 密码
}


"""副本集机器,留给异步队列监控健康状况的"""
replica_hosts = [
    {"host": "safego.org", "port": 27017},
    {"host": "safego.org", "port": 20000},
    {"host": "pltf.safego.org", "port": 7174},
    {"host": "pltf.safego.org", "port": 8184}
    ]


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
        command_name = event.command_name
        command_dict = event.command
        database_name = event.database_name
        ms = "Error: {} 数据库的 {} 命令执行失败,参数:{}".format(database_name, command_name, command_dict)
        print(ms)
        logger.exception(ms)


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


def get_db():
    """
    获取一个针对db_name对应的数据库的的连接，一般用于ORM方面。比如构建一个类。
    :return: 一个Database对象。
    """
    mongodb_conn = DB()
    conn = mongodb_conn[db_name]
    return conn


def get_conn(table_name):
    """
    获取一个针对table_name对应的表的的连接，一般用户对数据库进行增删查改等操作。
    :param table_name: collection的名称，对应sql的表名。必须。
    :return: 一个Collection对象，用于操作数据库。
    """
    if table_name is None or table_name == '':
        raise TypeError("表名不能为空")
    else:
        mongodb_conn = get_db()
        conn = mongodb_conn[table_name]
        return conn


def other_can_json(obj):
    """
    把其他对象转换成可json,是to_flat_dict的内部函数
    v = v.strftime("%F %H:%M:%S.%f")是v = v.strftime("%Y-%m-%d %H:%M:%S")的
    简化写法，其中%f是指毫秒， %F等价于%Y-%m-%d.
    注意，这个%F只可以用在strftime方法中，而不能用在strptime方法中
    """
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, (DBRef, MyDBRef)):
        return str(obj.id)
    elif isinstance(obj, datetime.datetime):
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


def to_flat_dict(a_dict, ignore_columns: list = list()) -> dict:
    """
    转换成可以json的字典,这是一个独立的方法
    to_flat_dict 实例方法.
    to_flat_dict 独立方法
    doc_to_dict  独立方法
    三个方法将在最后的评估后进行统一 2018-3-16
    :param a_dict: 待处理的doc.
    :param ignore_columns: 不需要返回的列
    :return:
    """
    return {other_can_json(k): other_can_json(v) for k, v in a_dict.items() if k not in ignore_columns}


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
    根据字符串返回datet对象
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
        logger.exception(ms)
    return the_date


def get_datetime_from_str(date_str: str) -> datetime.datetime:
    """
    根据字符串返回datetime对象
    :param date_str: 表示时间的字符串."%Y-%m-%d %H:%M:%S  "%Y-%m-%d %H:%M:%S.%f 或者 "%Y-%m-%d
    :return: datetime.datetime对象
    """
    if isinstance(date_str, (datetime.datetime, datetime.date)):
        return date_str
    elif isinstance(date_str, str):
        search = re.search(r'\d{4}.\d{1,2}.*\d', date_str)
        if search:
            date_str = search.group()
            pattern_0 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d$')  # 时间匹配2017-01-01
            pattern_1 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d$')  # 时间匹配2017-01-01 12:00:00
            pattern_2 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d\.\d+$') # 时间匹配2017-01-01 12:00:00.000
            pattern_3 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d\s\d+$') # 时间匹配2017-01-01 12:00:00 000
            pattern_4 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d$')  # 时间匹配2017-01-01T12:00:00
            pattern_5 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\.\d+$') # 时间匹配2017-01-01T12:00:00.000
            pattern_6 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\.\d{1,3}Z$')  # 时间匹配2017-01-01T12:00:00.000Z
            pattern_7 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\s\d+$')  # 时间匹配2017-01-01T12:00:00 000

            if pattern_7.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S %f")
            elif pattern_6.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            elif pattern_5.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            elif pattern_4.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            elif pattern_3.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %f")
            elif pattern_2.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
            elif pattern_1.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
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
    把两个字典合并成一个字典。目的是保留尽可能多的信息
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


def doc_to_dict(doc_obj: dict, ignore_columns: list = list())->dict:
    """
    此方法和to_flat_dict独立方法的不同是本方法不能处理嵌套的对象,
    所以推荐to_flat_dict独立方法.此函数保留只是为了兼容性.
    调用时会警告
    把一个mongodb的doc对象转换为纯的，可以被json转换的dict对象,
    注意，这个方法不能转换嵌套对象，嵌套对象请自行处理。
    to_flat_dict 实例方法.
    to_flat_dict 独立方法
    doc_to_dict  独立方法
    三个方法将在最后的评估后进行统一 2018-3-16
    :param doc_obj: mongodb的doc对象
    :param ignore_columns: 不需要返回的列
    :return: 可以被json转换的dict对象
    """
    ms = "已不推荐使用此方法,请用独立的to_flat_dict函数替代, 2018-3-16"
    warnings.warn(message=ms)
    res = dict()
    for k, v in doc_obj.items():
        if k in ignore_columns:
            pass
        else:
            if isinstance(v, datetime.datetime):
                v = v.strftime("%F %H:%M:%S.%f")
                """
                v = v.strftime("%F %H:%M:%S.%f")是v = v.strftime("%Y-%m-%d %H:%M:%S")的
                简化写法，其中%f是指毫秒， %F等价于%Y-%m-%d.
                注意，这个%F只可以用在strftime方法中，而不能用在strptime方法中
                """
            elif isinstance(v, datetime.date):
                v = v.strftime("%F")
            elif isinstance(v, ObjectId):
                v = str(v)
            elif isinstance(v, (MyDBRef, DBRef)):
                v = str(v.id)
            elif isinstance(v, dict):
                keys = list(v.keys())
                if len(keys) == 2 and "coordinates" in keys and "type" in keys:
                    """这是一个GeoJSON对象"""
                    v = v['coordinates']  # 前经度后纬度
                else:
                    pass
            else:
                pass
            res[k] = v
    return res


class Field:
    def __init__(self, col_name, col_type, sub_item_type=''):
        self.col_name = col_name
        self.col_type = col_type
        self.col_value = None
        if col_type == list or col_type == dict:
            self.sub_item_type = sub_item_type


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


class MyDBRef(DBRef):
    """自定义一个DBRef类，主要原本的初始化方法过于生僻，特进行简化"""
    def __init__(self, collection, id=None, database=None, _extra={}, obj=None, doc=None, **kwargs):
        """

        :param collection: 继承父类参数，表名,作为简化写法，你也可以在这里传入一个DBRef，MyDBRef或者mongodb的doc实例。
        :param id: 继承父类参数 object_id
        :param database: 继承父类参数 数据库名 这前三个参数和obj，(collection,database,id)不可共存。会优先覆盖后者
        :param _extra: 继承父类参数
        :param obj: 一个DBRef对象。这个参数和doc，(collection,database,id)不可共存。
        :param doc: 这个是从mongodb查询出来的DBRef的doc。这个参数和obj，(collection,database,id)不可共存。
        :param kwargs: 继承父类参数
        简化构造器
        example：
        dbref = MyDBRef(obj)
        isinstance(obj,(DBRef,MyDBRef,dict))
        """
        db = database
        if isinstance(collection, (DBRef, MyDBRef)) and id is None and obj is None:
            """只有一个参数，并且是DBRef实例的情况，这是为了兼容BaseDoc的构造器"""
            ref = None
            oid = None
            obj = collection
        elif isinstance(collection, dict) and id is None and doc is None:
            """只有一个参数，并且是dict实例的情况，这是为了兼容BaseDoc的构造器"""
            ref = None
            oid = None
            doc = collection
        else:
            ref = collection
            oid = id
        if not (ref and oid):
            """oid或者ref为空"""
            if isinstance(obj, (MyDBRef, DBRef)):
                ref = obj.collection
                oid = obj.id
                db = obj.database
            else:
                try:
                    ref = doc['$ref']
                    oid = doc['$id']
                    db = doc['$db']
                except KeyError as e:
                    print(e)
                    ref = doc['collection']
                    oid = doc['id']
                    db = doc['database']
                finally:
                    pass

        super(MyDBRef, self).__init__(collection=ref, id=oid, database=db)

    def to_dict(self) -> dict:
        """
        直接将self转换为dict的格式，和as_doc方法不同，本方法保留value原来的数据类型，而不是像as_doc全部转换为字符串格式。
        :return: dict
        """
        res = {"$id": self.id, "$ref": self.collection, "$db": self.database}
        return res


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

    def table_name(self):
        return self._table_name

    def get_id(self):
        """返回id对象"""
        return self._id

    def __eq__(self, other) -> bool:
        """
        重构的比较的方法．
        :param other: 另一个对象
        :return: 比较的结果．布尔值
        """
        if isinstance(other, self.__class__):
            if self.get_id() == other.get_id():
                return True
            else:
                d1 = self.__dict__
                d2 = other.__dict__
                d1.pop("_id")
                d2.pop("_id")
                return d1 == d2
        else:
            return False

    @classmethod
    def get_table_name(cls):
        return cls._table_name

    @classmethod
    def get_attr_from_cache(cls, o_id: (ObjectId, str), attr_name: str, default=None)-> (object, None):
        """
        从缓存中获取属性.
        :param o_id:　ObjectId
        :param attr_name:　属性名称
        :param default:　　默认值
        :return:
        """
        cache = MyCache(cls.get_table_name())
        o_id = o_id if isinstance(o_id, str) else str(o_id)
        if attr_name not in cls.type_dict:
            pass
        else:
            r = cache.get_value("{}.{}".format(o_id, attr_name))
            return r


    @classmethod
    def get_attr_cls(cls, o_id: ObjectId, attr_name: str, default=None) -> object:
        """
        ｇｅｔ_attr的类方法，带缓存．
        :param o_id:
        :param attr_name:
        :param default:
        :return:
        """
        r = cls.get_attr_from_cache(o_id, attr_name, default)

    @classmethod
    def get_unique_index_info(cls) -> dict:
        """
        获取所有唯一索引信息,这个方法还不完善.暂未使用
        :param ses: 一个ｐｙｍｏｎｇｏ的连接对象
        :return: dict,索引名,索引列名的list组成的字典．
        """
        ses = get_conn(cls.get_table_name())
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
                        elif (type_name.__name__ in ["DBRef", "MyDBRef"]) and not isinstance(v, (DBRef, MyDBRef)):
                            try:
                                temp = MyDBRef(v)
                                self.__dict__[k] = temp
                            except Exception as e:
                                print(e)
                                raise TypeError("{} 不是一个DBRef的实例".format(v))
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
        if "_id" not in self.__dict__:
            self._id = ObjectId()

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

    def check_type(self):
        """检查类的属性是否符合原始设定"""
        if len(self.type_dict) == 0:
            warnings.warn("没有设置字段类型检查")
        else:
            types = self.type_dict.keys()
            for k, v in self.__dict__.items():
                if k in types:
                    if isinstance(v, self.type_dict[k]):
                        pass
                    else:
                        warnings.warn("{}的值{}的类型与设定不符，原始的设定为{}，实际类型为{}".format(k, v, self.type_dict[k], type(v)),
                                      RuntimeWarning)

    def insert(self, obj=None):
        """插入数据库,单个对象,返回ObjectId的实例"""
        obj = self if obj is None else obj
        table_name = obj.table_name()
        ses = get_conn(table_name=table_name)
        insert_dict = {k: v for k, v in obj.__dict__.items() if v is not None}
        try:
            inserted_id = ses.insert_one(insert_dict).inserted_id
            if self._id is None and isinstance(inserted_id, ObjectId):
                self._id = inserted_id
        except errors.DuplicateKeyError as e:
            error_key = ""
            for x in obj.type_dict.keys():
                if x in e.details['errmsg']:
                    error_key = x
                    break
            error_val = obj.__dict__[error_key]
            mes = "重复的 {}:{}".format(error_key, error_val)
            raise ValueError(mes)
        return inserted_id

    def save_plus(self, ignore: list = None) -> bool:
        """
        更新
        :param ignore: 忽略的更新的字段,一般是有唯一性验证的字段
        :return:
        """
        ignore = ["_id"] if ignore is None else ignore
        ses = get_conn(self.table_name())
        doc = self.__dict__
        _id = doc.pop("_id", None)
        doc = {k: v for k, v in doc.items() if k not in ignore}
        f = {"_id": _id}
        res = ses.replace_one(filter=f, replacement=doc, upsert=False)
        return res

    def save(self, obj=None)->ObjectId:
        """更新
        1.如果原始对象不存在，那就插入，返回objectid
        2.如果原始对象存在，那就update。返回objectid
        3.如果遭遇唯一性验证失败，查询重复的对象的，返回0
        4.其他问题会抛出/记录错误,返回None
        return ObjectId
        """
        ms = "此方法已不建议使用,请使用实例方法save_plus和类方法replace_one替代, 2018-3-22"
        warnings.warn(ms)
        obj = self if obj is None else obj
        table_name = obj.table_name()
        ses = get_conn(table_name=table_name)
        save_dict = {k: v for k, v in obj.__dict__.items() if v is not None}
        save_id = None
        try:
            save_id = ses.save(save_dict)
            if self._id is None and isinstance(save_id, ObjectId):
                self._id = save_id
        except pymongo.errors.DuplicateKeyError as e:
            save_id = 0
            ms = "mongo_db.save func Error,原因:重复的对象,detail: {}".format(e)
            logger.info(ms)
        except Exception as e:
            ms = "mongo_db.save func Error,原因:{}".format(e)
            logger.exception(ms)
            raise e
        finally:
            return save_id

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

    def get_dbref(self):
        """获取一个实例的DBRef对象"""
        obj = DBRef(self._table_name, self._id, db_name)
        return obj

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

    def to_flat_dict(self, obj=None):
        """转换成可以json的字典,此方法和同名的独立方法仍在评估中
            to_flat_dict 实例方法.
            to_flat_dict 独立方法
            doc_to_dict  独立方法
            三个方法将在最后的评估后进行统一 2018-3-16
        """
        obj = self if obj is None else obj
        raw_type = obj.type_dict
        data_dict = {k: v for k, v in obj.__dict__.items() if v is not None}
        result_dict = dict()
        for k, v in data_dict.items():
            type_name = '' if raw_type.get(k) is None else raw_type[k].__name__
            if isinstance(v, (DBRef, MyDBRef)):
                temp = {"$id": str(v.id), "$db": v.database, "$ref": v.collection}
                result_dict[k] = temp
            elif isinstance(v, dict):
                temp = dict()
                for k2, v2 in v.items():
                    if isinstance(v2, BaseDoc):
                        temp[k2] = self.to_flat_dict(v2)
                    else:
                        temp[k2] = v2
                result_dict[k] = temp
            elif isinstance(v, list):
                temp = list()
                for x in v:
                    if isinstance(x, BaseDoc):
                        temp.append(self.to_flat_dict(x))
                    elif isinstance(x, DBRef):
                        temp.append(str(x.id))
                    else:
                        temp.append(x)
                result_dict[k] = temp
            elif isinstance(v, BaseDoc):
                result_dict[k] = self.to_flat_dict(v)
            else:
                if isinstance(v, ObjectId):
                    result_dict[k] = str(v)
                elif isinstance(v, DBRef):
                    result_dict[k] = v.as_doc().to_dict()
                elif isinstance(v, datetime.datetime) and type_name == "datetime":
                    result_dict[k] = v.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(v, datetime.datetime) and type_name == "date":
                    result_dict[k] = v.strftime("%Y-%m-%d")
                elif isinstance(v, datetime.date):
                    result_dict[k] = v.strftime("%Y-%m-%d")
                else:
                    result_dict[k] = v

        return result_dict

    @classmethod
    def replace_one(cls, filter_dict: dict, replace_dict: dict, upsert: bool = False) -> bool:
        """
        替换一个文档.
        :param filter_dict: 过滤器
        :param replace_dict:  替换字典
        :param upset: 不存在是否插入?
        :return:
        """
        ses = get_conn(cls.get_table_name())
        res = ses.replace_one(filter=filter_dict, replacement=replace_dict, upsert=upsert)
        return res

    @staticmethod
    def simple_doc(doc_dict: dict, ignore_columns: list = None) -> dict:
        """
        :param doc_dict: 等待被精简的doc,一般是to_flat_dict方法处理过的实例
        :param ignore_columns: 不需要的列名
        :return: 精简过的doc
        """
        ignore_columns = [] if ignore_columns is None else ignore_columns
        result = doc_to_dict(doc_dict, ignore_columns)
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

    def find_one_and_update(self, filter_dict=None, update=None, projection=None, sort=None, upsert=True,
                            return_document="after"):
        """
        找到一个文档然后更新它，如果找不到就插入,尽量使用类方法find_alone_and_update而不要使用本实例方法。
        :param filter_dict: 查找时匹配参数 字典,
        :param update: 更新的数据，字典
        :param projection: 输出限制列  projection={'seq': True, '_id': False} 只输出seq，不输出_id
        :param upsert: 找不到对象时是否插入新的对象 布尔值
        :param sort: 排序列，一个字典的数组
        :param return_document: 返回update之前的文档还是之后的文档？ after 和 before
        :return:  doc或者None
        example:
        filter_dict = {"_id": self.get_id()}
        update_dict = {"$set": {"prev_date": datetime.datetime.now(),
                                "last_query_result_id": last_query_result_id},
                       "$inc": {"online_query_count": 1, "all_count": 1,
                                "today_online_query_count": 1}}
        self.find_one_and_update(filter_dict=filter_dict, update=update_dict)
        """
        if return_document == "after":
            return_document = ReturnDocument.AFTER
        else:
            return_document = ReturnDocument.BEFORE

        """处理filter_dict数据
            如果参数中包含_id参数，那filter_dict={"_id": _id}
            若干阐述中包含_id参数或者为None ，那么filter_dict={"_id": self.get_id()}
        """
        # filter_dict = {k: (get_obj_id(v) if k == "_id" else v) for k, v in filter_dict.items()}
        if filter_dict is None:
            filter_dict = {"_id": self.get_id()}
        else:
            if "_id" in filter_dict:
                # 只依id为准，抛弃其他条件了
                filter_dict = {"_id": get_obj_id(filter_dict['_id'])}
            else:
                filter_dict = {"_id": self.get_id()}
        """处理update数据"""
        if update is None:
            raise ValueError("update参数不能为空")
        else:
            keys = update.keys()
            flag = [k for k in keys if k.startswith("$")]
            if len(flag) > 0:
                """如果用户已经自己定义了$开头的方法"""
                pass
            else:
                update = {"$set": update}
        ses = get_conn(self._table_name)
        print("~~~~~~~~~~~~~~")
        print(filter_dict)
        print(update)
        print("~~~~~~~~~~~~~~")
        result = ses.find_one_and_update(filter=filter_dict, update=update, projection=projection, sort=sort,
                                         return_document=return_document, upsert=upsert)
        return result

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

    def insert_self_and_return_dbref(self):
        """
        把参数转成obj对象插入数据库并返回dbref对象
        return: DBRef
        """
        _id = self.insert()
        if _id is None:
            raise InvalidId("对象插入失败， {}".format(str(self.__dict__)))
        else:
            self._id = _id
            return self.get_dbref()

    def save_self_and_return_dbref(self):
        """
        把参数转成obj对象插入数据库并返回dbref对象,这个是save，对象不存在就插入，对象存在就update
        return: DBRef
        """
        _id = self.save()
        if _id is None:
            raise InvalidId("对象保存失败， {}".format(str(self.__dict__)))
        else:
            self._id = _id
            return self.get_dbref()

    @classmethod
    def get_instance_from_dbref(cls, dbref):
        """
        根据dbref返回一个实例对象
        :param dbref: 一个dbref对象
        :return: dbref对象的collection对应的class的一个实例
        """
        if dbref is None:
            return None
        else:
            table_name = dbref.collection
            object_id = dbref.id
            obj = cls.find_by_id(object_id)
            return obj

    @classmethod
    def insert_and_return_dbref(cls, **kwargs):
        """
        把参数转成obj对象插入数据库并返回dbref对象，如果对象已存在，则返回原始对象的DBRef，
        注意如果建议类构造器不是__init__方法时，你需要在子类中重构此方法。
        :param kwargs: 创建对象的参数
        :return: DBRef
        """
        obj = cls.find_one(**kwargs)
        if isinstance(obj, cls):
            """如果找到一个相同的对象"""
            return obj.get_dbref()
        else:
            obj = cls(**kwargs)
            _id = obj.insert()
            if _id is None:
                raise InvalidId("对象插入失败， {}".format(str(kwargs)))
            else:
                obj._id = _id
                return obj.get_dbref()

    @classmethod
    def insert_and_return_instance(cls, **kwargs):
        """
        把参数转成一个obj对象插入数据库并返回实例f对象
        :param kwargs: 
        :return: cls的实例
        """
        obj = cls(**kwargs)
        _id = obj.insert()
        if _id is None:
            raise InvalidId("对象插入失败， {}".format(str(kwargs)))
        else:
            obj._id = _id
            return obj

    @classmethod
    def insert_one(cls, **kwargs):
        """
        把参数转换为对象并插入
        :param obj: 字典参数
        :return: ObjectId
        """
        instance = None
        try:
            instance = cls(**kwargs)
        except TypeError:
            logger.exception("Error! args: {}".format(str(kwargs)))
        finally:
            if instance is None:
                return instance
            else:
                obj_id = instance.insert()
                return obj_id

    @classmethod
    def insert_many_and_return_doc(cls, input_list: list) -> list:
        """
        retry_insert_many_after_error  的辅助函数,批量插入,并返回成功和失败的结果.
        :param input_list: 待处理的数据ｌｉｓｔ．是ｄｏｃ(有_id的,)．不能是dict或者cls的实例.
        :return: 插入成功的doc的list
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
                try:
                    inserted_results = ses.insert_many(sub, ordered=False)  # 无序写,希望能返回所有出错信息.默认有序
                    success_ids = inserted_results.inserted_ids
                except pymongo.errors.BulkWriteError as e:
                    ms = "insert_many_and_return_doc func Error:{}, args={}".format(e, input_list)
                    logger.info(ms)
                    print(e)
                    duplicate_doc_ids = [x['op']['_id'] for x in e.details['writeErrors']]
                    success_ids = [x["_id"] for x in input_list if x["_id"] not in duplicate_doc_ids]
                except Exception as e1:
                    success_ids = []
                    ms = "retry_insert_many_after_error Error: {}".format(e1)
                    logger.exception(ms)
                finally:
                    res = [x for x in input_list if x['_id'] in success_ids]
                    return_doc.extend(res)
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
    def count(cls, filter_dict: dict, session = None, **kwargs):
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
    def find_by_id(cls, o_id: (str, ObjectId), to_dict: bool = False, can_json: bool = False):
        """查找并返回一个对象，这个对象是o_id对应的类的实例
        :param o_id: _id可以是字符串或者ObjectId
        :param to_dict: 是否转换结果为字典?
        :param can_json: 是否转换结果为可json化的字典?注意如果can_json为真,to_dict参数自动为真
        return cls.instance
        """
        o_id = get_obj_id(o_id)
        ses = get_conn(cls._table_name)
        result = ses.find_one({"_id": o_id})
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
    def find(cls, to_dict: bool = False, **kwargs)->(list, None):
        """根据条件查找对象,返回多个对象的实例
         :param to_dict: True,返回的是字典的数组，False，返回的是实例的数组
         :return : list
        """
        table_name = cls._table_name
        ses = get_conn(table_name=table_name)
        args = dict()
        for k, v in kwargs.items():
            if k == "_id":
                if isinstance(v, str):
                    try:
                        object_id = get_obj_id(v)
                        args[k] = object_id
                    except TypeError as e:
                        print(e)
                        raise TypeError("ObjectId转换失败.val:{}".format(v))
                elif isinstance(v, ObjectId):
                    args[k] = v
                else:
                    raise TypeError("{} 不能转换成ObjectId".format(v))
            else:
                args[k] = v
        result = ses.find(args)
        if result is None:
            return result
        else:
            if to_dict:
                pass
            else:
                result = [cls(**x) for x in result]
            return result

    @classmethod
    def find_plus(cls, filter_dict: dict, sort_dict: dict = None, skip: int = None, limit: int = None,
                  projection: list = None, to_dict: bool = False, can_json=False) -> (list, None):
        """
        find的增强版本,根据条件查找对象,返回多个对象的实例
        :param filter_dict:   过滤器,筛选条件.
        :param sort_dict:     排序字典. 比如: {"time": -1}  # -1表示倒序,注意排序字典参数的处理
        :param skip:          跳过多少记录.
        :param limit:         输出数量限制.
        :param projection:    投影数组,决定输出哪些字段?
        :param to_dict:       True,返回的是字典的数组，False，返回的是实例的数组
        :param can_json:       是否调用to_flat_dict函数转换成可以json的字典?
        :return:
        """
        if can_json:
            to_dict = True
        if sort_dict is not None:
            sort_list = [(k, v) for k, v in sort_dict.items()]  # 处理排序字典.
        else:
            sort_list = None
        table_name = cls._table_name
        ses = get_conn(table_name=table_name)
        args = {
            "filter": filter_dict,
            "sort": sort_list,   # 可能是None,但是没问题.
            "projection": projection,
            "skip": skip,
            "limit": limit
        }
        args = {k: v for k, v in args.items() if v is not None}
        result = ses.find(**args)
        if result is None:
            return result
        else:
            if to_dict:
                if can_json:
                    result = [to_flat_dict(x) for x in result]
                else:
                    result = [x for x in result]
            else:
                result = [cls(**x) for x in result]
            return result

    @classmethod
    def find_one(cls, **kwargs):
        """根据条件查找对象,返回单个对象的实例"""
        table_name = cls._table_name
        ses = get_conn(table_name=table_name)
        args = dict()
        for k, v in kwargs.items():
            if k == "_id":
                if isinstance(v, str):
                    try:
                        object_id = get_obj_id(v)
                        args[k] = object_id
                    except TypeError as e:
                        print(e)
                        raise TypeError("ObjectId转换失败.val:{}".format(v))
                elif isinstance(v, ObjectId):
                    args[k] = v
                else:
                    raise TypeError("{} 不能转换成ObjectId".format(v))
            else:
                args[k] = v
        result = ses.find_one(args)
        if result is None:
            return result
        else:
            return cls(**result)

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
    def find_alone_and_update(cls, filter_dict: dict, update, projection=None, sort=None, upsert=True,
                              return_document="after"):
        """
        找到一个文档然后更新它，如果找不到就插入,这个实例方法的find_one_and_update本质是同一方法。
        :param filter_dict: 查找时匹配参数 字典
        :param update: 更新的数据，字典
        :param projection: 输出限制列  projection={'seq': True, '_id': False} 只输出seq，不输出_id
        :param upsert: 找不到对象时是否插入新的对象 布尔值
        :param sort: 排序列，一个字典的数组
        :param return_document: 返回update之前的文档还是之后的文档？ after 和 before
        :return:  doc或者None
        example:
        filter_dict = {"_id": self.get_id()}
        update_dict = {"$set": {"prev_date": datetime.datetime.now(),
                                "last_query_result_id": last_query_result_id},
                       "$inc": {"online_query_count": 1, "all_count": 1,
                                "today_online_query_count": 1}}
        self.find_one_and_update(filter_dict=filter_dict, update=update_dict)
        """
        if "_id" in filter_dict:
            obj = cls.find_by_id(filter_dict.pop('_id'))
        else:
            obj = cls(**filter_dict)
        res = obj.find_one_and_update(filter_dict=None, update=update, projection=projection, sort=sort,
                                      upsert=upsert, return_document=return_document)
        return res

    @classmethod
    def find_one_and_update_plus(cls, filter_dict: dict, update_dict: dict, projection: list = None, sort_dict: dict = None, upsert: bool = True,
                              return_document: str="after"):
        """
        find_one_and_update和find_alone_and_update的增强版.推荐使用本方法!
        find_one_and_update和find_alone_and_update替更简单医易用.
        本方法更灵活,只是在设置参数时要求更高.
        找到一个文档然后更新它，如果找不到就插入
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
    pass

