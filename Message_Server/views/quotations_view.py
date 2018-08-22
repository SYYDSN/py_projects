#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import abort
from flask import render_template
import json
from bson.objectid import ObjectId
from tools_module import *
from mail_module import send_mail


"""接受行情服务器推送过来的信息2018-8-7,此视图仅做测试用，有正式的行情服务器"""


"""注册蓝图"""
quotations_blueprint = Blueprint("quotations_blueprint", __name__, url_prefix="/quotations", template_folder="templates/quotations")


"""用于站点部分的视图函数"""


def index_func() -> str:
    """
    首页的函数,hello world!
    :return:
    """
    return "hello world!, 1 am quotations server."


def listen_func() -> str:
    """
    行情报价的处理函数.接受交易平台推送过来的实时报价.
    典型的url:
    """

    headers = request.headers
    mes = {"message": "success"}
    headers = {k.lower(): (v.lower() if isinstance(v, str) else v) for k, v in headers.items()}
    auth_req = headers.get("x-auth", "")
    auth_str = "274e9735e2c94d60bd903e45c96fc3b6"
    # if auth_str != auth_req:
    #     return abort(404)
    # else:
    #     mes = {"message": "success"}
    return json.dumps(mes)
    


"""集中注册函数"""


quotations_blueprint.add_url_rule(rule="/", view_func=index_func, methods=['get', 'post'])  # hello world
quotations_blueprint.add_url_rule(rule="/listen", view_func=listen_func, methods=['get', 'post'])  # 接收实时行情
