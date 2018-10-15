#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask import Blueprint
import json
import datetime


""""
管理员模块,用于:
1. 添加账户
2. 设置权限
"""


"""注册蓝图"""
image_blueprint = Blueprint("root_blueprint", __name__, url_prefix="/root", template_folder="templates/root")


