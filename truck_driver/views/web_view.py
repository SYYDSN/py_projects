#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import render_template
import json
from tools_module import *
from model.company_module import Company
from model.identity_validate import GlobalSignature
from model.driver_module import DriverResume
from flask import request
from mongo_db import db_name
from mongo_db import DBRef


"""注册蓝图"""
web_blueprint = Blueprint("web_blueprint", __name__, url_prefix="/web", template_folder="templates/web")


"""用于站点部分的视图函数"""


def login_func():
    """登录函数"""
    method = request.method.lower()
    if method == "get":
        """登录页面"""
        return render_template("web/web_login.html")




"""集中注册函数"""


web_blueprint.add_url_rule(rule="/login", view_func=login_func, methods=['get', 'post'])  # 注册
# web_blueprint.add_url_rule(rule="/driver_page", view_func=driver_page_func, methods=['get', 'post'])  # 分页查询司机信息
