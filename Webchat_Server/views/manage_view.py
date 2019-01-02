#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask import request
from flask import make_response
from flask import Blueprint
from flask import send_from_directory
from flask import flash
from flask import render_template
from flask import abort
from uuid import uuid4
import json
import datetime
from mongo_db import MyView
from module.admin_module import *
from module.trade_module import *
from module.trade_module import Teacher
from tools_module import *
from bson.son import SON
from collections import OrderedDict
import warnings


""""
对系统进行操作模块.
"""


"""注册蓝图"""
secret_key = uuid4().hex  # 用于通讯的密钥
url_prefix = "/manage"
manage_blueprint = Blueprint("manage_blueprint", __name__, url_prefix=url_prefix, template_folder="templates/manage")
project_name = "微信公众号后台"
render_data = dict()  # 用来渲染的数据
render_data['project_name'] = project_name
"""导航菜单"""
navs = [
    {
        "name": "交易管理", "path": "/manage/trade_history", "class": "fa fa-cogs", "children":
            [
                {"name": "交易历史", "path": "/manage/trade_history"}
            ]
    },
    {
        "name": "系统管理", "path": "/manage/user",  "class": "fa fa-bar-chart", "children":
        [
            {"name": "权限组管理", "path": "/manage/role"},
            {"name": "用户管理", "path": "/manage/user"}
        ]
    }
]


class LoginView(MyView):
    """管理员登录页面和登录函数"""
    _rule = "/login"
    _allowed_view = [3]
    _allowed_delete = []
    _allowed_edit = []
    _endpoint = "login_func"
    _name = "登录"

    def get(self):
        """返回登录页"""
        render_data['page_title'] = "管理员登录"
        return render_template("manage/login.html", **render_data)

    def post(self):
        """检查管理员登录"""
        user_name = get_arg(request, "user_name", "")
        password = get_arg(request, "password", "")
        mes = Admin.login(user_name=user_name, password=password)
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

    @check_admin_session
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

    @check_admin_session
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

    @check_admin_session
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


