# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
from mongo_db import *
import datetime


"""
记录交易平台发过来的事件消息的模块
目前记录的事件包含:
1. 提交入金
2. 入金成功
3. 出金处理
4. 待审核客户
"""


class PlatformEvent(BaseDoc):
    """
    交易平台发送来的事件信息.
    """
    _table_name = "platform_event"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['title'] = str
    type_dict['mt4_account'] = str
    type_dict['user_name'] = str
    type_dict['user_parent_name'] = str
    type_dict['order'] = str                 # 出入金单号
    type_dict['money'] = float               # 有符号浮点,
    type_dict['status'] = str
    type_dict['time'] = datetime.datetime    # 事件时间
    type_dict['create_time'] = datetime.datetime    # 创建

    @classmethod
    def instance(cls, **kwargs):
        if "create_time" not in kwargs:
            kwargs['create_time'] = datetime.datetime.now()
        instance = cls(**kwargs)
        return instance


if __name__ == "__main__":
    begin = get_datetime_from_str("2018-7-10 0:0:0")
    end = get_datetime_from_str("2018-7-11 0:0:0")
    f = dict()
    f["time"] = {"$lt": end, "$gte": begin}
    f['title'] = {"$in": ['入金成功', '提交入金']}
    f['title'] = {"$in": ['待审核客户']}
    rs = PlatformEvent.find_plus(filter_dict=f, to_dict=True)
    money = 0
    for x in rs:
        print(x)
        # print(x['title'], x['time'], x['user_parent_name'], x['money'])
        # money += x['money']
    print("{}笔入金,共计:{}".format(len(rs), money))
    pass