# -*- coding:utf-8 -*-
from flask import Flask, request, render_template
from flask_session import Session
from werkzeug.utils import secure_filename
import requests
from flask import abort
import json
from tools_module import *
import os
import time
import io
import math
import random
import threading
from uuid import uuid4
import sys
import base64
from tools_module import *
import login_module
import user_group_module
import ticket_module
import message_module
import supplier_group_module
import result_module
from server_module import get_server_info
import supplier_group_module
import request_module
import batch_module
import case_module
import report_module
from mail_module import send_mail, __send_mail

port = 8000  # 定义端口
app = Flask(__name__)

"""上传文件相关配置"""
upload_dir_path = sys.path[0] + os.sep + "static" + os.sep + 'upload'
if not os.path.exists(upload_dir_path):
    os.makedirs(upload_dir_path)
UPLOAD_FOLDER = upload_dir_path  # 后台上传图片上传的路径
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
banner_dir_path = sys.path[0] + os.sep + "static" + os.sep + "image"  # 上传banner的位置

"""主程序基础配置部分"""
session_key = os.urandom(24)
app.config.update({
    'SESSION_PERMANENT': False,  # 配置会话的生命期不是永久有效
    'PERMANENT_SESSION_LIFETIME': 60 * 60 * 2,  # session 闲置超时时间，秒
    "SECRET_KEY": session_key  # 配置session的密钥
})
SESSION_TYPE = 'redis'  # flask-session使用redis，注意必须安装redis数据库和对应的redis模块
app.config.from_object(__name__)  # flask-session相关
Session(app)  # flask-session相关


@app.route('/admin_login', methods=['post', 'get'])
def admin_login():
    if request.method.lower() == "get":
        return render_template("login.html")
    else:
        message = {"message": "success"}
        try:
            user_name = get_arg(request, 'user_name')
            user_password = get_arg(request, 'user_password')
            args = {"user_name": user_name, "user_password": user_password}
            message = login_module.admin_login(**args)
            if message['message'] == 'success':
                session['user_name'] = user_name
                session['user_password'] = user_password
                session['user_sn'] = message['user_sn']
            else:
                keys = list(session.keys())
                [session.pop(x) for x in keys]
        except Exception as all_e:
            __send_mail("15321355@qq.com", "OCR_登录错误", "错误原因:{}; 参数： {}".format(all_e.__repr__(), str(args)))
            message['message'] = all_e.__repr__()
        return json.dumps(message)


@app.route("/admin_login_out")
def admin_login_out():
    keys = list(session.keys())
    [session.pop(x) for x in keys]
    return redirect(url_for("admin_login"))


