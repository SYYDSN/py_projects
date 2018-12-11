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
from module.system_module import *
from module.file_module import *
from module.code_module import set_code_length
from module.code_module import CodeInfo
from uuid import uuid4
import json
import datetime
from orm_module import MyView
from tools_module import *


""""
对系统进行操作模块.
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
        {"name": "导出打印条码", "path": "/manage/code_export"},
        {"name": "导出生产条码", "path": "/manage/code_pickle"},
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
        if the_type == "query":
            """查询条码信息"""
            _id = get_arg(request, "_id", "")
            if isinstance(_id, str) and len(_id) == 24:
                _id = ObjectId(_id)
                f = {"_id": _id}
                code = CodeInfo.find_info(filter_dict=f)
            else:
                mes['message'] = "没有_id参数"

        elif the_type == "replace":
            """替换条码"""
            pass
        elif the_type == "reset":
            """重置条码"""
            pass
        else:
            mes['message'] = '404'
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
                        mes = PrintCode.cancel_data(f_ids=ids)
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
                        mes = PrintCode.delete_file_and_record(ids=ids, include_record=include_record)

            else:
                mes['message'] = "无效的操作类型:{}".format(the_type)
        return json.dumps(mes)


class CodeImportView(MyView):
    """条码信息导入页面视图函数"""
    _rule = "/code_import"
    _allowed_view = [0, 3]
    _name = "条码信息导入"

    @check_session
    def get(self, user: dict):
        """返回条码信息导入界面"""
        render_data['page_title'] = "条码信息导入"
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
            result = UploadFile.paging_info(filter_dict=access_filter, page_index=page_index, sort_cond=s)
            disk_import_file = UploadFile.all_file_name()  # 获取磁盘上的所有文件名
            files = result['data']
            render_data.update(result)
            render_data['files'] = files
            render_data['disk_import_file'] = disk_import_file
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
        f = self.operate_filter(user)  # 数据访问权
        if f is None:
            pass
        else:
            upload = request.headers.get("upload-file", "0", str)
            if upload == "1":
                """上传文件"""
                mes = UploadFile.upload(request)
            else:
                the_type = get_arg(request, "type", "")
                if the_type == "cancel":
                    """撤销导入条码操作"""
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
                            mes = UploadFile.cancel_data(f_ids=ids)
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
                            mes = UploadFile.delete_file_and_record(ids=ids, include_record=include_record)

                else:
                    mes['message'] = "无效的操作类型:{}".format(the_type)
        return json.dumps(mes)


class CodeExportView(MyView):
    """条码信息导入页面视图函数"""
    _rule = "/code_export"
    _allowed_view = [0, 3]
    _name = "条码信息导入"

    @check_session
    def get(self, user: dict):
        """返回条码信息导出界面"""
        render_data['page_title'] = "条码信息导出"
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
            result = PrintCode.paging_info(filter_dict=access_filter, page_index=page_index, sort_cond=s)
            files = result['data']
            render_data.update(result)
            render_data['files'] = files
            return render_template("code_export.html", **render_data)
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
                """统计条码余量"""
                mes['message'] = "success"
                p_id = get_arg(request, "product_id", None)
                p_id = ObjectId(p_id)
                mes['count'] = CodeInfo.deposit(product_id=p_id)
            elif the_type == "export":
                """生成导出文件"""
                p_id = get_arg(request, "product_id", None)
                number = int(get_arg(request, "number", "0"))
                p_id = ObjectId(p_id)
                mes = PrintCode.export(product_id=p_id, number=number)
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
                        mes = PrintCode.cancel_data(f_ids=ids)
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
                        mes = PrintCode.delete_file_and_record(ids=ids, include_record=include_record)

            else:
                mes['message'] = "无效的操作类型:{}".format(the_type)
        return json.dumps(mes)


class ProduceTaskView(MyView):
    """生产任务管理的视图函数"""
    _rule = "/task_<key>"
    _allowed_view = [0, 3]
    _name = "生产任务管理"

    @check_session
    def get(self, user: dict, key):
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = self.operate_filter(user)  # 数据访问权
        render_data['navs'] = self.check_nav(navs=navs, user=user)  # 导航访问权
        base_info = ProduceTask.task_summary()
        render_data['base_info'] = base_info  # 生产任务概况
        if key == "manage":
            """返回生产任务管理界面"""
            render_data['page_title'] = "生产任务管理"
            if isinstance(access_filter, dict):
                page_index = get_arg(request, "page", 1)
                selector = Product.selector_data()
                render_data['selector'] = selector
                result = ProduceTask.paging_info(filter_dict=access_filter, page_index=page_index)
                tasks = result['data']
                render_data.update(result)
                render_data['tasks'] = tasks
                return render_template("produce_task.html", **render_data)
            else:
                return abort(401, "access refused!")
        elif key == "summary":
            """生产任务概况,暂时不用"""
            render_data['page_title'] = "生产任务概况"
            return render_template("task_summary.html", **render_data)
        elif key == "sync":
            """任务同步/条码回传"""
            render_data['page_title'] = "条码同步记录"
            sync_data = TaskSync.paging_info(filter_dict=access_filter)
            sync_list = sync_data.pop("data", [])
            render_data.update(sync_data)
            render_data['sync_list'] = sync_list
            f = {"status": 1}
            p = ['_id', "batch_sn"]
            tasks = ProduceTask.find(filter_dict=f, projection=p)
            render_data['tasks'] = tasks
            return render_template("task_sync.html", **render_data)
        else:
            return abort(404)

    @check_session
    def post(self, user: dict, key):
        """
        req_type 代表请求的类型, 有3种:
        1. add          添加任务
        2. edit         修改任务
        3. delete       删除任务
        4. start_task       开始任务
        5. stop_task       停止任务
        :param user:
        :return:
        """
        mes = {"message": "access refused"}
        f = self.operate_filter(user)  # 数据访问权
        if f is None:
            pass
        else:
            if key == "manage":
                the_type = get_arg(request, "type", "")
                product_id = ObjectId(get_arg(request, "product_id", None))
                batch_sn = get_arg(request, "batch_sn", "")
                plan_number = int(get_arg(request, "plan_number", "0"))
                if the_type == "add":
                    """新建任务"""
                    args = {
                        "batch_sn": batch_sn,
                        "plan_number": plan_number,
                        "create": datetime.datetime.now(),
                        "status": 0,
                        "product_id": product_id
                    }
                    r = ProduceTask.insert_one(doc=args)
                    if isinstance(r, ObjectId):
                        mes['message'] = "success"
                    else:
                        mes['message'] = "插入失败"
                elif the_type == "edit":
                    """编辑任务"""
                    _id = ObjectId(get_arg(request, "_id", None))
                    args = {
                        "batch_sn": batch_sn,
                        "plan_number": plan_number,
                        "create": datetime.datetime.now(),
                        "status": 0,
                        "product_id": product_id
                    }
                    u = {"$set": args}
                    f = {"_id": _id}
                    r = ProduceTask.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)
                    if isinstance(r, dict):
                        mes['message'] = "success"
                    else:
                        mes['message'] = "插入失败"
                elif the_type == "start_task":
                    """开始任务"""
                    _id = ObjectId(get_arg(request, "_id", None))
                    f = {"_id": _id}
                    task = ProduceTask.find_one(filter_dict=f)
                    if isinstance(task.get("begin"), datetime.datetime):
                        args = {
                            "status": 1,
                            "end": None
                        }
                    else:
                        args = {
                            "status": 1,
                            "begin": datetime.datetime.now()
                        }
                    u = {"$set": args}
                    r = ProduceTask.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)
                    if isinstance(r, dict):
                        mes['message'] = "success"
                    else:
                        mes['message'] = "操作失败"
                elif the_type == "stop_task":
                    """停止任务"""
                    _id = ObjectId(get_arg(request, "_id", None))
                    f = {"_id": _id}
                    args = {
                        "status": 0,
                        "end": datetime.datetime.now()
                    }
                    u = {"$set": args}
                    r = ProduceTask.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)
                    if isinstance(r, dict):
                        mes['message'] = "success"
                    else:
                        mes['message'] = "操作失败"
                elif the_type == "delete":
                    """批量删除任务"""
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
                            mes = ProduceTask.delete_tasks(ids=ids)

                else:
                    mes['message'] = "无效的操作类型:{}".format(the_type)
            elif key == "summary":
                """"""
                pass
            elif key == "sync":
                """条码回传记录的操作"""
                the_type = get_arg(request, "type", "")
                if the_type == "edit":
                    """关联和重新关联生产任务"""
                    _id = ObjectId(get_arg(request, "_id", None))
                    task_id = get_arg(request, "task_id", None)
                    task_id = ObjectId(task_id) if isinstance(task_id, str) and len(task_id) == 24 else task_id
                    task_id = task_id if isinstance(task_id, ObjectId) else None
                    if task_id is None or _id is None:
                        mes['message'] = '参数错误'
                    else:
                        mes = TaskSync.relate_task(sync_id=_id, task_id=task_id)
                elif the_type == "cancel":
                    """清除已回传的条码"""
                    ids = []
                    try:
                        ids = json.loads(get_arg(request, "ids"))
                    except Exception as e:
                        print(e)
                    finally:
                        if len(ids) == 0:
                            mes['message'] = "没有发现需要取消的作业"
                        else:
                            ids = [ObjectId(x) for x in ids]
                            mes = TaskSync.cancel_data(ids=ids)
                elif the_type == "delete":
                    """删除回传的文件和日志"""
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
                            mes = TaskSync.delete_file_and_record(ids=ids, include_record=True)
                else:
                    mes['message'] = "无效的操作类型:{}".format(the_type)
            else:
                mes['message'] = "unknown error"
        return json.dumps(mes)


class ManageCompanyView(MyView):
    """公司信息"""
    _rule = "/company"
    _allowed_view = [3]
    _allowed_edit = []   # 任何人都不能编辑,除了管理员
    _allowed_delete = []  # 任何人都不能删除,除了管理员
    _name = "公司信息"

    @check_session
    def post(self, user: dict):
        """对公司信息的操作(只有添加和编辑)"""
        mes = {"message": "access refused"}
        if self.is_root(user):
            _id = get_arg(request, "_id", "")   # 公司id
            company_name = get_arg(request, "company_name", "")  # 公司名称
            doc = {"company_name": company_name}
            _id = ObjectId(_id) if isinstance(_id, str) and len(_id) == 24 else _id
            inventory_threshold = get_arg(request, "inventory_threshold", None)   # 库存条码下限
            printed_threshold = get_arg(request, "printed_threshold", None)      # 已打印的可用条码下限
            try:
                doc['inventory_threshold'] = int(inventory_threshold)
            except Exception as e:
                print(e)
            try:
                doc['printed_threshold'] = int(printed_threshold)
            except Exception as e:
                print(e)
            code_length = get_arg(request, "code_length", "")     # 标准条码长度
            try:
                code_length = int(code_length)
            except Exception as e:
                print(e)
                code_length = 35
            finally:
                now = datetime.datetime.now()
                doc['code_length'] = code_length
                if isinstance(_id, ObjectId):
                    """修改"""
                    doc['last'] = now
                    r = Company.find_one_and_update(filter_dict={"_id": _id}, update_dict={"$set": doc})
                    if r is None:
                        mes['message'] = "保存数据失败"
                    else:
                        mes['message'] = "success"
                        set_code_length(code_length)  # 重设标准条码长度
                else:
                    """添加"""
                    doc['time'] = now
                    r = Company.insert_one(doc=doc)
                    if r is None:
                        mes['message'] = "保存数据失败"
                    else:
                        mes['message'] = "success"
                        set_code_length(code_length)  # 重设标准条码长度
        else:
            """不是管理员"""
            pass
        return json.dumps(mes)


class ManageProductView(MyView):
    """管理产品信息页面视图函数"""
    _rule = "/product"
    _allowed_view = [0, 1, 3]
    _name = "产品管理"

    @check_session
    def get(self, user: dict):
        """返回管理用户界面"""
        render_data['page_title'] = "产品管理"
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = self.operate_filter(user)  # 数据访问权
        render_data['navs'] = self.check_nav(navs=navs, user=user)  # 导航访问权

        if isinstance(access_filter, dict):
            page_index = get_arg(request, "page", 1)
            r = Product.query(filter_dict=access_filter, page_index=page_index)  # 产品列表
            products = r.pop("data")
            render_data['products'] = products
            render_data.update(r)
            company = Company.find_one(filter_dict=dict())
            company = dict() if company is None else company
            render_data['company'] = company
            return render_template("manage_product.html", **render_data)
        else:
            return abort(401, "access refused!")

    @check_session
    def post(self, user: dict):
        """
        req_type 代表请求的类型, 有4种:
        1. add          添加产品
        2. edit         修改产品
        3. delete       删除产品
        4. selector     获取选择器数据
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
                product_name = get_arg(request, "product_name", "")
                specification = get_arg(request, "specification", "")
                net_contents = get_arg(request, "net_contents", "")
                package_ratio = get_arg(request, "package_ratio", "")
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
                net_contents = get_arg(request, "net_contents", "")
                package_ratio = get_arg(request, "package_ratio", "")
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
            elif req_type == "selector":
                """获取级联选择器数据"""
                args = get_args(request)
                args.pop("type", None)
                _id = args.pop("_id", "")
                if isinstance(_id, str) and len(_id) == 24:
                    args['_id'] = ObjectId(_id)
                selector = Product.selector_data(filter_dict=args)
                mes['message'] = "success"
                mes['data'] = selector
            else:
                mes['message'] = "无效的类型: {}".format(req_type)
        return json.dumps(mes)


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


