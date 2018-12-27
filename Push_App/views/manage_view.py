#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask import request
from flask import Blueprint
from flask import send_from_directory
from flask import flash
from flask import render_template
from flask import abort
from uuid import uuid4
import json
import datetime
from module.items_module import *
from orm_module import MyView
from tools_module import *


""""
对系统进行管理模块.
"""


"""注册蓝图"""
secret_key = uuid4().hex  # 用于通讯的密钥
url_prefix = "/manage"
manage_blueprint = Blueprint("manage_blueprint", __name__, url_prefix=url_prefix, template_folder="templates")
project_name = "后台管理"
render_data = dict()  # 用来渲染的数据
render_data['project_name'] = project_name
"""导航菜单"""
navs = [
    {"name": "消息推送", "path": "/manage/message", "class": "fa fa-exclamation-circle", "children": [
        {"name": "消息推送", "path": "/manage/product"}
    ]}
]


class LoginView(MyView):
    """登录页面和登录函数"""
    _rule = "/login"
    _allowed_view = [3]
    _allowed_delete = []
    _allowed_edit = []
    _endpoint = "login_func"
    _name = "登录"

    def get(self):
        """返回登录页"""
        render_data['page_title'] = "用户登录"
        return render_template("login.html", **render_data)

    def post(self):
        """检查用户登录"""
        user_name = get_arg(request, "user_name", "")
        password = get_arg(request, "password", "")
        mes = User.login(user_name=user_name, password=password)
        if mes['message'] == 'success':
            _id = mes.pop('_id', None)
            session['_id'] = _id
        else:
            pass
        return json.dumps(mes)


class LogoutView(MyView):
    """注销视图"""
    _rule = "/logout"
    _allowed_view = [3]
    _allowed_delete = []
    _allowed_edit = []
    _name = "注销"

    def get(self):
        clear_platform_session()
        return redirect(url_for("manage_blueprint.login_func"))

    def post(self):
        return self.get()


class DownLoadPrintFileView(MyView):
    """下载批量打印的文件函数"""
    _rule = "/print_file/<file_name>"
    _allowed_view = [0, 3]
    _allowed_edit = []
    _allowed_delete = []
    _name = "下载批量打印的文件"

    @check_session
    def get(self, user: dict, file_name: str):
        """
        下载
        :param user:
        :param file_name:
        :return:
        """
        access_filter = self.operate_filter(user=user, operate="view")
        if isinstance(access_filter, dict):
            directory = os.path.join(__project_dir__, "export_data")
            return send_from_directory(directory=directory, filename=file_name, attachment_filename=file_name, as_attachment=True)
        else:
            return abort(403)  # 权限不足


