#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from log_module import get_logger
from log_module import recode
import requests
import re
import gc
import time
import json
import datetime
import mongo_db
from module import send_moudle
from module.spread_module import SpreadChannel
from gevent.queue import JoinableQueue
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import FirefoxProfile
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import Firefox
from selenium.webdriver import ChromeOptions
from selenium.webdriver import Chrome
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import By
from pyquery import PyQuery
from mongo_db import get_datetime_from_str
from werkzeug.contrib.cache import RedisCache
from module.transaction_module import Transaction
from module.transaction_module import Withdraw
from gevent.queue import JoinableQueue
from mail_module import send_mail
from threading import Lock


send_signal = send_moudle.send_signal
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
logger = get_logger()
cache = RedisCache()
queue = JoinableQueue()
job_key = "job_list"
cache.delete(job_key)


"""爬虫模块"""


class CustomerManagerRelation(mongo_db.BaseDoc):
    """
    客户和客户经理/总监的对应关系类，用来确认客户归属
    注意这个类是不完整的，缺少必要的方法。
    因为这里只负责记录
    """
    _table_name = 'customer_manager_relation'
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['record_id'] = str  # 简道云提交过来的_id，仅仅在删除信息的时候做对应的判断。
    type_dict['customer_sn'] = int  # 新平台id
    type_dict['create_date'] = datetime.datetime  # 记录的创建时间
    type_dict['update_date'] = datetime.datetime  # 记录的最近一次修改时间
    type_dict['delete_date'] = datetime.datetime  # 记录的删除时间
    type_dict['mt4_account'] = str         # 唯一，但不建立对应的索引，目的是容错。
    type_dict['platform'] = str   # 平台名称
    type_dict['customer_name'] = str
    type_dict['sales_name'] = str
    type_dict['manager_name'] = str
    type_dict['director_name'] = str  # 总监


if __name__ == "__main__":
    """测试获取客户归属"""
    # i_dict = {
    #         "_id" : ObjectId("5ace114bc69abbd345bfa6c2"),
    #         "mt4_account" : 8300144,
    #         "record_id" : "5ace114b214d2c0a6b376269",
    #         "sales_name" : "黄腾飞",
    #         "customer_name" : "赵刚刚",
    #         "platform" : "shengfxchina",
    #         "director_name" : "倪丽娜",
    #         "manager_name" : "吴峰",
    #         "update_date" : get_datetime_from_str("2018-04-12T02:37:10.522Z"),
    #         "create_date" : get_datetime_from_str("2018-04-11T21:44:43.543Z")
    #     }
    # c = CustomerManagerRelation(**i_dict)
    # print(CustomerManagerRelation.get_relation('8300144'))
    pass