#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
import json
from tools_module import *
from model.company_module import Company
from flask import request


"""注册蓝图"""
web_blueprint = Blueprint("web_blueprint", __name__, url_prefix="/web", template_folder="templates/web")


"""用于站点部分的视图函数"""


def login_func(series: str, **kwargs) -> str:
    """
    登录函数
    :param series: 用于区分不同的登录用户 company/operator/driver/admin  企业/运营/司机用户/管理员  默认是company(公司)
    :param kwargs: 备用参数
    :return:
    """
    mes = {"message": "success"}
    method = request.method.lower()
    if method == "get":
        """测试接口可用"""
        mes['method'] = method
    else:
        """登录接口"""
        user_name = get_arg(request, "user_name", "")
        user_password = get_arg(request, "user_password", "")
        if user_name == "" or user_password == "":
            mes['message'] = "用户名或密码不能为空"
        else:
            """看看是什么类型登录?"""
            if series == 'company':
                return Company.login(user_name=user_name, user_password=user_password)
            else:
                mes['message'] = "功能未实现"
    return json.dumps(mes)


"""集中注册函数"""


web_blueprint.add_url_rule(rule="/login_<series>", view_func=login_func, methods=['get', 'post'])  # 注册
