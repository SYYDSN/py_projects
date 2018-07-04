#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import request
from flask import abort
from flask import render_template
import json
from bson.objectid import ObjectId
from tools_module import *
from module.identity_validate import GlobalSignature
from module.item_module import RawRequestInfo
from module.document_tools import markdown_to_html


"""接受mt4后台推送过来的信息2018-6-29"""


"""注册蓝图"""
mt4_blueprint = Blueprint("mt4_blueprint", __name__, url_prefix="/mt4", template_folder="templates/mt4")


"""用于站点部分的视图函数"""


def index_func() -> str:
    """
    首页的函数,hello world!
    :return:
    """
    return "hello world!, 1 am mt4 server."


def md_view():
    """md文档视图"""
    if request.method.lower() == "get":
        sid = get_arg(request, "sid", "")
        if sid == "bbb5fd48094942be80dbf0467be3d6f6":
            content = markdown_to_html()
            return render_template("md.html", content=content)
        else:
            return abort(404)
    else:
        return abort(405)


def secret_func(key) -> str:
    """
    获取服务器端的数字签名和当前算法,node.js服务器用此两项信息来进行和保驾犬后台的加密通讯
    当前情况下.使用sid来换取signature  sid = "bbb5fd48094942be80dbf0467be3d6f6"
    :return:
    """
    mes = {"message": "success"}
    if key == "get":
        """获取签名和算法"""
        sid = get_arg(request, "sid", "")
        if sid == "bbb5fd48094942be80dbf0467be3d6f6":
            """可以请求signature"""
            data = dict()
            r = GlobalSignature.get_signature()
            data['signature'] = r['signature']
            data['algorithm'] = r['algorithm']
            data['expire'] = r['expire']
            mes['data'] = data
        else:
            mes['message'] = "未实现请求"
    else:
        mes = "未实现"
    return json.dumps(mes)


def mes_func(key) -> str:
    """
    消息的处理函数.接受交易平台推送过来的信息.
    典型的url:
    /mt4/message/push
    :param key: 动词 push/get/delete/update
    :return:
    """
    mes = {"message": "success"}
    if key == "push":
        """推送数据"""
        oid = RawRequestInfo.record(req=request)
        mes['mid'] = str(oid)
    elif key == "get":
        mid = request.args.get("mid", "")
        if mid == "":
            mes['message'] = "mid必须"
        elif isinstance(mid, str) and len(mid) == 24:
            f = {"_id": ObjectId(mid)}
            one = RawRequestInfo.find_one_plus(filter_dict=f, instance=False, can_json=True)
            mes['data'] = one
        else:
            mes['message'] = "错误的mid格式"
    else:
        mes = "未实现"
    return json.dumps(mes)


"""集中注册函数"""


mt4_blueprint.add_url_rule(rule="/", view_func=index_func, methods=['get', 'post'])  # hello world
mt4_blueprint.add_url_rule(rule="/api", view_func=md_view, methods=['get'])  # api
mt4_blueprint.add_url_rule(rule="/secret/<key>", view_func=index_func, methods=['get', 'post'])  # 获取签名和算法
mt4_blueprint.add_url_rule(rule="/message/<key>", view_func=mes_func, methods=['get', 'post'])  # 接收平台消息
