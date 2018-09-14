#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import render_template
from flask import make_response
from flask import abort
from flask import send_file
from tools_module import *
import json
import requests
from hashlib import md5
from uuid import uuid4
from mail_module import send_mail
from tools_module import *
from module.trade_module import process_case
from module.teacher_module import *
import mongo_db
from io import BytesIO


BaseFile = mongo_db.BaseFile


"""注册蓝图"""
teacher_blueprint = Blueprint("teacher_blueprint", __name__, url_prefix="/teacher", template_folder="templates/")


"""分析师登录，喊单操作的视图函数"""


def version():
    """生成一个随机的版本号"""
    return uuid4().hex


def login() -> str:
    """teacher login page"""
    method = request.method.lower()
    if method == "get":
        page_title = "大师登录"
        return render_template("t_login.html", page_title=page_title,v=version())
    elif method == "post":
        phone = get_arg(request, "phone", '')
        pw = get_arg(request, "password", '')
        mes = {"message": "success"}
        if phone == "" or pw == "":
            mes['message'] = "必要参数不能为空"
        else:
            f = {"phone": phone}
            p = ['phone', 'name', 'password']
            t = Teacher.find_one_plus(filter_dict=f, projection=p, instance=False)
            if t is None:
                mes['message'] = "用户不存在"
            else:
                pw = md5(pw.encode(encoding='utf-8')).hexdigest().lower()
                if pw == t.get("password", "").lower():
                    if t.get("native"):
                        """登录成功"""
                        session['t_id'] = t["_id"]
                    else:
                        mes['message'] = "此账户无法登录"
                else:
                    mes['message'] = "密码错误"
        return json.dumps(mes)
    else:
        return abort(405)


def login_out():
    """注销"""
    session.pop("t_id")
    return json.dumps({"message": "success"})


def quotation_page():
    """报价页面"""
    page_title = "行情"
    return render_template("quotation.html", page_title=page_title, v=version())


def news_func():
    """
    新闻页面/系统信息
    :return:
    """
    page_title = "实时新闻"
    return render_template("news.html", page_title=page_title, v=version())


def log_func():
    """记录老师操作日志"""
    t_id = session.get("t_id", '')
    content = get_arg(request, "args", "")
    url = get_arg(request, "url", "")
    error = get_arg(request, "error", "")
    error_time = get_arg(request, "error_time", "")
    error_time_t = mongo_db.get_datetime_from_str(error_time)
    error_time = error_time_t if isinstance(error_time_t, datetime.datetime) else error_time
    TeacherLog.log(t_id=t_id, url=url, error_time=error_time, error=error, content=content)
    return json.dumps("ok")


@check_teacher_session
def file_func(teacher: dict = None, action: str = "", table_name: str = ""):
    """
    保存/获取文件,
    :param action: 动作, save/get(保存/获取)
    :param table_name: 文件类对应的表名.
    :return:
    """
    mes = {"message": "success"}
    """
    tables表名,分别存储不同的类的实例.
    1. base_info                  文件存储基础表,对应mongo_db.BaseFile
    2. teacher_image                老师相关图片
    """
    tables = ['base_file', 'teacher_image']
    table_name = table_name if table_name in tables else 'base_file'
    if action == "save":
        """保存文件"""
        owner = teacher.get('_id')
        r = BaseFile.save_flask_file(req=request, collection=table_name, owner=owner)
        if isinstance(r, ObjectId):
            mes['_id'] = str(r)
        else:
            mes['message'] = "保存失败"
    elif action == "view":
        """获取文件"""
        fid = get_arg(request, "fid", "")
        if isinstance(fid, str) and len(fid) == 24:
            fid = ObjectId(fid)
            f = {"_id": fid}
            r = BaseFile.find_one_cls(filter_dict=f, collection=table_name)
            if r is None:
                return abort(404)
            else:
                mime_type = "image/jpeg" if r.get('mime_type') is None else r['mime_type']
                file_name = "1.jpeg" if r.get('file_name') is None else r['file_name']
                """把文件名的中文从utf-8转成latin-1,这是防止中文的文件名造成的混乱"""
                file_name = file_name.encode().decode('latin-1')
                data = r['data']
                data = BytesIO(initial_bytes=data)
                resp = make_response(send_file(data, attachment_filename=file_name, as_attachment=True,
                                               mimetype=mime_type))
                return resp
        else:
            mes['message'] = '无效的id'
    else:
        mes['message'] = "不支持的操作"
    return json.dumps(mes)


