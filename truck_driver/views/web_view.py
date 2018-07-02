#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import render_template
from flask import abort
import json
from tools_module import *
from bson.regex import Regex
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
    elif method == "post":
        mes = {"message": "success"}
        user_name = request.form.get("user_name", None)
        user_password = request.form.get("user_password", None)
        if user_name and user_password:
            r = Company.login(user_name=user_name, user_password=user_password, can_json=False)
            if r['message'] == "success":
                save = {"user_name": user_name, "user_password": user_password, "user_id": r['data']['_id']}
                save_platform_session(**save)
            else:
                mes = r
        else:
            mes['message'] = "用户名或密码必须"
        return json.dumps(mes)
    else:
        return abort(405)


def driver_page_func():
    """
    分页显示页面信息
    :return:
    """
    url_path = request.path  # 当前web路径
    q = dict()
    keywords = request.args.get("kw", "")  # 搜索关键词
    keywords = keywords.strip()
    if keywords == "":
        pass
    else:
        keywords = [x.strip() for x in keywords.split(" ") if x.strip() != ""]
        if len(keywords) == 0:
            pass
        else:
            r = list()
            r.extend([{"phone": {"$regex": Regex("\S*{}\S*".format(x))}} for x in keywords])
            q['$or'] = r
    index = request.args.get("index", "1")  # 第几页
    try:
        index = int(index)
    except Exception as e:
        index = 1
    resumes = DriverResume.query_by_page(filter_dict=q)
    return render_template("web/drivers.html", url_path=url_path, total=resumes['total'], resumes=resumes['data'])




"""集中注册函数"""


"""注册"""
web_blueprint.add_url_rule(rule="/login", view_func=login_func, methods=['get', 'post'])
"""分页查询司机信息"""
web_blueprint.add_url_rule(rule="/drivers", view_func=driver_page_func, methods=['get', 'post'])
