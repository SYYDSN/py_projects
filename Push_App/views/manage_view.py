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
    {"name": "设备管理", "path": "/manage/device_list", "class": "fa fa-exclamation-circle", "children": [
        {"name": "设备列表", "path": "/manage/device_list"}
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


class UploadView(MyView):
    """上传图片/文件视图"""
    _rule = "upload/<file_type>"
    _allowed_view = [0, 3]
    _allowed_edit = []
    _allowed_delete = []
    _name = "上传文件"

    @check_session
    def get(self, user: dict):
        """
        上传
        :param user:
        :param file_name:
        :return:
        """
        access_filter = self.operate_filter(user=user, operate="view")
        if isinstance(access_filter, dict):
            directory = os.path.join(__project_dir__, "export_data")
            return send_from_directory(directory=directory, filename=file_name, attachment_filename=file_name,
                                       as_attachment=True)
        else:
            return abort(403)  # 权限不足

    def post(self, user: dict):
        return self.get(uer=user)


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


class ManagePhoneView(MyView):
    """管理设备视图函数"""
    _rule = "/device_<key>"
    _allowed_view = [0, 3]
    _name = "设备管理"

    @check_session
    def get(self, user: dict, key:  str):
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = self.operate_filter(user)  # 数据访问权
        c = self.check_nav(navs=navs, user=user)  # 导航访问权
        render_data['navs'] = c
        if isinstance(access_filter, dict):
            """允许访问的用户"""
            if key == "list":
                """设备列表"""
                render_data['page_title'] = "设备列表"
                page_index = get_arg(request, "page", 1)
                info = Device.paging_info(filter_dict=access_filter, page_index=page_index)
                phones = info.pop("data", list())
                render_data.update(info)
                render_data['phones'] = phones
                prev_icon = last_icon()  # 上一次使用的图标
                render_data['prev_icon'] = prev_icon
                return render_template("phone_list.html", **render_data)
            else:
                return abort(404)
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
"""管理移动设备页面"""
ManagePhoneView.register(app=manage_blueprint)
"""查看修改自己的信息"""
SelfInfoView.register(app=manage_blueprint)

