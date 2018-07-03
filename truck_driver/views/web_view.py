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
    q = dict()  # 查询条件
    keywords = request.args.get("keywords", "")  # 搜索关键词
    keywords = keywords.strip()
    if keywords == "":
        pass
    else:
        keywords = [x.strip() for x in keywords.split(" ") if x.strip() != ""]
        if len(keywords) == 0:
            pass
        else:
            """填充搜索条件,匹配其他表的字段先忽视,因为那需要一个检索服务器,比如elasticsearch"""
            or_list = list()
            """匹配简历的字段"""
            fields = ["living_place", "address", "email"]  # 模糊匹配字段
            for word in keywords:
                for field in fields:
                    t = {field: {"$regex": Regex("\S*{}\S*".format(word))}}
                    or_list.append(t)
            q['$or'] = or_list
    now = datetime.datetime.now()
    """从业年限"""
    i_exp = request.args.get("i_exp", "")
    if i_exp == "":
        pass
    else:
        try:
            i_exp = int(i_exp)
        except Exception as e:
            print(e)
    if isinstance(i_exp, int) and i_exp > 0:
        i_exp = now + datetime.timedelta(days=365 * i_exp)
        q['rtqc_first_date'] = {"$lte": i_exp}
    """工作经验"""
    work_exp = request.args.get("work_exp", "")
    if work_exp == "":
        pass
    else:
        try:
            work_exp = int(work_exp)
        except Exception as e:
            print(e)
    if isinstance(work_exp, int) and work_exp > 0:
        work_exp = now + datetime.timedelta(days=365 * i_exp)
        q['first_work_date'] = {"$lte": work_exp}
    """驾龄"""
    driving_exp = request.args.get("driving_exp", "")
    if driving_exp == "":
        pass
    else:
        try:
            driving_exp = int(driving_exp)
        except Exception as e:
            print(e)
    if isinstance(driving_exp, int) and driving_exp > 0:
        driving_exp = now + datetime.timedelta(days=365 * i_exp)
        q['dl_first_date'] = {"$lte": driving_exp}
    """发布时间"""
    update_date = request.args.get("update_date", "")
    times = ['today', 'three_day', 'week', 'month', 'three_month', 'half_year']
    if update_date in times:
        if update_date == "today":
            delta = datetime.timedelta(days=1)
        elif update_date == "three_day":
            delta = datetime.timedelta(days=3)
        elif update_date == "week":
            delta = datetime.timedelta(days=7)
        elif update_date == "month":
            """不精确,暂时这样"""
            delta = datetime.timedelta(days=30)
        elif update_date == "three_month":
            delta = datetime.timedelta(days=90)
        else:
            delta = datetime.timedelta(days=181)
        q['update_date'] = {"$gte": now - delta}
    """当前状态"""

    index = request.args.get("index", "1")  # 第几页
    try:
        page_index = int(index)
    except Exception as e:
        print(e)
        page_index = 1
    r = DriverResume.query_by_page(filter_dict=q)
    return render_template("web/drivers.html", url_path=url_path, resumes=r['data'], total_record=r['total_record'],
                           total_page=r['total_page'], pages=r['pages'], page_index=page_index)




"""集中注册函数"""


"""注册"""
web_blueprint.add_url_rule(rule="/login", view_func=login_func, methods=['get', 'post'])
"""分页查询司机信息"""
web_blueprint.add_url_rule(rule="/drivers", view_func=driver_page_func, methods=['get', 'post'])
