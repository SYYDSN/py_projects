# -*-coding:utf-8-*-
import pymongo


db_name = "my_db"


def get_conn(table_name, db_name=db_name):
    """
    获取一个针对table_name对应的表的的连接，一般用户对数据库进行增删查改等操作。
    :param table_name: collection的名称，对应sql的表名。必须。
    :param db_name: database的名称，默认是platform_db，建议不要传递这个参数
    :return: 一个Collection对象，用于操作数据库。
    """
    if table_name is None or table_name == '':
        raise TypeError("表名不能为空")
    else:
        mongodb_conn = pymongo.MongoClient()
        conn = mongodb_conn[db_name][table_name]
        return conn