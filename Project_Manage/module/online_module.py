# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
from log_module import get_logger


"""此模块专门用于查询保驾犬用户在线人数的相关功能"""


logger = get_logger()
db_user = "eroot"              # 数据库用户名