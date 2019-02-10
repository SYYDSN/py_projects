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

""""
对系统进行管理模块.
"""

"""注册蓝图"""
url_prefix = "/oauth/v1.0/"
oauth_blueprint = Blueprint("oauth_blueprint", __name__, url_prefix=url_prefix, template_folder="templates")


class LoginView(MethodView):
    """登录页面和登录函数"""

    def get(self, *args, **kwargs):
        return self.post()

    def post(self):
        """检查用户登录"""
        mes = {"message": "success"}
        user_name = get_arg(request, "user_name", "")
        password = get_arg(request, "password", "")
        mes = User.login(user_name=user_name, password=password)
        if mes['message'] == 'success':
            _id = mes.pop('_id', None)
            session['_id'] = _id
        else:
            pass
        return json.dumps(mes)


class LogoutView(MethodView):
    """注销视图"""

    def get(self):
        return self.post()

    def post(self):
        return json.dumps({"message": "success"})


"""集中注册视图函数"""

"""登录"""
manage_blueprint.add_url_rule(rule="/login", view_func=LoginView.as_view(name="login_func"), methods=['get', 'post'])
"""注销"""
manage_blueprint.add_url_rule(rule="/logout", view_func=LogoutView.as_view(name="logout_func"), methods=['get', 'post'])
