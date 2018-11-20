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
from module.system_module import *
from module.file_module import *
import json
import datetime
from orm_module import MyView
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


class LoginView(MyView):
    """登录页面和登录函数"""
    _rule = "/login"
    _allowed = [3]
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
    _allowed = [3]
    _name = "注销"

    def get(self):
        clear_platform_session()
        return redirect(url_for("manage_blueprint.login_func"))

    def post(self):
        return self.get()


class CodeImportView(MyView):
    """条码信息导入页面视图函数"""
    _rule = "/code_import"
    _allowed = [0, 1, 3]
    _name = "条码信息导入"

    @check_session
    def get(self, user: dict):
        """返回条码信息导入界面"""
        render_data['page_title'] = "条码信息导入"
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = self.get_filter(user)

        if isinstance(access_filter, dict):
            page_index = get_arg(request, "index", 1)
            s = {"upload_time": -1}
            result = UploadFile.query(filter_dict=access_filter, page_index=page_index, sort_cond=s)
            files = result['data']
            render_data.update(result)
            render_data['files'] = files
            return render_template("code_import.html", **render_data)
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
        f = self.get_filter(user)
        if f is None:
            pass
        else:
            upload = request.headers.get("upload-file", "0", str)
            if upload == "1":
                """上传文件"""
                p = os.path.join(__project_dir__, "import_data")
                if not os.path.exists(p):
                    os.makedirs(p)
                else:
                    pass
                mes = UploadFile.upload(request, p)
            else:
                """其他操作"""
        return json.dumps(mes)


class ManageProductView(MyView):
    """管理产品信息页面视图函数"""
    _rule = "/product"
    _allowed = [0, 1, 3]
    _name = "产品管理"

    @check_session
    def get(self, user: dict):
        """返回管理用户界面"""
        render_data['page_title'] = "产品管理"
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = self.get_filter(user)

        if isinstance(access_filter, dict):
            page_index = get_arg(request, "index", 1)
            r = Product.query(filter_dict=access_filter, page_index=page_index)  # 产品列表
            products = r.pop("data")
            render_data['products'] = products
            render_data.update(r)
            return render_template("manage_product.html", **render_data)
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
        f = self.get_filter(user)
        if f is None:
            pass
        else:
            req_type = get_arg(request, "type", "")
            if req_type == "add":
                product_name = get_arg(request, "product_name", "")
                specification = get_arg(request, "specification", "")
                net_contents = int(get_arg(request, "net_contents", ""))
                package_ratio = int(get_arg(request, "package_ratio", ""))
                doc = {
                    "product_name": product_name,
                    "specification": specification,
                    "net_contents": net_contents,
                    "package_ratio": package_ratio
                }
                mes = Product.add(**doc)
            elif req_type == "edit":
                _id = ObjectId(get_arg(request, "_id", ""))
                product_name = get_arg(request, "product_name", "")
                specification = get_arg(request, "specification", "")
                net_contents = int(get_arg(request, "net_contents", ""))
                package_ratio = int(get_arg(request, "package_ratio", ""))
                f.update({"_id": _id})
                u = {"$set": {
                    "product_name": product_name,
                    "specification": specification,
                    "net_contents": net_contents,
                    "package_ratio": package_ratio,
                    "last": datetime.datetime.now()
                }}
                Product.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)
                mes['message'] = "success"
            elif req_type == "delete":
                ids = json.loads(get_arg(request, "ids"))
                ids = [ObjectId(x) for x in ids]
                f.update({"_id": {"$in": ids}})
                Product.delete_many(filter_dict=f)
                mes['message'] = "success"
            else:
                mes['message'] = "无效的类型: {}".format(req_type)
        return json.dumps(mes)


class ManageUserView(MyView):
    """管理用户页面视图函数"""
    _rule = "/user"
    _allowed = [0, 1, 3]
    _name = "用户管理"

    @check_session
    def get(self, user: dict):
        """返回管理用户界面"""
        render_data['page_title'] = "用户管理"
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = self.get_filter(user)

        if isinstance(access_filter, dict):
            """不显示管理员用户"""
            access_filter.update({"role_id": {"$ne": ObjectId("5bdfad388e76d6efa7b92d9e")}})
            page_index = get_arg(request, "index", 1)
            r = User.views_info(filter_dict=access_filter, page_index=page_index)  # 用户列表
            users = r.pop("data")
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
        f = self.get_filter(user)
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


class ManageRoleView(MyView):
    """管理权限页面视图函数"""
    _rule = "/role"
    _allowed = [0, 3]
    _name = "权限管理"

    @check_session
    def get(self, user: dict):
        """返回管理权限界面"""
        render_data['page_title'] = "权限管理"
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = self.get_filter(user)
        access_filter.update({"role_name": {"$ne": "root"}})
        page_index = get_arg(request, "index", 1)
        r = Role.views_info(filter_dict=access_filter, page_index=page_index)  # 角色列表
        if r is None:
            return abort(401, "access refused!")
        else:
            roles = r.pop("data")
            render_data['roles'] = roles
            render_data.update(r)
            all_rules = orm_module.FlaskUrlRule.find(filter_dict=dict())  # 所有的访问规则
            render_data['rules'] = all_rules
            return render_template("manage_role.html", **render_data)

    @check_session
    def post(self, user: dict):
        """
        req_type 代表请求的类型, 有4种:
        1. add          添加角色
        2. edit         修改角色
        3. delete       删除角色
        4. rules        根据role的id查询规则
        :param user:
        :return:
        """
        mes = {"message": "access refused"}
        f = self.get_filter(user)
        if f is None:
            pass
        else:
            req_type = get_arg(request, "type", "")
            if req_type == "add":
                rules = json.loads(get_arg(request, "rules"))
                role_name = get_arg(request, "role_name", "")
                now = datetime.datetime.now()
                doc = {
                    "role_name": role_name,
                    "rules": rules,
                    "last": now,
                    "time": now
                }
                mes = Role.add(**doc)
            elif req_type == "rules":
                role_id = get_arg(request, "role_id", "")
                role_id = ObjectId(role_id) if isinstance(role_id, str) and len(role_id) == 24 else role_id
                f.update({"_id": role_id})
                r = Role.find_one(filter_dict=f)
                if "rules" in r:
                    mes['message'] = "success"
                    mes['data'] = r['rules']
                else:
                    mes['message'] = "查询数据失败"
            elif req_type == "edit":
                role_id = ObjectId(get_arg(request, "role_id"))
                rules = json.loads(get_arg(request, "rules"))
                role_name = get_arg(request, "role_name", "")
                f.update({"_id": role_id})
                u = {"$set": {
                    "role_name": role_name,
                    "rules": rules,
                    "last": datetime.datetime.now()
                }}
                Role.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)
                mes['message'] = "success"
            elif req_type == "delete":
                ids = json.loads(get_arg(request, "ids"))
                ids = [ObjectId(x) for x in ids]
                f.update({"_id": {"$in": ids}})
                Role.delete_many(filter_dict=f)
                mes['message'] = "success"
            else:
                mes['message'] = "无效的类型: {}".format(req_type)
        return json.dumps(mes)


"""集中注册视图函数"""
"""登录"""
LoginView.register(manage_blueprint)
"""注销"""
LogoutView.register(manage_blueprint)
"""导入条码页面"""
CodeImportView.register(app=manage_blueprint)
"""管理产品页面"""
ManageProductView.register(app=manage_blueprint)
"""管理用户页面"""
ManageUserView.register(app=manage_blueprint)
"""管理权限页面"""
ManageRoleView.register(app=manage_blueprint)

