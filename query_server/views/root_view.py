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
from module.system_module import Root
import json
import datetime
from tools_module import *


""""
管理员模块,用于:
1. 添加账户
2. 设置权限
"""


"""注册蓝图"""
root_blueprint = Blueprint("root_blueprint", __name__, url_prefix="/root", template_folder="templates/root")


def login_func():
    """管理员登录页面"""
    method = request.method.lower()
    if method == 'get':
        """返回登录页"""
        return render_template("root/root_login.html", page_title="管理员登录")
    elif method == 'post':
        """检查登录函数"""
        user_name = get_arg(request, "user_name", "")
        password = get_arg(request, "password", "")
        mes = Root.login(user_name=user_name, password=password)
        if mes['message'] == 'success':
            _id = mes.pop('_id', None)
            session['_id'] = _id
        else:
            pass
        return json.dumps(mes)
    else:
        return abort(405)


@check_root_session
def common_func(root: Root = None, file_name: str = ''):
    """
    通用视图
    :param root: 管理员对象
    :param file_name:  访问的html文件名,带不带html后缀都可以
    :return:
    """
    method = request.method.lower()
    if root is None:
        return abort(401)
    elif file_name == '':
        return abort(404, 'file name is null')
    elif method not in ['get', 'post']:
        return abort(405)
    elif method == 'get':
        """返回页面"""
        file_path = os.path.join(__project_dir__, 'templates', 'root')
        if file_name.endswith(".html"):
            pass
        else:
            file_name = "{}.html".format(file_name)
        files = os.listdir(file_path)
        files = [x for x in files if x not in ['root_login.html']]
        if file_name in files:
            kws = dict()
            if file_name == "manage_user.html":
                kws['page_title'] = "用户管理"
            else:
                pass
            template = "root/{}".format(file_name)
            return render_template(template, **kws)
        else:
            return abort(404, "not found '{}'".format(file_name))
    else:
        mes = {"message": "success"}
        return json.dumps(mes)


"""集中注册视图函数"""
"""登录"""
root_blueprint.add_url_rule(rule="/login", view_func=login_func, methods=['get', 'post'])
"""通用页面解析"""
root_blueprint.add_url_rule(rule="/common/<file_name>", view_func=common_func, methods=['get', 'post'])
