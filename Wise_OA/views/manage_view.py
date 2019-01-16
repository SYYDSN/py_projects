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
from tools_module import *


""""
系统管理员视图模块
"""


"""注册蓝图"""
secret_key = uuid4().hex  # 用于通讯的密钥
url_prefix = "/manage"
manage_blueprint = Blueprint("manage_blueprint", __name__, url_prefix=url_prefix, template_folder="templates")
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
        # {"name": "生产线", "path": "/manage/device_line"},
        # {"name": "嵌入式", "path": "/manage/device_embed"}
    ]},
    {"name": "条码信息", "path": "/manage/code_tools", "class": "fa fa-qrcode", "children": [
        {"name": "条码信息导入", "path": "/manage/code_import"},
        {"name": "提取打印条码", "path": "/manage/code_export"},
        {"name": "导出查询替换", "path": "/manage/code_pickle"},
    ]},
    {"name": "生产任务", "path": "/manage/task_summary", "class": "fa fa-server", "children": [
        # {"name": "生产任务概况", "path": "/manage/task_summary"},  # 暂时不用
        {"name": "生产任务列表", "path": "/manage/task_manage"},
        {"name": "条码回传记录", "path": "/manage/task_sync"}
    ]},
    {"name": "系统管理", "path": "/manage/user",  "class": "fa fa-bar-chart", "children": [
        {"name": "权限组管理", "path": "/manage/role"},
        {"name": "用户管理", "path": "/manage/user"}
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


class DownLoadSyncFileView(MyView):
    """下载任务执行回传的文件函数"""
    _rule = "/sync_file/<file_name>"
    _allowed_view = [0, 3]
    _allowed_edit = []
    _allowed_delete = []
    _name = "下载任务执行回传的文件"

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
            directory = os.path.join(__project_dir__, "task_sync")
            return send_from_directory(directory=directory, filename=file_name, attachment_filename=file_name,
                                       as_attachment=True)
        else:
            return abort(403)  # 权限不足


class DownLoadOutputFileView(MyView):
    """下载生产完成的导出文件函数"""
    _rule = "/output_file/<file_name>"
    _allowed_view = [0, 3]
    _allowed_edit = []
    _allowed_delete = []
    _name = "下载生产完成的导出文件"

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
            directory = os.path.join(__project_dir__, "output_code")
            return send_from_directory(directory=directory, filename=file_name, attachment_filename=file_name,
                                       as_attachment=True)
        else:
            return abort(403)  # 权限不足


class CodeInfoView(MyView):
    """查询/替换条码信息"""
    _rule = "/code_info"
    _allowed_view = [0, 3]
    _allowed_edit = [0, 3]
    _allowed_delete = []
    _name = "查询/替换条码信息"

    @check_session
    def post(self, user: dict):
        """
        :param user:
        :return:
        """
        mes = {"message": "success"}
        the_type = get_arg(request, "type", "")
        _id = get_arg(request, "_id", "")
        _id = _id if _id else get_arg(request, "old_id", "")
        if isinstance(_id, str) and len(_id) > 18:
            if the_type == "query":
                """查询条码信息"""
                access_filter = self.operate_filter(user=user, operate="view")
                if isinstance(access_filter, dict):
                    access_filter.update({"_id": _id})
                    code = CodeInfo.find_info(filter_dict=access_filter, can_json=True)
                    mes['data'] = code
                else:
                    mes['message'] = "401"
            elif the_type == "replace":
                """替换条码"""
                access_filter = self.operate_filter(user=user, operate="edit")
                if isinstance(access_filter, dict):
                    new_id = get_arg(request, "new_id", "")
                    mes = CodeInfo.replace_info(_id, new_id)
                else:
                    mes['message'] = "401"
            elif the_type == "reset":
                """重置条码"""
                access_filter = self.operate_filter(user=user, operate="edit")
                if isinstance(access_filter, dict):
                    access_filter.update({"_id": _id})
                    mes = CodeInfo.reset_info(filter_dict=access_filter)
                else:
                    mes['message'] = "401"
            else:
                mes['message'] = '404'
        else:
            mes['message'] = "没有_id参数"

        return json.dumps(mes)


class CodePickleView(MyView):
    """导出生产条码视图函数"""
    _rule = "/code_pickle"
    _allowed_view = [0, 3]
    _name = "导出生产条码"

    @check_session
    def get(self, user: dict):
        """导出生产条码视图界面"""
        render_data['page_title'] = "导出生产条码"
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = self.operate_filter(user)   # 数据访问权
        render_data['navs'] = self.check_nav(navs=navs, user=user)  # 导航访问权
        base_info = CodeInfo.preview()
        render_data['base_info'] = base_info
        if isinstance(access_filter, dict):
            page_index = get_arg(request, "page", 1)
            s = {"upload_time": -1}
            selector = Product.selector_data()
            render_data['selector'] = selector
            result = OutputCode.paging_info(filter_dict=access_filter, page_index=page_index, sort_cond=s)
            data = result.pop("data", list())
            render_data.update(result)
            render_data['files'] = data
            return render_template("code_pickle.html", **render_data)
        else:
            return abort(401, "access refused!")

    @check_session
    def post(self, user: dict):
        """
        req_type 代表请求的类型, 有3种:
        1. add          添加产品
        2. edit         修改产品
        3. delete       删除产品
        :param user:
        :return:
        """
        mes = {"message": "access refused"}
        f = self.operate_filter(user)  # 数据访问权
        if f is None:
            pass
        else:
            the_type = get_arg(request, "type", "")
            if the_type == "count":
                """统计可导出条码余量"""
                mes['message'] = "success"
                p_id = get_arg(request, "product_id", None)
                p_id = ObjectId(p_id)
                mes['count'] = CodeInfo.can_output(product_id=p_id)
            elif the_type == "export":
                """生成导出文件"""
                p_id = get_arg(request, "product_id", None)
                number = int(get_arg(request, "number", "0"))
                p_id = ObjectId(p_id)
                mes = OutputCode.export(product_id=p_id, number=number)
            elif the_type == "cancel":
                """撤销导出条码操作"""
                ids = []
                try:
                    ids = json.loads(get_arg(request, "ids"))
                except Exception as e:
                    print(e)
                finally:
                    if len(ids) == 0:
                        mes['message'] = "没有需要撤销的文件记录"
                    else:
                        ids = [ObjectId(x) for x in ids]
                        mes = OutputCode.cancel_data(f_ids=ids)
            elif the_type == "delete":
                """批量删除文件和日志"""
                ids = []
                try:
                    ids = json.loads(get_arg(request, "ids"))
                except Exception as e:
                    print(e)
                finally:
                    if len(ids) == 0:
                        mes['message'] = "没有发现需要删除的文件"
                    else:
                        ids = [ObjectId(x) for x in ids]
                        include_record = get_arg(request, "include_record")
                        mes = OutputCode.delete_file_and_record(ids=ids, include_record=include_record)

            else:
                mes['message'] = "无效的操作类型:{}".format(the_type)
        return json.dumps(mes)


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
"""下载文件"""
DownLoadPrintFileView.register(app=manage_blueprint)
"""查看修改自己的信息"""
SelfInfoView.register(app=manage_blueprint)

