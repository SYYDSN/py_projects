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
from module.push_module import *
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


class ImageView(MyView):
    """查看/上传图片视图"""
    _rule = "/image/<key>"
    _allowed_view = [0, 3]
    _allowed_edit = []
    _allowed_delete = []
    _name = "上传文件"

    def get(self, key: str):
        """
        :param key:
        :return:
        """
        user_id = session.get("_id")
        if isinstance(user_id, ObjectId):
            user = User.find_by_id(o_id=user_id, to_dict=True)
        else:
            user = None
        access_filter = user if user is None else self.operate_filter(user=user, operate="view")
        if key == "view":
            """
            查看图片,无权限要求
            """

            fid = get_arg(request, "fid", "")
            directory = IMAGE_DIR
            r = UploadImageHistory.find_by_id(o_id=fid, to_dict=True)
            if isinstance(r, dict):
                file_name = r['storage_name']
                return send_from_directory(directory=directory, filename=file_name,
                                           attachment_filename=file_name, as_attachment=True)
            else:
                return abort(404)
        elif key == "upload":
            """上传图片"""
            if isinstance(access_filter, dict):
                mes = UploadImageHistory.upload(req=request)
                return json.dumps(mes)
            else:
                return abort(403)
        else:
            return abort(403)

    def post(self, key: str):
        return self.get(key=key)


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
                start_args = StartArgs.find_one(filter_dict=dict(), sort=[("time", -1)])
                if start_args is None:
                    start_args = {"delay": "", "img_url": "", "redirect": ""}

                else:
                    pass
                render_data.update(start_args)
                return render_template("phone_list.html", **render_data)
            else:
                return abort(404)
        else:
            return abort(401, "access refused!")

    @check_session
    def post(self, key: str, user: dict):
        """
        req_type 代表请求的类型, 有3种:
        1. push_message          推送消息
        2. delete_device         删除设备
        3. start_args            设置启动参数
        :param key: 用于匹配路由,防止抛出异常
        :param user:
        :return:
        """
        mes = {"message": "access refused"}
        f = self.operate_filter(user)  # 数据访问权
        if f is None:
            pass
        else:
            req_type = get_arg(request, "type", "")
            if req_type == "push_message":
                """推送消息"""
                ids = []
                try:
                    ids = json.loads(get_arg(request, "ids"))
                except Exception as e:
                    print(e)
                finally:
                    if len(ids) == 0:
                        mes['message'] = "设备id不能为空"
                    else:
                        title = get_arg(request, "title", "")
                        alert = get_arg(request, "alert", "")
                        url = get_arg(request, "url", "")
                        kw = {
                            "title": title,
                            "alert": alert,
                            "url": url,
                            "tags": {"registration_id": ids}
                        }
                        mes = push_mes(**kw)
            elif req_type == "delete_device":
                """删除设备"""
                ids = []
                try:
                    ids = json.loads(get_arg(request, "ids"))
                except Exception as e:
                    print(e)
                finally:
                    if len(ids) == 0:
                        mes['message'] = "设备id不能为空"
                    else:
                        mes = Device.batch_delete(ids=ids)
            elif req_type == "start_args":
                """设置启动参数"""
                delay = get_arg(request, "delay", "1")
                try:
                    delay = int(delay)
                except Exception as e:
                    print(e)
                    delay = 1
                finally:
                    img_url = get_arg(request, "img_url", "")
                    redirect_url = get_arg(request, "redirect", "")
                    doc = {
                        "delay": delay,
                        "redirect": redirect_url,
                        "img_url": img_url,
                        "time": datetime.datetime.now()
                    }
                    r = StartArgs.insert_one(doc=doc)
                    if isinstance(r, ObjectId):
                        mes['message'] = "success"
                    else:
                        mes['message'] = "保存失败"
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
ImageView.register(app=manage_blueprint)
"""管理移动设备页面"""
ManagePhoneView.register(app=manage_blueprint)
"""查看修改自己的信息"""
SelfInfoView.register(app=manage_blueprint)

