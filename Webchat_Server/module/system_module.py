# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
from log_module import get_logger


logger = get_logger()
ObjectId = mongo_db.ObjectId


"""
系统用户模块
"""


class Permission(mongo_db.BaseDoc):
    """
    用户权限类
    """


class SystemUser(mongo_db.BaseDoc):
    """
    系统用户类,用户操作后台
    """
    _table_name = "system_user"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['phone'] = str  # 手机号/用户名
    type_dict['password'] = str  # 密码
    type_dict['name'] = str  # 显示的名称
    type_dict['create_date'] = datetime.datetime
