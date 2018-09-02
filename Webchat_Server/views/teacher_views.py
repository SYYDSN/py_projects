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
import requests
from hashlib import md5
from uuid import uuid4
from tools_module import *
from module.teacher_module import *
import mongo_db


"""注册蓝图"""
teacher_blueprint = Blueprint("teacher_blueprint", __name__, url_prefix="/teacher", template_folder="templates/")


"""分析师登录，喊单操作的视图函数"""


def version():
    """生成一个随机的版本号"""
    return uuid4().hex


def post_trade(info: dict) -> True:
    """
    发送微信喊单信号给Message_Server,这是一个临时的解决方案.
    将来可能要把处理喊单信号的模块整合进本项目  2018-8-28
    :param info:
    :return:
    """
    u = "http://127.0.0.1:8000/listen_virtual_trade"
    u = "http://wx.yataitouzigl.com/listen_virtual_trade"
    r = requests.post(u, data=info)
    status = r.status_code
    res = True
    if status == 200:
        resp = r.json()
        mes = resp['message']
        if mes == "success":
            print("ok")
        else:
            ms = "Message_Server的listen_virtual_trade接口返回了错误的信息:{}".format(resp)
            logger.exception(ms)
            print(ms)
            res = False
    else:

        ms = "Message_Server的listen_virtual_trade接口返回了错误的响应码:{}".format(status)
        logger.exception(ms)
        print(ms)
        res = False
    return res


def login() -> str:
    """teacher login page"""
    method = request.method.lower()
    if method == "get":
        page_title = "大师登录"
        return render_template("t_login.html", page_title=page_title,v=version())
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
                    if t.get("native"):
                        """登录成功"""
                        session['t_id'] = t["_id"]
                    else:
                        mes['message'] = "此账户无法登录"
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


def news_func():
    """
    新闻页面/系统信息
    :return:
    """
    page_title = "实时新闻"
    return render_template("news.html", page_title=page_title, v=version())


@check_teacher_session
def process_case_page(teacher: dict = None):
    """交易管理"""
    method = request.method.lower()
    if method == "get":
        page_title = "交易管理"
        hold_list = Teacher.get_hold(t_id=teacher['_id'])  # 持仓信息
        return render_template("process_case.html", page_title=page_title, teacher=teacher, hold_list=hold_list,
                               v=version())
    elif method == "post":
        """
        分析师微信喊单信号。在未整合之前，此类信号一律转交
        Message_Server项目处理 2018-8-28
        """
        args = get_args(request)
        args['teacher_id'] = teacher['_id']
        args['teacher_name'] = teacher['name']
        if teacher['native']:
            """真实老师"""
            args['change'] = "raw"
            args['native'] = True
        else:
            args['change'] = 'follow'
            args['native'] = False
        _id = args.get("_id", "")
        if isinstance(_id, str) and len(_id) == 24:
            """这是离场"""
            ses = mongo_db.get_conn(table_name="trade")
            f = {"_id": ObjectId(_id)}
            obj = ses.find_one(filter=f)
            if obj is None:
                return json.dumps({"message": "订单不存在"})
            else:
                args.update(obj)
                args['case_type'] = "exit"
        else:
            """这是进场"""
            args['_id'] = ObjectId()
            args['case_type'] = "enter"
            args['each_profit'] = 0.0
            args['lots'] = 1
            args['native_direction'] = args['direction']
            args['record_id'] = args['_id']
        if post_trade(args):
            mes = {"message": "success"}
        else:
            mes = {"message": "操作失败"}
        return json.dumps(mes)

    else:
        return abort(405)


"""集中注册函数"""


"""老师登录"""
teacher_blueprint.add_url_rule(rule="/login.html", view_func=login, methods=['get', 'post'])
"""老师注销"""
teacher_blueprint.add_url_rule(rule="/login_out", view_func=login_out, methods=['get', 'post'])
"""报价页面"""
teacher_blueprint.add_url_rule(rule="/quotation.html", view_func=quotation_page, methods=['get', 'post'])
"""新闻页面"""
teacher_blueprint.add_url_rule(rule="/news.html", view_func=news_func, methods=['get', 'post'])
"""交易管理"""
teacher_blueprint.add_url_rule(rule="/process_case.html", view_func=process_case_page, methods=['get', 'post'])

