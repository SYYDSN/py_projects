#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import render_template
from flask import make_response
from flask import abort
from tools_module import *
import json
from hashlib import md5
from uuid import uuid4
from tools_module import *
from module.teacher_module import *


"""注册蓝图"""
teacher_blueprint = Blueprint("teacher_blueprint", __name__, url_prefix="/teacher", template_folder="templates/")


"""分析师登录，喊单操作的视图函数"""


def version():
    return uuid4().hex


def login() -> str:
    """teacher login page"""
    method = request.method.lower()
    if method == "get":
        page_title = "大师登录"
        return render_template("t_login.html", page_title=page_title)
    elif method == "post":
        phone = get_arg(request, "phone", '')
        pw = get_arg(request, "password", '')
        mes = {"message": "success"}
        if phone == "" or pw == "":
            mes['message'] = "必要参数不能为空"
        else:
            f = {"phone": phone}
            p = ['phone', 'name', 'password']
            t = Teacher.find_one_plus(filter_dict=f, projection=p, instance=False)
            if t is None:
                mes['message'] = "用户不存在"
            else:
                pw = md5(pw.encode(encoding='utf-8')).hexdigest().lower()
                if pw == t.get("password", "").lower():
                    """登录成功"""
                    session['t_id'] = t["_id"]
                    ref = get_arg(request, "ref", "")
                    if ref != "":
                        ref = base64.urlsafe_b64decode(ref).decode()
                        mes['ref'] = ref
                else:
                    mes['message'] = "密码错误"
        return json.dumps(mes)
    else:
        return abort(405)


def login_out():
    """注销"""
    session.pop("t_id")
    return json.dumps({"message": "success"})


def quotation_page():
    """报价页面"""
    page_title = "行情"
    return render_template("quotation.html", page_title=page_title, v=version())


@check_teacher_session
def process_case_page(teacher: dict = None):
    """交易管理"""
    method = request.method.lower()
    if method == "get":
        page_title = "交易管理"
        return render_template("process_case.html", page_title=page_title, teacher=teacher, v=version())
    elif method == "post":
        """
        分析师微信喊单信号。在未整合之前，此类信号一律转交
        Message_Server项目处理 2018-8-28
        """
        args = get_args(request)
        _id = args.get("_id", "")
        if isinstance(_id, str) and len(_id) == 24:
            """这是离场"""
            pass
        else:
            """这是进场"""

    else:
        return abort(405)


"""集中注册函数"""


"""老师登录"""
teacher_blueprint.add_url_rule(rule="/login.html", view_func=login, methods=['get', 'post'])
"""老师注销"""
teacher_blueprint.add_url_rule(rule="/login_out", view_func=login_out, methods=['get', 'post'])
"""报价页面"""
teacher_blueprint.add_url_rule(rule="/quotation.html", view_func=quotation_page, methods=['get', 'post'])
"""交易管理"""
teacher_blueprint.add_url_rule(rule="/process_case.html", view_func=process_case_page, methods=['get', 'post'])