# @check_teacher_session
# def process_case_page(teacher: dict = None):
#     """
#     暂停使用,仅作参考 2018-9-9
#     交易管理
#     旧版本,
#     """
#     method = request.method.lower()
#     if method == "get":
#         page_title = "交易管理"
#         hold_list = Teacher.get_hold(t_id=teacher['_id'])  # 持仓信息
#         return render_template("process_case.html", page_title=page_title, teacher=teacher, hold_list=hold_list,
#                                v=version())
#     elif method == "post":
#         """
#         分析师微信喊单信号。在未整合之前，此类信号一律转交
#         Message_Server项目处理 2018-8-28
#         """
#         args = get_args(request)
#         now = datetime.datetime.now()
#         mes = {"message": "success"}
#         t_id = teacher['_id']
#         args['teacher_id'] = t_id
#         args['teacher_name'] = teacher['name']
#         args['version'] = "1.0"
#         if teacher['native']:
#             """真实老师"""
#             args['change'] = "raw"
#             args['native'] = True
#         else:
#             args['change'] = 'follow'
#             args['native'] = False
#         _id = args.get("_id", "")
#         if isinstance(_id, str) and len(_id) == 24:
#             """1 这是离场"""
#             """1.1 处理离场时间"""
#             ets = args.get('exit_time', '')
#             et = mongo_db.get_datetime_from_str(ets)
#             if isinstance(et, datetime.datetime):
#                 args['exit_time'] = et
#             else:
#                 title = "{}离场时没有传递离场时间".format(now)
#                 content = "老师id: {}, trade_id:{}, exit_time:{}".format(t_id, _id, ets)
#                 logger.exception(msg=title + content)
#                 send_mail(title=title, content=content)
#                 args['exit_time'] = now
#             """1.2 处理离场价格"""
#             exit_price = None
#             exit_price_s = args.pop("exit_price", None)
#             try:
#                 exit_price = float(exit_price_s)
#             except Exception as e:
#                 print(e)
#             finally:
#                 if isinstance(exit_price, float):
#                     args['exit_price'] = float(exit_price)
#                     ses = mongo_db.get_conn(table_name="trade")
#                     f = {"_id": ObjectId(_id)}
#                     obj = ses.find_one(filter=f)
#                     if obj is None:
#                         mes["message":] = "订单不存在"
#                     else:
#                         args['case_type'] = "exit"
#                         obj.update(args)
#                         args = obj
#                         if process_case(doc_dict=args, raw=True):
#                             """成功"""
#                             pass
#                         else:
#                             mes = {"message": "操作失败"}
#                 else:
#                     title = "{}离场时没有传递离场价格".format(now)
#                     content = "老师id: {}, trade_id:{},exit_price:{} ".format(t_id, _id, exit_price_s)
#                     logger.exception(msg=title + content)
#                     send_mail(title=title, content=content)
#                     mes = {"message": "缺少离场价格"}
#         else:
#             """2 这是进场"""
#             """2.1 先处理进场时间"""
#             enter_time_s = args.get("enter_time", '')
#             enter_time = mongo_db.get_datetime_from_str(enter_time_s)
#             if isinstance(enter_time, datetime.datetime):
#                 args['enter_time'] = enter_time
#             else:
#                 title = "{}进场时没有传递进场时间".format(now)
#                 content = "老师id: {}, trade_id:{}, enter_time:{}".format(t_id, _id, enter_time_s)
#                 logger.exception(msg=title + content)
#                 send_mail(title=title, content=content)
#                 args['enter_time'] = now
#             """2.2 处理进场价格"""
#             enter_price = None
#             enter_price_s = args.pop("enter_price", None)
#             try:
#                 enter_price = float(enter_price_s)
#             except Exception as e:
#                 print(e)
#             finally:
#                 if isinstance(enter_price, float):
#                     args['enter_price'] = float(enter_price)
#                     args['_id'] = ObjectId()
#                     args['case_type'] = "enter"
#                     args['each_profit'] = 0.0
#                     args['lots'] = 1
#                     args['native_direction'] = args['direction']
#                     args['record_id'] = args['_id']
#                     if process_case(doc_dict=args, raw=True):
#                         """成功"""
#                         pass
#                     else:
#                         mes = {"message": "操作失败"}
#                 else:
#                     title = "{}进场时没有传递进场价格".format(now)
#                     content = "老师id: {}, trade_id:{},enter_price:{} ".format(t_id, _id, enter_price_s)
#                     logger.exception(msg=title + content)
#                     send_mail(title=title, content=content)
#                     mes = {"message": "缺少进场价格"}
#
#         return json.dumps(mes)
#     else:
#         return abort(405)


