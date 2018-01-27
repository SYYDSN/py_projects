# -*- encoding: utf-8 -*-
# 数据库连接模块
__author__ = 'Administrator'

import pymssql, time
import sys


# 返回数据库连接

#def get_conn(host='127.0.0.1', user='sa', password='123456', database='yingxiao_db', charset='utf8'):
def get_conn(host='175.102.7.80', user='sa', password='SHrihui158', database='yingxiao_db', charset='utf8'):
    flag = True
    while flag:
        try:
            conn = pymssql.connect(host=host, user=user, password=password, database=database, charset=charset,timeout=2)
            flag = False
            # print("数据库连接成功")
        except:
            flag = True
            print("数据库连接失败")
            time.sleep(3)
    return conn


