#  -*- coding: utf-8 -*-
import os
import sys

__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask import request
from flask import Blueprint
from flask.views import MethodView
from flask import send_from_directory
from flask import flash
from flask import render_template
from flask import abort
from uuid import uuid4
import json
import datetime
from flask_cors import cross_origin
from toolbox.tools_module import *
from authorization_package.employee_module import Employee
from authorization_package.authorization_tools import *
from authorization_package.rpc_client import RPC

""""
对系统进行管理模块.
"""

"""注册蓝图"""
url_prefix = "/oauth/"
oauth_blueprint = Blueprint("oauth_blueprint", __name__, url_prefix=url_prefix, template_folder="templates")


class LoginView(MethodView):
    """登录页面和登录函数"""

    def get(self, version):
        return self.post(version=version)

    def post(self, version):
        """检查用户登录"""
        checked = RPC.check_request(request)
        mes = {"message": "success"}
        login_type = get_arg(request, "login_type", "page")
        if version == "1.0":
            """oauth 1.0"""
            if login_type == "page":
                """网页的账户和密码登录"""
                user_name = get_arg(request, "user_name", "")
                password = get_arg(request, "password", "")
                hotel_id = get_arg(request, "hotel_id", 1)
                mes = Employee.account_login(hotel_id=hotel_id, user_name=user_name, password=password)
            else:
                """未实现的登录方式"""
                mes['message'] = "未实现的登录方式"
            if mes['message'] == 'success':
                user_id = mes['user_id']
                role_id = mes['role_id']
                mes.update(encode_1(user_id=user_id, role_id=role_id))
            else:
                pass
        elif version == "2.0":
            """oauth 2.0"""
            mes['message'] = "未实现"
        else:
            mes['message'] = "无效的协议"
        return checked.after(response=mes)


class LogoutView(MethodView):
    """注销视图"""

    def get(self):
        return self.post()

    def post(self):
        return json.dumps({"message": "success"})


"""集中注册视图函数"""

"""登录"""
oauth_blueprint.add_url_rule(rule="/v<version>/user/user_login", view_func=LoginView.as_view(name="login_func"), methods=['get', 'post'])
"""注销"""
oauth_blueprint.add_url_rule(rule="/v<version>/user/user_logout", view_func=LogoutView.as_view(name="logout_func"), methods=['get', 'post'])
