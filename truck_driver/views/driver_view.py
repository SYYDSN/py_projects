#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
import json
from flask import request


"""用于站点部分的视图函数"""


def login_func(series: str, **kwargs) -> str:
    """
    登录函数
    :param series: 用于区分不同的登录用户 enterprise/operator/user/admin  企业/运营/一般用户/管理员  默认是enterprise(企业)
    :param kwargs:
    :return:
    """
    mes = {"message": "success"}
    method = request.method.lower()
    if method == "get":
        mes['method'] = method
    return json.dumps(mes)


web_blueprint = Blueprint("manage_blueprint", __name__, url_prefix=None, template_folder="templates/web")


"""集中注册函数"""


web_blueprint.add_url_rule(rule="/login_<series>", view_func=login_func)  # 注册