class ManageTradeView(MyView):
    """交易管理视图函数"""
    _access_rules = OrderedDict()  # 定义访问级别
    _access_rules[0] = "禁止访问"
    _access_rules[1] = "允许操作"
    _rule = "/trade_<key>"
    _allowed_view = [0, 1]
    _name = "交易管理"

    """
    注意:
    trade表中有大量的没有the_profit的离场单,并且case_type字段没有的离场单也很多. 都暂时忽略.
    现阶段case_type是必须的,case_type==exit是离场单,the_profit>=0 是胜单
    """

    @classmethod
    def _get_filter(cls, user: dict, access_value: int, operate: str = "view") -> dict:
        """
        根据用户信息和访问级别的值.构建并返回一个用于查询的字典.此函数应该只被cls.identity调用.
        当你重新定义过访问级别的值后.请重构此函数.注意,你可以根据operate的类型不同,分别针对类型去重构过滤器.
        :param user: 用户信息字典.不同的视图类请重构此函数.
        :param access_value:
        :param operate:  权限的类型 分为 view/edit/delete  查看/编辑/删除
        :return: 返回None表示禁止访问
        """
        ms = "已重新定义过权限范围过滤器"
        warnings.warn(message=ms)
        res = None
        d = cls.get_rules(operate=operate)
        if access_value not in d:
            ms = "权限值:{} 未被定义".format(access_value)
            raise ValueError(ms)
        else:
            if access_value == 1:
                res = dict()
            else:
                pass
        return res

    @check_admin_session
    def get(self, admin: dict, key):
        """返回条码信息导出界面"""
        render_data['cur_user'] = admin  # 当前用户,这个变量名要保持不变
        access_filter = self.operate_filter(admin)   # 数据访问权
        render_data['navs'] = self.check_nav(navs=navs, user=admin)  # 导航访问权

        if isinstance(access_filter, dict):
            if key == "history":
                """交易历史"""
                render_data['page_title'] = "交易历史"
                selector = Teacher.selector_data()
                render_data['selector'] = selector
                page_index = get_arg(request, "page", 1)
                page_size = get_arg(request, "size", 15)
                begin = None
                try:
                    begin = mongo_db.get_datetime_from_str(get_arg(request, "begin", None))
                except Exception as e:
                    print(e)
                end = None
                try:
                    end = mongo_db.get_datetime_from_str(get_arg(request, "end", None))
                except Exception as e:
                    print(e)
                kw = dict()
                case_type = get_arg(request, "case_type", '')
                if case_type == "":
                    pass
                else:
                    kw['case_type'] = case_type
                teacher_id = ObjectId(get_arg(request, "teacher_id", '')) if get_arg(request, "teacher_id", '') != "" else get_arg(request, "teacher_id", '')
                if isinstance(teacher_id, ObjectId):
                    kw['teacher_id'] = teacher_id
                else:
                    t_ids = [x["_id"] for x in selector]
                    kw['teacher_id'] = {"$in": t_ids}
                if case_type == "":
                    """看全部"""
                    if isinstance(begin, datetime.datetime):
                        kw['enter_time'] = {"$gte": begin}
                        if isinstance(end, datetime.datetime):
                            kw['exit_time'] = {"$lte": end}
                        else:
                            pass
                    else:
                        if isinstance(end, datetime.datetime):
                            kw['exit_time'] = {"$lte": end}
                        else:
                            pass
                elif case_type == "enter":
                    """只看持仓的"""
                    if isinstance(begin, datetime.datetime):
                        temp = {"$gte": begin}
                        if isinstance(end, datetime.datetime):
                            temp['$lte'] = end
                            kw['enter_time'] = temp
                        else:
                            pass
                    else:
                        if isinstance(end, datetime.datetime):
                            kw['enter_time'] = {"$lte": end}
                        else:
                            pass
                else:
                    """只看离场的"""
                    if isinstance(begin, datetime.datetime):
                        temp = {"$gte": begin}
                        if isinstance(end, datetime.datetime):
                            temp['$lte'] = end
                            kw['exit_time'] = temp
                        else:
                            pass
                    else:
                        if isinstance(end, datetime.datetime):
                            kw['exit_time'] = {"$lte": end}
                        else:
                            pass
                only_win = get_arg(request, "only_win", '-1')
                try:
                    only_win = int(only_win)
                except Exception as e:
                    print(e)
                    only_win = -1
                finally:
                    if only_win == 1:
                        """只看胜场"""
                        kw['the_profit'] = {
                            "$exists": True,
                            "$gte": 0
                        }
                    elif only_win == 0:
                        """只看负场"""
                        kw['the_profit'] = {
                            "$exists": True,
                            "$lt": 0
                        }
                    else:
                        pass

                access_filter.update(kw)
                result = Trade.paging_info(filter_dict=access_filter, page_size=page_size, page_index=page_index)
                preview = Trade.preview(filter_dict=access_filter)
                render_data['preview'] = preview
                trades = result['data']
                render_data.update(result)
                render_data['trades'] = trades
                current_rule = self.current_rule_value(role_id=admin['role_id'], operate="delete")
                render_data['allowed_delete'] = 1 if self.is_root(user=admin) else current_rule
                return render_template("manage/trade_history.html", **render_data)
            else:
                return abort(404)
        else:
            return abort(401, "access refused!")

    @check_admin_session
    def post(self, key: str, admin: dict):
        """
        req_type 代表请求的类型, 有2种:
        1. reverse         反转交易
        2. delete          删除交易
        :param key: 这个参数目前没有,主要是和路由规则保持一致
        :param admin:
        :return:
        """
        mes = {"message": "access refused"}
        f = self.operate_filter(admin)  # 数据访问权
        if f is None:
            pass
        else:
            the_type = get_arg(request, "type", "")
            if the_type == "reverse":
                """反转交易方向"""
                ids = []
                try:
                    ids = json.loads(get_arg(request, "ids"))
                except Exception as e:
                    print(e)
                finally:
                    if len(ids) == 0:
                        mes['message'] = "没有发现需要反转的交易"
                    else:
                        ids = [ObjectId(x) for x in ids]
                        handler = admin['_id']
                        mes = Trade.batch_reverse(ids=ids, handler=handler)
            elif the_type == "delete":
                """批量删除交易"""
                rule = self.current_rule_value(role_id=admin['role_id'], operate="delete")
                if rule == 1:
                    ids = []
                    try:
                        ids = json.loads(get_arg(request, "ids"))
                    except Exception as e:
                        print(e)
                    finally:
                        if len(ids) == 0:
                            mes['message'] = "没有发现需要删除的交易"
                        else:
                            ids = [ObjectId(x) for x in ids]
                            handler = admin['_id']
                            mes = Trade.batch_delete(ids=ids, handler=handler)
                else:
                    mes['message'] = "权限不足"
            else:
                mes['message'] = "无效的操作类型:{}".format(the_type)
        return json.dumps(mes)


