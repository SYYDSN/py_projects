# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
from mongo_db import *


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