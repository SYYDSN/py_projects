#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask import request
from flask import Blueprint
from flask import render_template
from flask import abort
from module.system_module import User
import json
import datetime
from flask.views import MethodView
from tools_module import *


""""
对系统进行操作模块.
"""


"""注册蓝图"""
manage_blueprint = Blueprint("manage_blueprint", __name__, url_prefix="/manage", template_folder="templates")
project_name = "生产线条码管理系统"
render_data = dict()  # 用来渲染的数据
render_data['project_name'] = project_name
"""导航菜单"""
navs = [
    {"name": "产品信息", "path": "/manage/product", "class": "fa fa-exclamation-circle", "children": [
        {"name": "基本信息管理", "path": "/manage/product"}
    ]},
    {"name": "设备信息", "path": "/manage/device", "class": "fa fa-cogs", "children": [
        {"name": "设备信息一览", "path": "/manage/device_summary"},
        {"name": "生产线", "path": "/manage/device_line"},
        {"name": "嵌入式", "path": "/manage/device_embed"}
    ]},
    {"name": "条码信息", "path": "/manage/code_summary", "class": "fa fa-qrcode", "children": [
        {"name": "条码信息概要", "path": "/manage/code_summary"},
        {"name": "条码信息导入", "path": "/manage/code_import"},
        {"name": "条码信息导出", "path": "/manage/code_export"},
        {"name": "提取印刷条码", "path": "/manage/code_pick"},
        {"name": "条码数据同步", "path": "/manage/code_sync"},
        {"name": "查询条码信息", "path": "/manage/code_query"},
    ]},
    {"name": "生产任务", "path": "/manage/task_summary", "class": "fa fa-server", "children": [
        {"name": "生产任务概况", "path": "/manage/task_summary"},
        {"name": "生产任务列表", "path": "/manage/task_list"}
    ]},
    {"name": "系统管理", "path": "/manage/user",  "class": "fa fa-bar-chart", "children": [
        {"name": "权限组管理", "path": "/manage/role"},
        {"name": "用户管理", "path": "/manage/user"}
    ]}
]
render_data['navs'] = navs


def login_func():
    """用户登录页面"""
    method = request.method.lower()
    if method == 'get':
        """返回登录页"""
        render_data['page_title'] = "用户登录"
        return render_template("login.html", **render_data)
    elif method == 'post':
        """检查登录函数"""
        user_name = get_arg(request, "user_name", "")
        password = get_arg(request, "password", "")
        mes = User.login(user_name=user_name, password=password)
        if mes['message'] == 'success':
            _id = mes.pop('_id', None)
            session['_id'] = _id
        else:
            pass
        return json.dumps(mes)
    else:
        return abort(405)


class LogoutView(MethodView):
    """注销视图"""
    def get(self):
        clear_platform_session()
        return redirect(url_for("manage_blueprint.login_func"))

    def post(self):
        return self.get()


class ManageUserView(MethodView):
    """管理用户页面视图函数"""
    @check_session
    def get(self, user: User):
        """返回管理用户界面"""
        render_data['page_title'] = "用户管理"
        rule = request.path.lower()
        method = request.method.lower()
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = User.get_access_filter(user=user, rule=rule, method=method)
        r = User.views_info(filter_dict=access_filter)  # 用户列表
        users = r.pop("data")
        users = users * 12
        render_data['users'] = users
        render_data.update(r)
        return render_template("manage_user.html", **render_data)


# def common_func(root: User = None, file_name: str = ''):
#     """
#     通用视图 此函数闲置不用.
#     :param root: 用户对象
#     :param file_name:  访问的html文件名,带不带html后缀都可以
#     :return:
#     """
#     method = request.method.lower()
#     if root is None:
#         return abort(401)
#     elif file_name == '':
#         return abort(404, 'file name is null')
#     elif method not in ['get', 'post']:
#         return abort(405)
#     elif method == 'get':
#         """返回页面"""
#         file_path = os.path.join(__project_dir__, 'templates', 'root')
#         if file_name.endswith(".html"):
#             pass
#         else:
#             file_name = "{}.html".format(file_name)
#         files = os.listdir(file_path)
#         files = [x for x in files if x not in ['root_login.html']]
#         if file_name in files:
#             kws = dict()
#             if file_name == "manage_user.html":
#                 kws['page_title'] = "用户管理"
#             else:
#                 pass
#             template = "root/{}".format(file_name)
#             return render_template(template, **kws)
#         else:
#             return abort(404, "not found '{}'".format(file_name))
#     else:
#         mes = {"message": "success"}
#         return json.dumps(mes)


"""集中注册视图函数"""
"""登录"""
manage_blueprint.add_url_rule(rule="/login", view_func=login_func, methods=['get', 'post'])
"""注销"""
manage_blueprint.add_url_rule(
    rule="/logout", view_func=LogoutView.as_view(name="logout_view"), methods=['get', 'post']
)
"""管理用户页面"""
manage_blueprint.add_url_rule(
    rule="/user", view_func=ManageUserView.as_view(name="user_view"), methods=['get', 'post']
)