@check_teacher_session
def process_case_page2(teacher: dict = None):
    """老师操作相关页面"""
    method = request.method.lower()
    if method == "get":

        page_title = "交易管理"
        hold_list = Teacher.get_hold(t_id=teacher['_id'])  # 持仓信息
        """喊单历史"""
        f = dict()
        trade_list = Teacher.trade_history(t_id=teacher['_id'], filter_dict=f)
        return render_template("positions.html", page_title=page_title, teacher=teacher, hold_list=hold_list,
                               v=version(), trade_list=trade_list)
    elif method == "post":
        args = get_args(request)
        mes = {"message": "error"}
        the_type = args.pop("the_type", None)
        now = datetime.datetime.now()
        if the_type == "operate_trade":
            """分析师喊单"""
            t_id = teacher['_id']
            args['teacher_id'] = t_id
            args['teacher_name'] = teacher['name']
            args['version'] = "1.0"
            if teacher['native']:
                """真实老师"""
                args['change'] = "raw"
                args['native'] = True
            else:
                args['change'] = 'follow'
                args['native'] = False
            _id = args.get("_id", "")
            if isinstance(_id, str) and len(_id) == 24:
                """1 这是离场"""
                """1.1 处理离场时间"""
                ets = args.get('exit_time', '')
                et = mongo_db.get_datetime_from_str(ets)
                if isinstance(et, datetime.datetime):
                    args['exit_time'] = et
                else:
                    title = "{}离场时没有传递离场时间".format(now)
                    content = "老师id: {}, trade_id:{}, exit_time:{}".format(t_id, _id, ets)
                    logger.exception(msg=title + content)
                    send_mail(title=title, content=content)
                    args['exit_time'] = now
                """1.2 处理离场价格"""
                exit_price = None
                exit_price_s = args.pop("exit_price", None)
                try:
                    exit_price = float(exit_price_s)
                except Exception as e:
                    print(e)
                finally:
                    if isinstance(exit_price, float):
                        args['exit_price'] = float(exit_price)
                        ses = mongo_db.get_conn(table_name="trade")
                        f = {"_id": ObjectId(_id)}
                        obj = ses.find_one(filter=f)
                        if obj is None:
                            mes["message":] = "订单不存在"
                        else:
                            args['case_type'] = "exit"
                            obj.update(args)
                            args = obj
                            if process_case(doc_dict=args, raw=True):
                                """成功"""
                                mes['message'] = 'success'
                            else:
                                mes = {"message": "操作失败"}
                    else:
                        title = "{}离场时没有传递离场价格".format(now)
                        content = "老师id: {}, trade_id:{},exit_price:{} ".format(t_id, _id, exit_price_s)
                        logger.exception(msg=title + content)
                        send_mail(title=title, content=content)
                        mes = {"message": "缺少离场价格"}
            else:
                """2 这是进场"""
                """2.1 先处理进场时间"""
                enter_time_s = args.get("enter_time", '')
                enter_time = mongo_db.get_datetime_from_str(enter_time_s)
                if isinstance(enter_time, datetime.datetime):
                    args['enter_time'] = enter_time
                else:
                    title = "{}进场时没有传递进场时间".format(now)
                    content = "老师id: {}, trade_id:{}, enter_time:{}".format(t_id, _id, enter_time_s)
                    logger.exception(msg=title + content)
                    send_mail(title=title, content=content)
                    args['enter_time'] = now
                """2.2 处理进场价格"""
                enter_price = None
                enter_price_s = args.pop("enter_price", None)
                try:
                    enter_price = float(enter_price_s)
                except Exception as e:
                    print(e)
                finally:
                    if isinstance(enter_price, float):
                        args['enter_price'] = float(enter_price)
                        args['_id'] = ObjectId()
                        args['case_type'] = "enter"
                        args['each_profit'] = 0.0
                        args['lots'] = 1
                        args['native_direction'] = args['direction']
                        args['record_id'] = args['_id']
                        if process_case(doc_dict=args, raw=True):
                            """成功"""
                            mes['message'] = 'success'
                        else:
                            mes = {"message": "操作失败"}
                    else:
                        title = "{}进场时没有传递进场价格".format(now)
                        content = "老师id: {}, trade_id:{},enter_price:{} ".format(t_id, _id, enter_price_s)
                        logger.exception(msg=title + content)
                        send_mail(title=title, content=content)
                        mes = {"message": "缺少进场价格"}
        elif the_type == "trade_history":
            """历史喊单"""
            p = get_arg(request, "product", "")  # 是否对产品种类进行了筛选?
            if p == "":
                f = dict()
            else:
                f = {"product": p}
            first_exit_time = get_arg(request, "first_exit_time", "")  # 是否对产品离场时间进行过滤?
            if isinstance(first_exit_time, str) and len(first_exit_time) > 12:
                first_exit_time = mongo_db.get_datetime_from_str(first_exit_time)
                if isinstance(first_exit_time, datetime.datetime):
                    f['exit_time'] = {"$lt": first_exit_time}
            data = Teacher.trade_history(t_id=teacher['_id'], filter_dict=f, can_json=True)
            mes['data'] = data
            mes['message'] = 'success'
        else:
            mes = {"message": "未知的操作:{}".format(the_type)}
        return json.dumps(mes)

    else:
        return abort(405)


"""集中注册函数"""


"""日志接口"""
teacher_blueprint.add_url_rule(rule="/log", view_func=log_func, methods=['get', 'post'])
"""老师登录"""
teacher_blueprint.add_url_rule(rule="/login.html", view_func=login, methods=['get', 'post'])
"""老师图片的相关操作"""
teacher_blueprint.add_url_rule(rule="/file/<action>/<table_name>", view_func=file_func, methods=['get', 'post'])
"""老师注销"""
teacher_blueprint.add_url_rule(rule="/login_out", view_func=login_out, methods=['get', 'post'])
"""报价页面"""
teacher_blueprint.add_url_rule(rule="/quotation.html", view_func=quotation_page, methods=['get', 'post'])
"""新闻页面"""
teacher_blueprint.add_url_rule(rule="/news.html", view_func=news_func, methods=['get', 'post'])
"""交易管理"""
teacher_blueprint.add_url_rule(rule="/process_case.html", view_func=process_case_page2, methods=['get', 'post'])