class ManageUserView(MyView):
    """管理用户页面视图函数"""
    _rule = "/user"
    _allowed_view = [0, 1, 3]
    _name = "用户管理"

    @classmethod
    def _get_filter(cls, user: dict, access_value: int, operate: str = "view") -> dict:
        """
        根据用户信息和访问级别的值.构建并返回一个用于查询的字典.此函数应该只被cls.identity调用.
        当你重新定义过访问级别的值后.请重构此函数
        :param user: 用户信息字典.不同的视图类请重构此函数.
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
                res = {"_id": user['_id']}
            elif access_value == 2:
                ms = "未实现的访问级别控制: {}".format(access_value)
                raise NotImplementedError(ms)
            elif access_value == 3:
                res = dict()
            else:
                pass
        return res

    @check_admin_session
    def get(self, admin: dict):
        """返回管理用户界面"""
        render_data['page_title'] = "用户管理"
        render_data['cur_user'] = admin  # 当前用户,这个变量名要保持不变
        access_filter = self.operate_filter(admin)  # 数据访问权
        c = self.check_nav(navs=navs, user=admin)  # 导航访问权
        render_data['navs'] = c

        if isinstance(access_filter, dict):
            """不显示管理员用户"""
            access_filter.update({"role_id": {"$ne": ObjectId("5bdfad388e76d6efa7b92d9e")}})
            page_index = get_arg(request, "page", 1)
            r = Admin.paging_info(filter_dict=access_filter, page_index=page_index)  # 用户列表
            users = r.pop("data", list())
            f = {"_id": {"$ne": ObjectId("5bdfad388e76d6efa7b92d9e")}}
            projection = ["_id", "role_name"]
            roles = AdminRole.find(filter_dict=f, projection=projection)
            render_data['users'] = users
            render_data['roles'] = roles
            render_data.update(r)
            return render_template("manage/manage_user.html", **render_data)
        else:
            return abort(401, "access refused!")

    @check_admin_session
    def post(self, admin: dict):
        """
        req_type 代表请求的类型, 有3种:
        1. add          添加用户
        2. edit         修改用户
        3. delete       删除用户
        :param admin:
        :return:
        """
        mes = {"message": "access refused"}
        f = self.operate_filter(admin)  # 数据访问权
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
                mes = Admin.add_user(**doc)
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
                Admin.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)
                mes['message'] = "success"
            elif req_type == "delete":
                ids = json.loads(get_arg(request, "ids"))
                ids = [ObjectId(x) for x in ids]
                f.update({"_id": {"$in": ids}})
                Admin.delete_many(filter_dict=f)
                mes['message'] = "success"
            else:
                mes['message'] = "无效的类型: {}".format(req_type)
        return json.dumps(mes)


class ManageRoleView(MyView):
    """管理权限页面视图函数"""
    _rule = "/role"
    _allowed_view = [0, 3]
    _name = "权限管理"

    @check_admin_session
    def get(self, admin: dict):
        """返回管理权限界面"""
        render_data['page_title'] = "权限管理"
        render_data['cur_user'] = admin  # 当前用户,这个变量名要保持不变
        access_filter = self.operate_filter(admin)  # 数据访问权
        render_data['navs'] = self.check_nav(navs=navs, user=admin)  # 导航访问权
        if access_filter is None:
            return abort(401)
        else:
            access_filter.update({"role_name": {"$ne": "root"}})
            page_index = get_arg(request, "page", 1)
            r = AdminRole.paging_info(filter_dict=access_filter, page_index=page_index)  # 角色列表
            roles = r.pop("data", list())
            render_data['roles'] = roles
            render_data.update(r)
            all_rules = orm_module.FlaskUrlRule.find(filter_dict=dict())  # 所有的访问规则
            render_data['rules'] = all_rules
            return render_template("manage/manage_role.html", **render_data)

    @check_admin_session
    def post(self, admin: dict):
        """
        req_type 代表请求的类型, 有4种:
        1. add          添加角色
        2. edit         修改角色
        3. delete       删除角色
        4. rules        根据role的id查询规则
        :param admin:
        :return:
        """
        mes = {"message": "access refused"}
        f = self.operate_filter(admin)  # 数据访问权
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
                mes = AdminRole.add(**doc)
            elif req_type == "rules":
                role_id = get_arg(request, "role_id", "")
                role_id = ObjectId(role_id) if isinstance(role_id, str) and len(role_id) == 24 else role_id
                f.update({"_id": role_id})
                r = AdminRole.find_one(filter_dict=f)
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
                AdminRole.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)
                mes['message'] = "success"
            elif req_type == "delete":
                ids = json.loads(get_arg(request, "ids"))
                ids = [ObjectId(x) for x in ids]
                f.update({"_id": {"$in": ids}})
                AdminRole.delete_many(filter_dict=f)
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

    @check_admin_session
    def post(self, admin: dict):
        mes = {"message": "success"}
        f = self.operate_filter(user=admin)
        req_id = get_arg(request, "_id", "")
        req_id = ObjectId(req_id) if isinstance(req_id, str) and len(req_id) == 24 else req_id
        if admin['_id'] == req_id:
            """身份验证正确"""
            the_type = get_arg(request, "type", "")
            if the_type == "change_pw":
                """修改密码"""
                pwd_old = get_arg(request, "pw_old", '')
                pw_n1 = get_arg(request, "pw_n1", '')
                pw_n2 = get_arg(request, "pw_n2", '')
                mes = Admin.change_pw(u_id=req_id, pwd_old=pwd_old, pw_n1=pw_n1, pw_n2=pw_n2)
            elif the_type == "change_nick":
                """修改昵称"""
                nick_name = get_arg(request, "nick_name", '')
                f = {"_id": req_id}
                u = {"$set": {"nick_name": nick_name}}
                r = Admin.find_one_and_update(filter_dict=f, update_dict=u)
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
"""交易管理"""
ManageTradeView.register(app=manage_blueprint)
"""管理用户页面"""
ManageUserView.register(app=manage_blueprint)
"""管理权限页面"""
ManageRoleView.register(app=manage_blueprint)
"""查看修改自己的信息"""
SelfInfoView.register(app=manage_blueprint)

