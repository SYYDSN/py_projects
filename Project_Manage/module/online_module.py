# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import pymongo
from mongo_db import to_flat_dict
from mongo_db import get_datetime_from_str
from bson.code import Code
import datetime
from log_module import get_logger


"""此模块专门用于查询保驾犬用户在线人数的相关功能"""


logger = get_logger()
db_user = "eroot"              # 数据库用户名
password = "Try@Ex68769"       # 数据库密码
db_name = "platform_db"        # 库名称
mechanism = "SCRAM-SHA-1"      # 加密方式，注意，不同版本的数据库加密方式不同。
mongodb_setting = {
    # "host": "127.0.0.1:27017",   # 数据库服务器地址            mongos 1
    "host": "safego.org:20000",   # 数据库服务器地址            mongos 1
    # "host": "pltf.safego.org:7171",   # 数据库服务器地址          mongos 2
    # "host": "pltf.safego.org:8181",   # 数据库服务器地址        mongos 3
    "localThresholdMS": 30,  # 本地超时的阈值,默认是15ms,服务器超过此时间没有返回响应将会被排除在可用服务器范围之外
    "maxPoolSize": 20,  # 最大连接池,默认100,不能设置为0,连接池用尽后,新的请求将被阻塞处于等待状态.
    "minPoolSize": 0,  # 最小连接池,默认是0.
    "waitQueueTimeoutMS": 30000,  # 连接池用尽后,等待空闲数据库连接的超时时间,单位毫秒. 不能太小.
    "authSource": db_name,  # 验证数据库
    'authMechanism': mechanism,  # 加密
    "readPreference": "primaryPreferred",  # 读偏好,优先从盘,可以做读写分离,本例从盘不稳定.改为主盘优先
    # "readPreference": "secondaryPreferred",  # 读偏好,优先从盘,读写分离
    "username": db_user,       # 用户名
    "password": password    # 密码
}


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


def get_online_report():
    """获取在线报告"""
    ses = get_conn("gps_info")
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    begin = get_datetime_from_str("{}-{}-1 0:0:0".format(year, month))
    # begin = now - datetime.timedelta(days=30)
    query = {"time": {"$gte": begin}}
    s = {"time": -1}
    out = "online_report_result"  # 保存数据的表,每次map_reduce都会提前清空这个表
    map_func = Code("""
    function(){
        emit(this.user_id.$id, 1);
    }
    """)
    reduce_func = Code("""
    function(key, values){
        return Array.sum(values);
    }
    """)
    result_conn = ses.map_reduce(map=map_func, reduce=reduce_func, query=query, sort=s, out=out, full_response=False)
    res = result_conn.find(filter=dict())
    count_dict = {x['_id']: int(x['value']) for x in res}
    ids = list(count_dict.keys())
    ses = get_conn("user_info")
    f = {"_id": {"$in": ids}}
    s = [("last_update", -1)]
    users = ses.find(filter=f, sort=s)
    res = list()
    for user in users:
        user_id = user['_id']
        temp = to_flat_dict(user)
        temp['count'] = count_dict[user_id]
        res.append(temp)
    res.sort(key=lambda obj: obj['count'], reverse=True)
    return res


def get_online_report2():
    """获取在线报告, 按天切分"""
    ses = get_conn("gps_info")
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    begin = get_datetime_from_str("{}-{}-1 0:0:0".format(year, month))
    # begin = now - datetime.timedelta(days=30)
    query = {"time": {"$gte": begin}}
    s = {"time": -1}
    out = "online_report_result2"  # 保存数据的表,每次map_reduce都会提前清空这个表
    map_func = Code("""
        function(){
            emit(this.time.getDate(), 1);
        }
        """)
    reduce_func = Code("""
        function(key, values){
            return Array.sum(values);
        }
        """)

    result_conn = ses.map_reduce(map=map_func, reduce=reduce_func,  query=query, sort=s, out=out, full_response=False)
    res = result_conn.find(filter=dict())
    res = [x for x in res]

    return res


if __name__ == "__main__":
    get_online_report2()
    pass