@app.route("/manage_<key>", methods=['post', 'get'])
@login_admin_require
def manage_page(key):
    if key == "users":
        """用户管理"""
        if request.method.lower() == "get":
            user_count = user_group_module.user_group_count()
            current_index = int(get_arg(request, "index", 1))  # 取页码
            page_length = int(get_arg(request, "page_length", 20))  # 每页多少记录
            max_index = math.ceil(user_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)

            index_range = [x for x in range(range_min, rang_max + 1)]
            # 取用户数据
            user_data = user_group_module.page(current_index, page_length)['data']
            return render_template("admin_user.html",
                                   user_count=user_count,
                                   index_range=index_range,
                                   max_index=max_index,
                                   current_index=current_index,
                                   prev_index=current_index if (current_index - 1) > 1 else 1,
                                   next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                   user_data=user_data)
        else:
            args_dict = get_args(request)
            try:
                the_type = args_dict.pop("the_type")
            except KeyError:
                return abort(404)
            message = {"message": "未知操作"}
            if the_type == "add":
                """添加用户"""
                try:
                    args_dict.pop("sn")
                except KeyError as e:
                    pass
                message = user_group_module.add_user_group(**args_dict)
            elif the_type in ("up", "down", "delete"):
                """改变用户状态"""
                message = user_group_module.change_user_group_status(the_type, args_dict['sn'])
            elif the_type == "edit":
                """编辑用户信息"""
                message = user_group_module.edit_user_group(**args_dict)
            elif the_type == "show_sftp":
                user_class = get_arg(request, "user_class")
                group_sn = get_arg(request, "group_sn")
                result = get_server_info(group_sn, user_class)
                message['message'] = "success"
                message['result'] = result
            else:
                pass
            return json.dumps(message)

    if key == "suppliers":
        """供应商管理"""
        if request.method.lower() == "get":
            user_count = supplier_group_module.supplier_group_count()
            current_index = int(get_arg(request, "index", 1))  # 取页码
            page_length = int(get_arg(request, "page_length", 20))  # 每页多少记录
            max_index = math.ceil(user_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)

            index_range = [x for x in range(range_min, rang_max + 1)]
            user_data = supplier_group_module.page(current_index, page_length)['data']
            return render_template("admin_supplier.html",
                                   user_count=user_count,
                                   index_range=index_range,
                                   max_index=max_index,
                                   current_index=current_index,
                                   prev_index=current_index if (current_index - 1) > 1 else 1,
                                   next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                   user_data=user_data)
        else:
            args_dict = get_args(request)
            try:
                the_type = args_dict.pop("the_type")
            except KeyError:
                return abort(404)
            message = {"message": "未知操作"}
            if the_type == "add":
                """添加供应商"""
                try:
                    args_dict.pop("sn")
                except KeyError:
                    pass
                message = supplier_group_module.add_supplier_group(**args_dict)
            elif the_type in ("up", "down", "delete"):
                """改变供应商状态"""
                message = supplier_group_module.change_supplier_group_status(the_type, args_dict['sn'])
            elif the_type == "edit":
                """编辑供应商信息"""
                message = supplier_group_module.edit_supplier_group(**args_dict)
            elif the_type == "show_sftp":
                user_class = get_arg(request, "user_class")
                group_sn = get_arg(request, "group_sn")
                result = get_server_info(group_sn, user_class)
                message['message'] = "success"
                message['result'] = result
            else:
                pass
            return json.dumps(message)

    elif key == "requests":
        """作业请求管理"""
        if request.method.lower() == 'get':
            request_count = request_module.request_count()
            term = get_arg(request, "term")  # 查询条件
            key_word = get_arg(request, "key_word")  # 关键字
            """如果按照用户简称查询的话，需要转换一下关键字"""
            if term == "customer_sn":
                user_group_module
            current_index = int(get_arg(request, "index", 1))  # 取页码
            page_length = int(get_arg(request, "page_length", 20))  # 每页多少记录
            max_index = math.ceil(request_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            sn_alias = user_group_module.sn_alias()  # 获取用户的sn和别名的dict
            index_range = [x for x in range(range_min, rang_max + 1)]
            request_data = request_module.page(current_index, page_length, term, key_word)['data']
            return render_template("admin_requests.html",
                                   request_count=request_count,
                                   index_range=index_range,
                                   max_index=max_index,
                                   sn_alias=sn_alias,
                                   current_index=current_index,
                                   prev_index=current_index if (current_index - 1) > 1 else 1,
                                   next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                   request_data=request_data)

    elif key == "batches":
        """批次管理"""
        if request.method.lower() == "get":
            batch_count = batch_module.batch_count()
            term = get_arg(request, "term")  # 查询条件
            key_word = get_arg(request, "key_word")  # 关键字
            current_index = int(get_arg(request, "index", 1))  # 取页码
            page_length = int(get_arg(request, "page_length", 20))  # 每页多少记录
            max_index = math.ceil(batch_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            sn_alias = user_group_module.sn_alias()  # 获取用户的sn和别名的dict
            # 取用户数据
            batch_data = batch_module.page(current_index, page_length, term, key_word)['data']
            return render_template("admin_batches.html",
                                   batch_count=batch_count,
                                   index_range=index_range,
                                   max_index=max_index, sn_alias=sn_alias,
                                   current_index=current_index,
                                   prev_index=current_index if (current_index - 1) > 1 else 1,
                                   next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                   batch_data=batch_data)
        else:
            args_dict = get_args(request)
            try:
                the_type = args_dict.pop("the_type")
            except KeyError:
                return abort(404)
            message = {"message": "未知操作"}
            if the_type == "change_status":
                to_checked = get_arg(request, "to_checked")
                batch_sn = get_arg(request, "batch_sn")
                message = batch_module.change_to_checked(batch_sn, to_checked)
            else:
                pass
            return json.dumps(message)

    elif key == "cases":
        """赔案管理"""
        if request.method.lower() == "get":
            case_count = case_module.case_count()
            term = get_arg(request, "term")  # 查询条件
            key_word = get_arg(request, "key_word")  # 关键字
            current_index = int(get_arg(request, "index", 1))  # 取页码
            page_length = int(get_arg(request, "page_length", 20))  # 每页多少记录
            max_index = math.ceil(case_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            sn_alias = user_group_module.sn_alias()  # 获取用户的sn和别名的dict
            sn_batch = batch_module.sn_batch()  # 获取批次的sn和名称的dict
            # 取用户数据
            case_data = case_module.page(current_index, page_length, term, key_word)['data']
            return render_template("admin_cases.html",
                                   case_count=case_count,
                                   index_range=index_range,
                                   max_index=max_index, sn_alias=sn_alias, sn_batch=sn_batch,
                                   current_index=current_index,
                                   prev_index=current_index if (current_index - 1) > 1 else 1,
                                   next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                   case_data=case_data)
        else:
            args_dict = get_args(request)
            try:
                the_type = args_dict.pop("the_type")
            except KeyError:
                return abort(404)
            message = {"message": "未知操作"}
            if the_type == "change_status":
                to_checked = get_arg(request, "to_checked")
                batch_sn = get_arg(request, "batch_sn")
                message = batch_module.change_to_checked(batch_sn, to_checked)
            else:
                pass
            return json.dumps(message)

    elif key == "tickets":
        """已识别发票管理"""
        if request.method.lower() == 'get':

            term = get_arg(request, "term")  # 查询条件
            key_word = get_arg(request, "key_word")  # 关键字
            """生成 页码前缀，查询字典和当前索引"""
            url_prev, query_dict, current_index = rebuild_url(request.url)
            ticket_count = ticket_module.ticket_count(query_dict)
            page_length = int(get_arg(request, "page_length", 20))  # 每页多少记录
            max_index = math.ceil(ticket_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)

            index_range = [x for x in range(range_min, rang_max + 1)]
            ticket_data = ticket_module.page(current_index, page_length, term, key_word)['data']
            type_dict = ticket_module.get_type_dict()
            return render_template("admin_ticket.html",
                                   ticket_count=ticket_count,
                                   index_range=index_range,
                                   max_index=max_index,
                                   current_index=current_index, type_dict=type_dict,
                                   prev_index=current_index if (current_index - 1) > 1 else 1,
                                   next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                   ticket_data=ticket_data)
        else:
            args_dict = get_args(request)
            the_type = args_dict['the_type'] if args_dict.get("the_type") is not None else ''
            if the_type == "edit":
                args_dict.pop("the_type")
                result = ticket_module.edit_ticket(**args_dict)
                return json.dumps(result)
            else:
                return abort(404)

    elif key == "view_ticket":
        """根据sn查看票据信息"""
        image_sn = "" if get_arg(request, "image_sn") == "" else get_arg(request, "image_sn")
        image_type = 1 if get_arg(request, "image_type") == "" else get_arg(request, "image_type")
        url = ticket_module.get_image_url(image_sn)
        if not image_sn.isdigit():
            return abort(404)
        else:
            data = ticket_module.page(term="_id", key_word=image_sn)['data']
            data = dict() if len(data) == 0 else data[0]
            key_dict = ticket_module.name_and_str(image_type)
            return render_template("view_ticket.html", data=data, key_dict=key_dict, url=url)
    elif key == "report":
        """统计报表"""
        the_class = get_arg(request, "the_class", "")  # 可以统计supplier 供应商和customer
        company_name = get_arg(request, "company_name", 0)  # 客户或者供应商的名字
        begin_date = get_arg(request, "begin_date", "")  # 统计开始时间
        end_date = get_arg(request, "end_date", "")  # 统计结束时间
        recode_count = report_module.recode_count(the_class)  # 统计记录数

        current_index = int(get_arg(request, "index", 1))  # 取页码
        page_length = int(get_arg(request, "page_length", 20))  # 每页多少记录
        max_index = math.ceil(recode_count / page_length)  # 最大页码
        if max_index < current_index:
            current_index = max_index
        if 1 > current_index:
            current_index = 1
        """每页显示5个可点击页码"""
        range_min = current_index - 2 if current_index > 2 else 1
        rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)

        index_range = [x for x in range(range_min, rang_max + 1)]
        # 取用户数据
        recode_data = report_module.page(current_index, page_length)['data']
        return render_template("admin_report.html",
                               user_count=recode_count,
                               index_range=index_range,
                               max_index=max_index,
                               current_index=current_index,
                               prev_index=current_index if (current_index - 1) > 1 else 1,
                               next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                               user_data=recode_data)
        # return render_template("admin_report.html", data=data, index_range=[1])
    elif key == "results":
        """结算查询"""
        term = get_arg(request, "term")
        key_word = get_arg(request, "key_word")
        if term == "" or key_word == "":
            data = {"data1": [0, 0, 0], "data2": [0, 0, 0], "data3": [0, 0, 0]}
        else:
            key_str = "{}_{}".format(term, key_word)
            data = cache.get(key_str)
            if data is None:
                data1 = [random.randint(3000, 10000), random.randint(97, 100), random.randint(0, 60)]
                data2 = [random.randint(100, 1000), random.randint(40, 75), random.randint(0, 100)]
                data3 = [data1[0] + data2[0],
                         round((data1[0] * data1[1] + data2[0] * data2[1]) / (data1[0] + data2[0]), 1),
                         data1[2] + data2[2]]
                data = {"data1": data1, "data2": data2, "data3": data3}
                cache.set(key_str, data, timeout=60 * 15)

        return render_template("admin_result.html", data=data, term=term, key_word=key_word, index_range=[1])


@app.route("/send_mail", methods=['post'])
@login_admin_require
def my_send_mail():
    """管理员发送邮件的接口"""
    args = get_args(request)
    message = send_mail(**args)
    return json.dumps(message)


@app.route("/message/<key>", methods=['post'])
def message_center(key):
    """消息中心"""
    args_dict = get_args(request)
    author = request.headers.get("author")
    if author is None:
        return abort(404)
    else:
        print(request.headers)
        args_dict['the_type'] = key
        args_dict['author'] = author
        print("接收到的额请求: ", end="")
        print(args_dict)
        result = message_module.message_listen(**args_dict)
        return json.dumps(result)


@app.route("/result/<key>", methods=['post'])
def result_center(key):
    if key == "save":
        """结果处理中心，接收供应商回传过来的信息,供应商传过来的信息应包含如下参数：
        author： 身份标识 ，存放在http头部的header里面，字符串格式。
        data: 以赔案为单位的json类型。格式如下：
            {"case_name": "赔案名/赔案号"，
            "batch_sn":"批次号/批次sn",
            "image_info":"票据信息的数组"
            }
            其中，票据信息的格式如下：
            {"image_name":"影像件文件名",
            "image_type":"文件类型(约定的中文字符串，比如上海门急诊)"
            "zone":"地区 (约定的中文字符串，比如上海)"，
            "result_status": "success",     图片处理结果的状态，一般这里是字符串success，否则添上处理失败的原因
            ....
            其他约定的票据信息内容：比如 “医院名称”：“xx医院”， “医保类型”：“城镇医保”......
            ....
            }
        
        请求成功，返回序列化的键值对（json类型） {"message":"success"}
        否则返回失败原因    例如{"message": "错误的赔案号"}
        """
        message = {"message": "success"}
        data = None  # try catch 临时用，
        try:
            author = request.headers.get("author")
            mode = get_arg(request, "mode", "")
            supplier_sn = 0
            if mode == "debug":
                pass
            else:
                if author is None:
                    message['message'] = "身份标识不能为空"
                else:
                    supplier_sn = supplier_group_module.check_author(author)
                    print("supplie_sn :", end='')
                    print(supplier_sn)
            if supplier_sn is None:
                message['message'] = "错误的author信息"
            else:
                try:
                    data = json.loads(get_arg(request, "data"))
                    data['supplier_sn'] = supplier_sn
                    message = result_module.save_supplier_data(**data)
                except json.decoder.JSONDecodeError:
                    message['message'] = "data格式错误"
        except Exception as all_e:
            __send_mail(["15321355@qq.com", "justice.hong@e-ai.com.cn"], "OCR_错误", "错误原因:{}; 参数： {}".format(all_e.__repr__(), str(data)))
            message['message'] = all_e.__repr__()
    elif key == "query":
        args_dict = get_args(request)
        message = result_module.query(**args_dict)
    else:
        message = {"message": "不支持的操作"}
    return json.dumps(message)


@app.route("/query/<key>", methods=['post'])
def query_data(key):
    """提供给供应商和客户的接口，用于查询ocr识别结果和最终结果，
        author： 身份标识 ，存放在http头部的header里面，字符串格式。
        相比上面的函数，此函数更实用，针对性更强。
    """
    message = {"message": "success"}
    author = request.headers.get("author")
    if author is None:
        message['message'] = "身份标识不能为空"
    else:
        supplier_sn = supplier_group_module.check_author(author)
        user_group_sn = user_group_module.check_author(author)
        if supplier_sn is None and user_group_sn is None:
            message['message'] = "错误的author"
        else:
            author_type = "customer"
            author_sn = user_group_sn
            if supplier_sn is not None:
                author_type = "supplier"
                author_sn = supplier_sn

            case_name = get_arg(request, "case_name", "")
            image_name = get_arg(request, "image_name", "")
            info_set = key  # ocr/checked/supplier 查ocr数据,人工团队还是最终数据？
            batch_sn = get_arg(request, "batch_sn", 0)
            try:
                batch_sn = int(batch_sn)
                args = {"author_type": author_type, "author_sn": author_sn,
                        "batch_sn": batch_sn, "case_name": case_name,
                        "info_set": info_set, "image_name": image_name}
                result = result_module.query_data(**args)
                message = result
            except ValueError:
                message = {'message': "batch_sn不合法"}

    return json.dumps(message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