class ManageUserView(MyView):
    """管理用户页面视图函数"""
    _rule = "/user"
    _allowed_view = [0, 1, 3]
    _name = "用户管理"

    @classmethod
    def _get_filter(cls, user_id: ObjectId, access_value: int, operate: str = "view") -> dict:
        """
        根据用户信息和访问级别的值.构建并返回一个用于查询的字典.此函数应该只被cls.identity调用.
        当你重新定义过访问级别的值后.请重构此函数
        :param user_id: 过滤器中的字段,一般是user_id,也可能是其他字段.不同的视图类请重构此函数.
        :param access_value:
        :param operate:
        :return: 返回None表示禁止访问
        """
        res = None
        _access_rules = cls._access_rules
        d = list(_access_rules.keys())
        if access_value not in d:
            ms = "权限值:{} 未被定义".format(access_value)
            raise ValueError(ms)
        else:
            if access_value == 1:
                res = {"_id": user_id}
            elif access_value == 2:
                ms = "未实现的访问级别控制: {}".format(access_value)
                raise NotImplementedError(ms)
            elif access_value == 3:
                res = dict()
            else:
                pass
        return res

    @check_session
    def get(self, user: dict):
        """返回管理用户界面"""
        render_data['page_title'] = "用户管理"
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = self.operate_filter(user)  # 数据访问权
        c = self.check_nav(navs=navs, user=user)  # 导航访问权
        render_data['navs'] = c

        if isinstance(access_filter, dict):
            """不显示管理员用户"""
            access_filter.update({"role_id": {"$ne": ObjectId("5bdfad388e76d6efa7b92d9e")}})
            page_index = get_arg(request, "page", 1)
            r = User.paging_info(filter_dict=access_filter, page_index=page_index)  # 用户列表
            users = r.pop("data", list())
            f = {"_id": {"$ne": ObjectId("5bdfad388e76d6efa7b92d9e")}}
            projection = ["_id", "role_name"]
            roles = Role.find(filter_dict=f, projection=projection)
            render_data['users'] = users
            render_data['roles'] = roles
            render_data.update(r)
            return render_template("manage_user.html", **render_data)
        else:
            return abort(401, "access refused!")

    @check_session
    def post(self, user: dict):
        """
        req_type 代表请求的类型, 有3种:
        1. add          添加用户
        2. edit         修改用户
        3. delete       删除用户
        :param user:
        :return:
        """
        mes = {"message": "access refused"}
        f = self.operate_filter(user)  # 数据访问权
        if f is None:
            pass
        else:
            req_type = get_arg(request, "type", "")
            if req_type == "add":
                nick_name = get_arg(request, "nick_name", "")
                user_name = get_arg(request, "user_name", "")
                status = int(get_arg(request, "status", "1"))
                role_id = ObjectId(get_arg(request, "role_id", ""))
                password = get_arg(request, "password", "")
                doc = {
                    "nick_name": nick_name,
                    "user_name": user_name,
                    "role_id": role_id,
                    "status": status,
                    "password": password
                }
                mes = User.add_user(**doc)
            elif req_type == "edit":
                _id = ObjectId(get_arg(request, "_id", ""))
                nick_name = get_arg(request, "nick_name", "")
                user_name = get_arg(request, "user_name", "")
                status = int(get_arg(request, "status", "1"))
                role_id = ObjectId(get_arg(request, "role_id", ""))
                password = get_arg(request, "password", "")

                f.update({"_id": _id})
                u = {"$set": {
                    "nick_name": nick_name,
                    "user_name": user_name,
                    "role_id": role_id,
                    "status": status,
                    "last": datetime.datetime.now()
                }}
                if password != '':
                    u['$set']['password'] = password
                else:
                    pass
                User.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)
                mes['message'] = "success"
            elif req_type == "delete":
                ids = json.loads(get_arg(request, "ids"))
                ids = [ObjectId(x) for x in ids]
                f.update({"_id": {"$in": ids}})
                User.delete_many(filter_dict=f)
                mes['message'] = "success"
            else:
                mes['message'] = "无效的类型: {}".format(req_type)
        return json.dumps(mes)


class SelfInfoView(MyView):
    """
    查看修改自己的信息
    """
    _rule = "/self_info"
    _allowed_view = [1]
    _name = "个人信息"

    @check_session
    def post(self, user: dict):
        mes = {"message": "success"}
        f = self.operate_filter(user=user)
        req_id = get_arg(request, "_id", "")
        req_id = ObjectId(req_id) if isinstance(req_id, str) and len(req_id) == 24 else req_id
        if user['_id'] == req_id:
            """身份验证正确"""
            the_type = get_arg(request, "type", "")
            if the_type == "change_pw":
                """修改密码"""
                pwd_old = get_arg(request, "pw_old", '')
                pw_n1 = get_arg(request, "pw_n1", '')
                pw_n2 = get_arg(request, "pw_n2", '')
                mes = User.change_pw(u_id=req_id, pwd_old=pwd_old, pw_n1=pw_n1, pw_n2=pw_n2)
            elif the_type == "change_nick":
                """修改昵称"""
                nick_name = get_arg(request, "nick_name", '')
                f = {"_id": req_id}
                u = {"$set": {"nick_name": nick_name}}
                r = User.find_one_and_update(filter_dict=f, update_dict=u)
            else:
                mes['message'] = "错误的操作:{}".format(the_type)
        else:
            mes['message'] = "权限不足"
        return json.dumps(mes)


"""集中注册视图函数"""

"""登录"""
LoginView.register(manage_blueprint)
"""注销"""
LogoutView.register(manage_blueprint)
"""下载批量打印的文件函数"""
DownLoadPrintFileView.register(app=manage_blueprint)
"""管理用户页面"""
ManageUserView.register(app=manage_blueprint)
"""查看修改自己的信息"""
SelfInfoView.register(app=manage_blueprint)