class ManageRoleView(MyView):
    """管理权限页面视图函数"""
    _rule = "/role"
    _allowed_view = [0, 3]
    _name = "权限管理"

    @check_session
    def get(self, user: dict):
        """返回管理权限界面"""
        render_data['page_title'] = "权限管理"
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = self.operate_filter(user)  # 数据访问权
        render_data['navs'] = self.check_nav(navs=navs, user=user)  # 导航访问权
        if access_filter is None:
            return abort(401)
        else:
            access_filter.update({"role_name": {"$ne": "root"}})
            page_index = get_arg(request, "page", 1)
            r = Role.paging_info(filter_dict=access_filter, page_index=page_index)  # 角色列表
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
        f = self.operate_filter(user)  # 数据访问权
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


class ManageDeviceView(MyView):
    """管理设备页面视图函数"""
    _rule = "/device_summary"
    _allowed_view = [0, 3]
    _name = "嵌入式设备管理"

    @check_session
    def get(self, user: dict):
        """生产线设备管理界面"""
        render_data['page_title'] = "设备信息"
        render_data['cur_user'] = user  # 当前用户,这个变量名要保持不变
        access_filter = self.operate_filter(user)  # 数据访问权
        render_data['navs'] = self.check_nav(navs=navs, user=user)  # 导航访问权
        if access_filter is None:
            return abort(401)
        else:
            page_index = get_arg(request, "page", 1)
            r = ProductLine.paging_info(filter_dict=access_filter, page_index=page_index)  # 角色列表
            lines = r.pop("data")
            render_data['lines'] = lines
            embedded = Embedded.find(filter_dict=access_filter)
            embedded_dict = {x["_id"]: {"ip": x['ip'], "children": x.get('children', dict())} for x in embedded}
            render_data['embedded_dict'] = embedded_dict
            render_data.update(r)
            return render_template("manage_device.html", **render_data)

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
        f = self.operate_filter(user)  # 数据访问权
        if f is None:
            pass
        else:
            req_type = get_arg(request, "type", "")
            if req_type == "line":
                """生产线的操作"""
                _id = get_arg(request, "_id", "")
                operate = get_arg(request, "operate", "")
                if operate == "edit" and isinstance(_id, str) and len(_id) == 24:
                    """编辑生产线"""
                    line_name = get_arg(request, "line_name", "")
                    f = {"_id": ObjectId(_id)}
                    u = {"$set": {"name": line_name}}
                    kw = {
                        "filter_dict": f,
                        "update_dict": u
                    }
                    r = ProductLine.find_one_and_update(**kw)
                    if line_name == r.get('name'):
                        mes['message'] = "success"
                    else:
                        mes['message'] = "修改生产线信息失败"
                elif operate == "add":
                    """添加"""
                    line_name = get_arg(request, "line_name", "")
                    doc = {"name": line_name}
                    r = ProductLine.insert_one(doc=doc)
                    if r is None:
                        mes['message'] = "插入失败"
                    else:
                        mes['message'] = "success"
                elif operate == "delete":
                    """删除"""
                    ids = json.loads(get_arg(request, "ids", ""))
                    ids = [ObjectId(x) for x in ids]
                    r = Embedded.find_one(filter_dict={"line_id": {"$in": ids}})
                    if isinstance(r, dict):
                        mes['message'] = "请先删除主控板:{}".format(r['ip'])
                    else:
                        ProductLine.delete_many(filter_dict={"_id": {"$in": ids}})
                        mes['message'] = "success"
                else:
                    mes['message'] = "未知的操作:{}".format(operate)
            elif req_type == "control":
                """主控板的操作"""
                _id = get_arg(request, "_id", "")
                operate = get_arg(request, "operate", "")
                if operate == "edit" and isinstance(_id, str) and len(_id) == 24:
                    """编辑主控板"""
                    line_id = ObjectId(get_arg(request, "line_id", ""))
                    ip = get_arg(request, "ip", "")
                    """先检查ip是否有冲突?"""
                    if Embedded.allow_control_ip(ip):
                        f = {"_id": ObjectId(_id)}
                        u = {"$set": {"line_id": line_id, "ip": ip}}
                        kw = {
                            "filter_dict": f,
                            "update_dict": u
                        }
                        r = Embedded.find_one_and_update(**kw)
                        if ip == r.get('ip') and line_id == r.get("line_id"):
                            mes['message'] = "success"
                        else:
                            mes['message'] = "修改主控板信息失败"
                    else:
                        mes['message'] = "ip地址冲突"
                elif operate == "add":
                    """添加"""
                    line_id = ObjectId(get_arg(request, "line_id", ""))
                    ip = get_arg(request, "ip", "")
                    if Embedded.allow_control_ip(ip):
                        doc = {"line_id": line_id, "ip": ip}
                        r = Embedded.insert_one(doc=doc)
                        if r is None:
                            mes['message'] = "插入失败"
                        else:
                            mes['message'] = "success"
                    else:
                        mes['message'] ='ip地址冲突'
                elif operate == "delete":
                    """删除"""
                    _id = get_arg(request, "_id", "")
                    f = {"_id": ObjectId(_id)}
                    Embedded.find_one_and_delete(filter_dict=f)
                    mes['message'] = "success"
                else:
                    mes['message'] = "未知的操作:{}".format(operate)
            elif req_type == "execute":
                """执行板的操作"""
                operate = get_arg(request, "operate", "")
                if operate == "add":
                    """添加"""
                    key = uuid4().hex if get_arg(request, "key", '') == "" else get_arg(request, "key")
                    ip = get_arg(request, "ip", "")
                    _id = get_arg(request, "_id", "")
                    raw = Embedded.find_by_id(o_id=_id, to_dict=True)
                    if raw is None:
                        mes['message'] = "对象不存在"
                    else:
                        if Embedded.allow_execute_ip(ip):
                            children = raw.get('children', dict())
                            children[key] = ip
                            f = {"_id": ObjectId(_id)}
                            u = {"$set": {"children": children}}
                            kw = {
                                "filter_dict": f,
                                "update_dict": u
                            }
                            r = Embedded.find_one_and_update(**kw)
                            if isinstance(r, dict):
                                mes['message'] = "success"
                            else:
                                mes['message'] = "添加执行板信息失败"
                        else:
                            mes['message'] = 'ip地址冲突'
                elif operate == "edit":
                    """编辑"""
                    key = get_arg(request, "key", '')
                    ip = get_arg(request, "ip", "")
                    _id = get_arg(request, "_id", "")
                    old_id = get_arg(request, "old_id", "")
                    _id = ObjectId(_id)
                    old_id = ObjectId(old_id)
                    raw = Embedded.find_by_id(o_id=old_id, to_dict=True)
                    if raw is None:
                        mes['message'] = "对象不存在"
                    else:
                        if old_id != _id:
                            """调整了主控板"""
                            if Embedded.allow_execute_ip(ip):
                                children = raw.get('children', dict())
                                children.pop(key, None)
                                u = {"$set": {"children": children}}
                                kw = {
                                    "filter_dict": {"_id": old_id},
                                    "update_dict": u
                                }
                                r = Embedded.find_one_and_update(**kw)
                                if isinstance(r, dict):
                                    n = Embedded.find_by_id(o_id=_id, to_dict=True)
                                    if n is None:
                                        mes['message'] = "新主控板不存在"
                                    else:
                                        children = n.get('children', dict())
                                        children[key] = ip
                                        u = {"$set": {"children": children}}
                                        kw = {
                                            "filter_dict": {"_id": _id},
                                            "update_dict": u
                                        }
                                        r2 = Embedded.find_one_and_update(**kw)
                                        if isinstance(r2, dict):
                                            mes['message'] = "success"
                                        else:
                                            mes['message'] = "修改执行板信息失败"
                                else:
                                    mes['message'] = "修改原始主控板信息失败"
                            else:
                                mes['message'] = 'ip地址冲突'
                        else:
                            """没有调整主控板,只是调整同一主控板下面的控制板"""
                            if Embedded.allow_execute_ip(ip):
                                children = raw.get('children', dict())
                                children[key] = ip
                                u = {"$set": {"children": children}}
                                kw = {
                                    "filter_dict": {"_id": old_id},
                                    "update_dict": u
                                }
                                r = Embedded.find_one_and_update(**kw)
                                if isinstance(r, dict):
                                    mes['message'] = "success"
                                else:
                                    mes['message'] = "修改执行板信息失败"
                            else:
                                mes['message'] = 'ip地址冲突'
                elif operate == "delete":
                    """删除"""
                    key = get_arg(request, "key", "")
                    _id = get_arg(request, "_id", "")
                    _id = ObjectId(_id)
                    f = {"_id": _id}
                    raw = Embedded.find_by_id(o_id=_id, to_dict=True)
                    if raw is None or key not in raw['children']:
                        mes['message'] = "对象不存在"
                    else:
                        children = raw['children']
                        children.pop(key, None)
                        u = {"$set": {"children": children}}
                        kw = {
                            "filter_dict": f,
                            "update_dict": u
                        }
                        r = Embedded.find_one_and_update(**kw)
                        if isinstance(r, dict):
                            mes['message'] = "success"
                        else:
                            mes['message'] = "删除执行板信息失败"
                else:
                    mes['message'] = "未知的操作:{}".format(operate)
            else:
                mes['message'] = "无效的请求类型: {}".format(req_type)
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
"""下载任务执行回传的文件函数"""
DownLoadSyncFileView.register(app=manage_blueprint)
"""下载生产完成的导出文件函数"""
DownLoadOutputFileView.register(app=manage_blueprint)
"""导入条码页面"""
CodeImportView.register(app=manage_blueprint)
"""导出条码页面"""
CodeExportView.register(app=manage_blueprint)
"""导出生产结果页面"""
CodePickleView.register(app=manage_blueprint)
"""生产任务管理"""
ProduceTaskView.register(app=manage_blueprint)
"""管理公司信息接口"""
ManageCompanyView.register(app=manage_blueprint)
"""管理产品页面"""
ManageProductView.register(app=manage_blueprint)
"""管理用户页面"""
ManageUserView.register(app=manage_blueprint)
"""管理权限页面"""
ManageRoleView.register(app=manage_blueprint)
"""管理生产线页面"""
ManageDeviceView.register(app=manage_blueprint)
"""查看修改自己的信息"""
SelfInfoView.register(app=manage_blueprint)

