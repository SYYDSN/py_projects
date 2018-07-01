#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
import json
from tools_module import *
from model.identity_validate import GlobalSignature
from flask import request


"""注册蓝图"""
identity_blueprint = Blueprint("identity_blueprint", __name__, url_prefix="/identity", template_folder="templates/web")


"""用于进行身份验证,数字签名和签权的视图函数，主要是为分离式前端站点调用"""


def get_signature_func() -> str:
    """
    获取服务器端的数字签名和当前算法,node.js服务器用此两项信息来进行和保驾犬后台的加密通讯
    当前情况下.使用郑宏振的手机号码做sid来换取signature  sid = "18336048620"
    :return:
    """
    mes = {"message": "success"}
    sid = get_arg(request, "sid", "")
    if sid == "18336048620":
        """可以请求signature"""
        data = dict()
        r = GlobalSignature.get_signature()
        data['signature'] = r['signature']
        data['algorithm'] = r['algorithm']
        mes['data'] = data
    else:
        mes['message'] = "未实现请求"
    return json.dumps(mes)


"""集中注册函数"""


identity_blueprint.add_url_rule(rule="/get_signature", view_func=get_signature_func, methods=['get', 'post'])  # 注册
