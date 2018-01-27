# -*- coding: utf-8 -*-
from sanic import Sanic
from sanic.response import json as resp_json
from sanic.response import html
import json
from sanic_jinja2 import SanicJinja2
from sanic.response import redirect
from sanic import response
from sanic.config import LOGGING
import asyncio_redis
from sanic_session import RedisSessionInterface
from sanic.response import text
from sanic.exceptions import NotFound
import random
import os
import re
import math
import admin_module
import customer_module
import company_module
import plan_module
import position_module
import url_module
import employee_module
import team_module
from db_module import check_phone, cache, validate_arg
import track_module
from log_module import get_logger
import sms_module
import datetime


LOGGING['loggers']['network']['handlers'] = ['accessSysLog', 'errorSysLog']
port = 5000
host = '0.0.0.0'
app = Sanic(__name__)
app.static("/static", "./static")
jinja = SanicJinja2(app)
logger = get_logger()
"""定义非法访问记录文件"""
dir_path = os.path.split(__file__)[0]
path_str = os.path.join(dir_path, "logs")
if not os.path.exists(path_str):
    os.makedirs(path_str)
format_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
back_ip_txt = open(os.path.join(path_str, "back_ip_{}.txt".format(format_now)), "w", encoding="utf-8")


class Redis:
    """定义一个类，用于sanic_session"""
    _pool = None

    async def get_redis_pool(self):
        if not self._pool:
            self._pool = await asyncio_redis.Pool.create(host='localhost', port=6379, db=10, poolsize=10)
        return self._pool


redis = Redis()
session_interface = RedisSessionInterface(redis.get_redis_pool, expiry=60 * 60 * 3)


@app.route("/admin_login", methods=["POST", "GET"])  # 和flask不同，注意方法必须大写
async def admin_login(request):
    """后台登录页面和登录请求验证"""
    if request.method == "GET":
        login_title = "后台登陆"
        return jinja.render("admin_login.html", request=request, login_title=login_title)
    else:
        user_name = request.form.get("user_name")
        user_password_md5 = request.form.get("user_password")
        message = admin_module.check_login(user_name, user_password_md5)
        if message['message'] == 'success':
            """验证通过"""
            request['session']['user_name'] = user_name
            request['session']['user_password'] = user_password_md5
        else:
            request['session'].clear()
        resp = resp_json(message)
        return resp


@app.route("/company_login", methods=["POST", "GET"])  # 和flask不同，注意方法必须大写
async def company_login(request):
    """分公司后台登录页面和登录请求验证"""
    if request.method == "GET":
        login_title = "后台登陆"
        return jinja.render("admin_login_company.html", request=request, login_title=login_title)
    else:
        user_name = request.form.get("user_name")
        user_password_md5 = request.form.get("user_password")
        message = company_module.check_login(user_name, user_password_md5)
        if message['message'] == 'success':
            """验证通过"""
            request['session']['user_name'] = user_name
            request['session']['user_password'] = user_password_md5
            request['session']['sn'] = message['data']['sn']
        else:
            request['session'].clear()
        resp = resp_json(message)
        return resp


@app.route("/employee_login", methods=["POST", "GET"])  # 和flask不同，注意方法必须大写
async def employee_login(request):
    """employee登录页面和登录请求验证"""
    if request.method == "GET":
        login_title = "员工登陆"
        return jinja.render("employee_login.html", request=request, login_title=login_title)
    else:
        user_phone = request.form.get("user_phone")
        user_password_md5 = request.form.get("user_password")
        message = employee_module.check_login(user_phone, user_password_md5)
        if message['message'] == 'success':
            """验证通过"""
            request['session']['user_phone'] = user_phone
            request['session']['user_password'] = user_password_md5
            request['session']['team_sn'] = message['data']['team_sn']
            request['session']['employee_sn'] = message['data']['employee_sn']
            request['session']['company_sn'] = message['data']['company_sn']
        else:
            request['session'].clear()
        resp = resp_json(message)
        return resp


@app.route("/admin_login_out")
async def my_login_out(request):
    """注销"""
    url_path = request.headers['referer'].split("?")[0]
    request['session'].clear()
    if url_path.find(r"/manage/") != -1:
        return redirect("/admin_login")
    elif url_path.find(r"/company/") != -1:
        return redirect("/company_login")
    else:
        return redirect("/employee_login")


@app.route("/manage/<key:string>", methods=["POST", "GET"])
async def my_manage(request, key):
    """后台管理模块"""
    owner_sn = 0
    if key == "user":
        """用户管理"""
        if request.method == "GET":
            """取翻页前缀"""
            url_path = request.path
            args = request.raw_args
            try:
                args.pop("index")
            except KeyError as e:
                print(e)
            finally:
                temp = "?"
                for k, v in args.items():
                    temp += "{}={}&".format(k, v)
                url_path += temp
            """取过滤关键词,用于只显示customer_description匹配的用户"""
            key_word_str = request.args.get("key_word", None)
            if key_word_str is None:
                key_word_list = list()
            else:
                key_word_list = [x.strip() for x in key_word_str.split(" ")]
            the_type = request.args.get("the_type", "all")  # 查询用户的条件，默认是all
            filter_dict = {"customer_description": key_word_list}  # 统计人数时的额外筛选器
            customer_count = customer_module.customer_count(sn=0, the_type="public", filter_dict=filter_dict)  # 统计总数
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(customer_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            # 取用户数据  page(the_type="all", index=1, length=30, term=''):
            args = {
                "the_type": the_type, "index": current_index,
                "length": page_length, "key_word_list": key_word_list
            }
            customer_data = customer_module.page(**args)  # 用户数据
            count_all = customer_module.count_by_company_name(0, filter_dict=filter_dict)  # 按分公司统计注册用户总数量
            count_public = customer_module.count_by_company_name(0, url_from='public', filter_dict=filter_dict)  # 按分公司统计公共链接注册用户总数量
            count_private = customer_module.count_by_company_name(0, url_from='private', filter_dict=filter_dict)  # 按分公司统计专用链接注册用户总数量
            company_sn_name = company_module.get_names()
            return jinja.render("admin_user.html",
                                request=request, count_all=count_all, count_public=count_public,
                                customer_count=customer_count, count_private=count_private,
                                index_range=index_range, company_sn_name=company_sn_name,
                                max_index=max_index,
                                current_index=current_index,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                customer_data=customer_data)
        else:
            """编辑用户信息"""
            the_type = request.form.get("the_type")
            user_sn = request.form.get("user_sn")
            val = request.form.get("val")
            args = {"the_type": the_type, "user_sn": user_sn, "val": val}
            message = customer_module.edit_customer(**args)
            return resp_json(message)
    elif key == "company":
        """公司管理"""
        if request.method == "GET":
            company_count = company_module.company_count(0)  # 统计总数
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(company_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            # 取用户数据  page(the_type="all", index=1, length=30, term=''):
            args = {"index": current_index, "length": page_length}
            customer_data = company_module.page(**args)['data']
            return jinja.render("admin_company.html",
                                request=request,
                                company_count=company_count,
                                index_range=index_range,
                                max_index=max_index,
                                current_index=current_index,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                user_data=customer_data)
        else:
            """编辑公司信息"""
            the_type = request.form.get("the_type")
            message = {"message": "error"}
            if the_type == "add":
                company_name = request.form.get("company_name")
                user_name = request.form.get("user_name")
                user_password = request.form.get("user_password")
                args = {"user_password": user_password, "user_name": user_name, "company_name": company_name}
                message = company_module.add_company(**args)
            elif the_type == "delete":
                sn = request.form.get("sn")
                message = company_module.delete_company(sn=sn)
            elif the_type in ['up', 'down']:
                sn = request.form.get("sn")
                user_status = 1 if the_type == "up" else 0
                message = company_module.edit_company(sn=sn, user_status=user_status)
            elif the_type == "edit":
                sn = request.form.get("sn")
                company_name = request.form.get("company_name")
                user_name = request.form.get("user_name")
                user_password = request.form.get("user_password")
                args = {"sn": sn, "user_password": user_password, "user_name": user_name, "company_name": company_name}
                message = company_module.edit_company(**args)
            return resp_json(message)
    elif key == "plan":
        """分配计划管理"""
        if request.method == "GET":
            plan_count = plan_module.plan_count(owner_sn)  # 统计总数
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(plan_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            args = {"index": current_index, "length": page_length}
            plan_count_data = plan_module.page(**args)['data']
            member_dict = plan_module.get_members(owner_sn)
            default_plan = None  # 默认分配计划
            for x in plan_count_data:
                if x['sn'] == 1:
                    default_plan = x
                    plan_count_data.remove(x)
                    break
            return jinja.render("admin_plan.html",
                                request=request, member_dict=member_dict,
                                plan_count=plan_count, default_plan=default_plan,
                                index_range=index_range,
                                max_index=max_index,
                                current_index=current_index,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                plan_count_data=plan_count_data)
        else:
            """编辑分配计划"""
            the_type = request.form.get("the_type")
            message = {"message": "error"}
            if the_type == "get_members":
                """获取可用选择的团队成员"""
                member_dict = plan_module.get_members(owner_sn)
                message['data'] = member_dict
            elif the_type in ["add", "edit", "delete", "up", "down"]:
                key_list = list(request.form.keys())
                args = dict()
                for key in key_list:
                    val = request.form.get(key)
                    if key == "member_list":
                        val = json.loads(val)
                    else:
                        pass
                    args[key] = val
                    args['owner_sn'] = owner_sn
                    member_list = list() if args.get("member_list") is None else args.get("member_list")
                if len(member_list) == 0 and the_type not in ["delete", "up", "down"]:
                    message['message'] = "没有团队成员无法创建分配策略"
                else:
                    result = plan_module.process(**args)
                    message = result
            elif the_type == "get_item":
                """根据plan_sn获取成员信息"""
                sn = request.form.get("plan_sn")
                message = plan_module.get_plan_item(sn)
            else:
                message['message'] = "不理解的操作"
            return resp_json(message)

    elif key == "url":
        """链接管理"""
        if request.method == "GET":
            url_count = url_module.url_count()  # 统计总数
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(url_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            # 取用户数据  page(the_type="all", index=1, length=30, term=''):
            args = {"index": current_index, "length": page_length}
            url_data = url_module.page(**args)
            company_dict = company_module.get_names()  # 公司sn和名字的字典
            separate_count = url_module.separate_count()  # 按照专有链接统计注册人数
            return jinja.render("admin_url.html",
                                request=request, company_dict=company_dict,
                                url_count=url_count, channel_dict=url_module.get_channel_dict(),
                                index_range=index_range, pattern_dict=url_module.get_pattern_dict(),
                                max_index=max_index, platform_dict=url_module.get_platform_dict(),
                                current_index=current_index, separate_count=separate_count,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                url_data=url_data)
        else:
            """编辑链接"""
            the_type = request.form.get("the_type")
            message = {"message": "success"}
            if the_type == "add":
                """获取可用选择的团队成员"""
                url = request.form.get('url')
                url_name = request.form.get('url_name')
                company_sn = request.form.get('company_sn')
                channel_sn = request.form.get('channel_sn')
                pattern_sn = request.form.get('pattern_sn')
                platform_sn = request.form.get('platform_sn')
                is_3th = request.form.get('is_3th')
                args = {"url": url, "url_name": url_name, "channel_sn": channel_sn, "pattern_sn": pattern_sn,
                        "company_sn": company_sn, "platform_sn": platform_sn, "is_3th": is_3th}
                message = url_module.add(**args)
            elif the_type == "edit":
                url = request.form.get('url')
                sn = request.form.get('sn')
                url_name = request.form.get('url_name')
                company_sn = request.form.get('company_sn')
                channel_sn = request.form.get('channel_sn')
                pattern_sn = request.form.get('pattern_sn')
                platform_sn = request.form.get('platform_sn')
                is_3th = request.form.get('is_3th')
                args = {"url": url, "url_name": url_name, "channel_sn": channel_sn, "pattern_sn": pattern_sn,
                        "company_sn": company_sn, "platform_sn": platform_sn, "is_3th": is_3th, "sn": sn}
                message = url_module.edit(**args)
            elif the_type == "delete":
                sn = request.form.get('sn')
                args = {'sn': sn}
                message = url_module.delete(**args)
            else:
                message['message'] = "不理解的操作"
            return resp_json(message)
    elif key == "excel":
        """导出"""
        if request.method == "GET":
            excel_list = customer_module.show_excel(0)
            excel_count = len(excel_list)
            months = list(range(1, 13))
            companys = customer_module.show_process_excel_list()
            return jinja.render("admin_excel.html", v=excel_count, request=request, excel_list=excel_list,
                                months=months, companys=companys, company_sn=0)
        else:
            the_type = request.form.get("the_type")
            message = {"message": "success"}
            if the_type == "export":
                """导出ｅｘｃｅｌ的请求"""
                begin = request.form.get("begin")
                end = request.form.get("end")
                customer_module.export_customer(0, begin, end)
            elif the_type == "delete":
                file_name = request.form.get("file_name")
                message = customer_module.delete_excel(0, file_name)
            elif the_type == "set_status":
                """修改对excel的操作权限"""
                company_sn = request.form.get("sn")
                status_code = request.form.get("status_code")
                try:
                    company_sn = int(company_sn)
                    status_code = int(status_code)
                    message = customer_module.set_process_excel_status(company_sn, status_code)
                except TypeError as e:
                    print(e)
                    message['message'] = "参数错误:{},{}".format(company_sn, status_code)
                except ValueError as e:
                    print(e)
                    message['message'] = "参数错误:{},{}".format(company_sn, status_code)
            else:
                message['message'] = "未知请求"
            return resp_json(message)


@app.route("/company/<key:string>", methods=["POST", "GET"])
async def my_company(request, key):
    """分公司后台管理模块"""
    sn = request['session']['sn']  # 这个sn是公司的sn
    if key == "user":
        """客户管理"""
        if request.method == "GET":
            """取翻页前缀"""
            url_path = request.path
            args = request.raw_args
            try:
                args.pop("index")
            except KeyError as e:
                print(e)
            finally:
                temp = "?"
                for k, v in args.items():
                    temp += "{}={}&".format(k, v)
                url_path += temp
            """取过滤关键词,用于只显示customer_description匹配的用户"""
            key_word_str = request.args.get("key_word", None)
            if key_word_str is None:
                key_word_list = list()
            else:
                key_word_list = [x.strip() for x in key_word_str.split(" ")]  # 用于查询客户档案时过滤customer_description
            filter_dict = {"customer_description": key_word_list}  # 统计人数时的额外筛选器
            the_type = request.args.get("the_type", "all")  # 查询用户的条件，默认是all
            customer_count = customer_module.customer_count(the_type, sn=sn,
                                                            filter_dict=filter_dict)  # 统计总数
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(customer_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            # 取用户数据  page(the_type="all", index=1, length=30, term=''):
            args = {
                "the_type": the_type, "index": current_index, "length": page_length,
                "sn": sn, "key_word_list": key_word_list
            }
            customer_data = customer_module.page(**args)
            company_count = customer_module.count_by_company_name(0, filter_dict=filter_dict)  # 按分公司统计数量
            member_dict = team_module.sn_name(sn)
            return jinja.render("admin_user_company.html",
                                request=request, company_count=company_count,
                                customer_count=customer_count, member_dict=member_dict,
                                index_range=index_range, key_word_str='' if key_word_str is None else key_word_str,
                                max_index=max_index, url_path=url_path,
                                current_index=current_index,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                customer_data=customer_data)
        else:
            """编辑客户信息"""
            the_type = request.form.get("the_type")
            user_sn = request.form.get("user_sn")
            team_sn = request.form.get("team_sn")
            args = {"the_type": the_type, "user_sn": user_sn, "team_sn": team_sn, "company_sn": sn}
            message = customer_module.edit_customer(**args)
            return resp_json(message)

    elif key == "position":
        """职务管理"""
        company_sn = request['session']['sn']
        if request.method == "GET":
            position_count = position_module.position_count(company_sn=company_sn)  # 统计总数
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(position_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            args = {"company_sn": company_sn, "index": current_index, "length": page_length}
            position_data = position_module.page(**args)
            k_v = {x['sn']: x['position_name'] for x in position_data}
            return jinja.render("admin_position_company.html",
                                request=request, k_v=k_v,
                                position_count=position_count,
                                index_range=index_range,
                                max_index=max_index,
                                current_index=current_index,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                position_data=position_data)
        else:
            """编辑职务信息"""
            message = {'message': 'success'}
            the_type = request.form.get("the_type")
            sn = request.form.get("sn")
            position_name = request.form.get("position_name")
            parent_sn = request.form.get("parent_sn")
            has_team = request.form.get("has_team")
            sn = request.form.get("sn")
            args = {"sn": sn, "position_name": position_name, "parent_sn": parent_sn,
                    "company_sn": company_sn, "has_team": has_team}
            if args['parent_sn'] == '' or args['parent_sn'] is None:
                args['parent_sn'] = 0

            if the_type == "add":
                args.pop("sn")
                message = position_module.add(**args)
            elif the_type == "edit":
                message = position_module.edit(**args)
            elif the_type == "delete":
                message = position_module.delete(**args)
            else:
                message['message'] = '不支持的操作'
            return resp_json(message)

    elif key == "employee":
        """员工管理"""
        company_sn = request['session']['sn']
        if request.method == "GET":
            employee_count = employee_module.Employee.count(company_sn=company_sn)  # 统计总数
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(employee_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            args = {"company_sn": company_sn, "index": current_index, "length": page_length}
            employee_data = employee_module.Employee.page(**args)
            k_v = team_module.sn_name(company_sn)
            k_v2 = position_module.sn_name(company_sn)
            return jinja.render("admin_employee_company.html",
                                request=request, k_v=k_v, k_v2=k_v2,
                                employee_count=employee_count,
                                index_range=index_range,
                                max_index=max_index,
                                current_index=current_index,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                employee_data=employee_data)
        else:
            """编辑员工信息"""
            message = {'message': 'success'}
            the_type = request.form.get("the_type")
            sn = request.form.get("sn")
            real_name = request.form.get("real_name")
            user_phone = request.form.get("user_phone")
            team_sn = request.form.get("team_sn", 0)
            position_sn = request.form.get("position_sn")
            user_mail = request.form.get("user_mail")
            born_date = request.form.get("born_date")

            args = {"sn": sn, "real_name": real_name, "user_phone": user_phone,
                    "team_sn": team_sn, "position_sn": position_sn, "user_mail": user_mail,
                    "born_date": born_date, "company_sn": company_sn}
            args = {k: v for k, v in args.items() if v is not None}

            if the_type == "add":
                message = employee_module.Employee.create(**args)
            elif the_type == "edit":
                message = employee_module.Employee.edit(**args)
            elif the_type == "delete":
                args = {"sn": sn, "company_sn": company_sn}
                message = employee_module.Employee.delete(**args)
            else:
                message['message'] = '不支持的操作'
            return resp_json(message)

    elif key == "team":
        """团队管理"""
        company_sn = request['session']['sn']
        if request.method == "GET":
            team_count = team_module.team_count(company_sn=company_sn)  # 统计总数
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(team_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            args = {"company_sn": company_sn, "index": current_index, "length": page_length}
            team_data = team_module.page(**args)
            for team in team_data:
                team['member_count'] = employee_module.Employee.count(company_sn, team['sn'])
            k_v = employee_module.Employee.sn_name(company_sn, manager=True)
            return jinja.render("admin_team_company.html",
                                request=request, k_v=k_v,
                                team_count=team_count,
                                index_range=index_range,
                                max_index=max_index,
                                current_index=current_index,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                team_data=team_data)
        else:
            """编辑团队信息"""
            message = {'message': 'success'}
            the_type = request.form.get("the_type")
            sn = request.form.get("sn")
            team_name = request.form.get("team_name")
            leader_sn = request.form.get("leader_sn")
            sn = request.form.get("sn")
            args = {"sn": sn, "team_name": team_name, "leader_sn": leader_sn,
                    "company_sn": company_sn}

            if the_type == "add":
                try:
                    args.pop("sn")
                except KeyError:
                    pass
                message = team_module.add(**args)
            elif the_type == "edit":
                message = team_module.edit(**args)
            elif the_type == "delete":
                message = team_module.delete(**args)
            else:
                message['message'] = '不支持的操作'
            return resp_json(message)

    elif key == "plan":
        """分配计划管理"""
        if request.method == "GET":
            plan_count = plan_module.plan_count(sn)  # 统计总数
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(plan_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            args = {"index": current_index, "length": page_length, "term": 'owner_sn', "key_word": sn}
            plan_count_data = plan_module.page(**args)['data']
            member_dict = plan_module.get_members(sn)
            default_plan = None  # 默认分配计划
            for x in plan_count_data:
                if x['sn'] == 1:
                    default_plan = x
                    plan_count_data.remove(x)
                    break
            return jinja.render("admin_plan_company.html",
                                request=request, member_dict=member_dict,
                                plan_count=plan_count, default_plan=default_plan,
                                index_range=index_range,
                                max_index=max_index,
                                current_index=current_index,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                plan_count_data=plan_count_data)
        else:
            """编辑分配计划"""
            the_type = request.form.get("the_type")
            message = {"message": "error"}
            if the_type == "get_members":
                """获取可用选择的团队成员"""
                member_dict = plan_module.get_members(sn)
                message['data'] = member_dict
            elif the_type in ["add", "edit", "delete", "up", "down"]:
                key_list = list(request.form.keys())
                args = dict()
                member_list = list()
                for key in key_list:
                    val = request.form.get(key)
                    if key == "member_list":
                        val = json.loads(val)
                    else:
                        pass
                    args[key] = val
                    args['owner_sn'] = sn
                    member_list = list() if args.get("member_list") is None else args.get("member_list")
                if len(member_list) == 0 and the_type not in ["delete", "up", "down"]:
                    message['message'] = "没有团队成员无法创建分配策略"
                else:
                    result = plan_module.process(**args)
                    message = result
            elif the_type == "get_item":
                """根据plan_sn获取成员信息"""
                sn = request.form.get("plan_sn")
                message = plan_module.get_plan_item(sn)
            else:
                message['message'] = "不理解的操作"
            return resp_json(message)
    elif key == "excel":
        """导出"""
        if request.method == "GET":
            excel_list = customer_module.show_excel(sn)
            excel_count = len(excel_list)
            months = list(range(1, 13))
            return jinja.render("admin_excel_company.html", v=excel_count, request=request, excel_list=excel_list,
                                months=months, company_sn=sn)
        else:
            the_type = request.form.get("the_type")
            message = {"message": "success"}
            if the_type == "export":
                """导出ｅｘｃｅｌ的请求"""
                begin = request.form.get("begin")
                end = request.form.get("end")
                flag = customer_module.can_process_excel(sn)
                if flag is None:
                    message['message'] = "权限不足"
                else:
                    customer_module.export_customer(sn, begin, end)
            elif the_type == "delete":
                file_name = request.form.get("file_name")
                flag = customer_module.can_process_excel(sn)
                if flag is None:
                    message['message'] = "权限不足"
                else:
                    message = customer_module.delete_excel(sn, file_name)
            else:
                message['message'] = "未知请求"
            return resp_json(message)


@app.route("/employee/<key:string>", methods=["POST", "GET"])
async def my_company(request, key):
    """员工页面模块"""
    user_phone = request['session']['user_phone']
    team_sn = request['session']['team_sn']
    company_sn = request['session']['company_sn']
    employee_sn = request['session']['employee_sn']
    if key == "user":
        """资源列表"""
        if request.method == "GET":
            customer_count = 0
            customer_data = list()
            if team_sn != -1:
                customer_count = customer_module.count_all_my_customer(team_sn)  # 统计总数
            else:
                customer_count = customer_module.count_all_my_customer(employee_sn)  # 统计总数
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(customer_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            member_dict = employee_module.Team.children_sn_name(employee_sn)
            if team_sn != -1:
                args = {"company_sn": company_sn, "index": current_index, "length": page_length, "team_sn": team_sn}
                customer_data = customer_module.page_by_team_sn(**args)
            else:
                args = {"index": current_index, "length": page_length, "employee_sn": employee_sn}
                customer_data = customer_module.page_by_employee_sn(**args)

            return jinja.render("admin_user_employee.html",
                                request=request,
                                customer_count=customer_count, member_dict=member_dict,
                                index_range=index_range,
                                max_index=max_index,
                                current_index=current_index,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                customer_data=customer_data)
        else:
            """编辑客户信息"""
            the_type = request.form.get("the_type")
            user_sn = request.form.get("user_sn")
            employee_sn = request.form.get("employee_sn")
            args = {"the_type": the_type, "user_sn": user_sn, "employee_sn": employee_sn, "company_sn": company_sn}
            message = customer_module.edit_customer(**args)
            return resp_json(message)

    elif key == "my_customer":
        """我的客户"""
        if request.method == "GET":
            customer_count = track_module.count(employee_sn)
            customer_data = list()
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(customer_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            member_dict = employee_module.Employee.sn_name_in_company(company_sn)
            args = {"index": current_index, "length": page_length, "employee_sn": employee_sn}
            customer_data = track_module.page(**args)
            my_name = member_dict[employee_sn]
            track_type = track_module.get_track_type()
            return jinja.render("my_customer.html",
                                request=request, team_sn=team_sn, my_name=my_name,
                                customer_count=customer_count, member_dict=member_dict,
                                index_range=index_range, track_type=track_type,
                                max_index=max_index,
                                current_index=current_index,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                customer_data=customer_data)

    elif key == "plan":
        """分配计划管理"""
        if request.method == "GET":
            plan_count = plan_module.plan_count(team_sn)  # 统计总数
            current_index = int(request.args.get("index", 1))  # 当前页码
            page_length = int(request.args.get("page_length", 20))  # 每页多少记录
            max_index = math.ceil(plan_count / page_length)  # 最大页码
            if max_index < current_index:
                current_index = max_index
            if 1 > current_index:
                current_index = 1
            """每页显示5个可点击页码"""
            range_min = current_index - 2 if current_index > 2 else 1
            rang_max = max_index if (range_min + 4) > max_index else (range_min + 4)
            index_range = [x for x in range(range_min, rang_max + 1)]
            args = {"index": current_index, "length": page_length, "term": 'owner_sn', "key_word": team_sn}
            plan_count_data = plan_module.page(**args)['data']
            member_dict = plan_module.get_team_members(team_sn)
            default_plan = None  # 默认分配计划
            for x in plan_count_data:
                if x['sn'] == 1:
                    default_plan = x
                    plan_count_data.remove(x)
                    break
            return jinja.render("admin_plan_employee.html",
                                request=request, member_dict=member_dict,
                                plan_count=plan_count, default_plan=default_plan,
                                index_range=index_range,
                                max_index=max_index,
                                current_index=current_index,
                                prev_index=current_index if (current_index - 1) > 1 else 1,
                                next_index=current_index + 1 if (current_index + 1) < max_index else max_index,
                                plan_count_data=plan_count_data)
        else:
            """编辑分配计划"""
            the_type = request.form.get("the_type")
            message = {"message": "error"}
            if the_type == "get_members":
                """获取可用选择的团队成员"""
                member_dict = plan_module.get_members(team_sn)
                message['data'] = member_dict
            elif the_type in ["add", "edit", "delete", "up", "down"]:
                key_list = list(request.form.keys())
                args = dict()
                for key in key_list:
                    val = request.form.get(key)
                    if key == "member_list":
                        val = json.loads(val)
                    else:
                        pass
                    args[key] = val
                    args['owner_sn'] = team_sn
                    member_list = list() if args.get("member_list") is None else args.get("member_list")
                if len(member_list) == 0 and the_type not in ["delete", "up", "down"]:
                    message['message'] = "没有团队成员无法创建分配策略"
                else:
                    result = plan_module.process(**args)
                    message = result
            elif the_type == "get_item":
                """根据plan_sn获取成员信息"""
                sn = request.form.get("plan_sn")
                message = plan_module.get_plan_item(sn)
            else:
                message['message'] = "不理解的操作"
            return resp_json(message)


@app.route("/send_sms", methods=['POST', 'GET'])
async def send_sms_func(request):
    """短信接口"""
    phone = request.args.get("user_phone") if request.form.get("user_phone") is None else \
        request.form.get("user_phone")
    result = sms_module.send_sms(phone)
    resp = response.json(result, headers={"Access-Control-Allow-Origin": "*"})
    return resp


@app.route("/register_demo.html", methods=['GET'])
async def register_demo_func(request):
    """通用注册脚本使用的示范页"""
    if request.method.lower() == "get":
        phone = request.args.get("phone") if request.form.get("phone") is None else \
            request.form.get("phone")
        if phone == "15618317376":
            return jinja.render("register_demo.html", request=request)
        else:
            raise NotFound("page not find!", status_code=404)
    else:
        raise NotFound("page not find!", status_code=405)


@app.route("/register", methods=['POST', 'GET'])
async def my_register(request):
    """注册接口"""
    sms_code = request.form.get("sms_code") if request.args.get("sms_code") is None else request.args.get("sms_code")
    user_name = "" if request.form.get("user_name") == "" else ('' if request.form.get("user_name") is None else request.form.get("user_name"))
    user_phone = request.args.get("user_phone") if request.args.get("user_phone") is not None \
        else request.form.get("user_phone")
    customer_description = request.form.get("customer_description")
    customer_description = "" if customer_description is None else customer_description
    page_url = "" if request.headers.get('referer') is None else request.headers.get('referer')
    args = {"user_name": user_name, "user_phone": user_phone, "page_url": page_url,
            "customer_description": customer_description}
    print(args)
    result = sms_module.check_sms_code(phone=user_phone, sms_code=sms_code)
    if result:
        """短信验证成功,可以注册"""
        print("短信验证成功,可以注册")
        result = customer_module.add_user(**args)
    else:
        result = {'message': "短信验证失败"}
    resp = response.json(result, headers={"Access-Control-Allow-Origin": "*"})
    logger.exception(resp.headers)
    print(resp.headers)
    return resp


@app.route("/register2", methods=['POST', 'GET'])
async def my_register2(request):
    """今日头条自助建站注册接口.停止使用"""
    raise NotFound("page not find!", status_code=404)
    args = request.args
    form = request.form
    data = json.loads(form['data'][0])['data']
    user_name = None
    user_phone = None
    for x in data:
        if x['label'] == '姓名':
            user_name = x['value']
        elif x['label'] == '电话':
            user_phone = x['value']
        else:
            pass

    customer_description = ""
    page_url = "http://www.toutiaopage.com/"
    args = {"user_name": user_name, "user_phone": user_phone, "page_url": page_url,
            "customer_description": customer_description}
    result = customer_module.add_user(**args)
    resp = response.json(result, headers={"Access-Control-Allow-Origin": "*"})
    return resp


@app.route("/sms_test")
async def sms_test_func(request):
    """短信测试页面,只能使用127.0.0.1这个地址访问"""
    ip = request.ip[0]
    if ip != "127.0.0.1":
        raise NotFound("page not find!", status_code=404)
    else:
        return jinja.render("sms_test.html", request=request)


@app.route("/show_black_ip_list", methods=['POST', 'GET'])
async def show_black_ip_list_func(request):
    """查看ip黑名单"""
    cache_key = "black_ip_list"
    clear_list = request.form.get("clear_list") if request.args.get("clear_list") is None \
        else request.args.get("clear_list")
    if clear_list == "True":
        cache.set(cache_key, list())
        result = {"message": "success"}
    else:
        result = cache.get(cache_key)
    resp = response.json(result, headers={"Access-Control-Allow-Origin": "*"})
    return resp


@app.route("/example")
async def my_example(request):
    return jinja.render("example.html", request=request)


@app.exception(NotFound)
def ignore_404s(request, exception):
    return text("页面没找到，url {}".format(request.url))


@app.middleware('request')
async def check_admin_session(request):
    """对管理员进行身份检查"""
    path = request.path
    need_check = [r"/manage/\w{2,20}"]
    flag = False
    for key in need_check:
        if re.fullmatch(key, path):  # 需要验证的
            flag = True
            break
    if flag:
        """从request取出session字典，注意await"""
        session_dict = await session_interface.open(request)
        try:
            user_name = session_dict.get("user_name", "")
            user_password = session_dict.get("user_password", "")
            message = admin_module.check_login(user_name, user_password)
            if message['message'] == "success":
                pass
            else:
                return redirect(app.url_for("admin_login"))
        except KeyError:
            return redirect(app.url_for("admin_login"))
    else:
        pass


@app.middleware('request')
async def check_company_session(request):
    """对公司登录进行身份检查"""
    path = request.path
    need_check = [r"/company/\w{2,20}"]
    flag = False
    for key in need_check:
        if re.fullmatch(key, path):  # 需要验证的
            flag = True
            break
    if flag:
        """从request取出session字典，注意await"""
        session_dict = await session_interface.open(request)
        try:
            user_name = session_dict.get("user_name", "")
            user_password = session_dict.get("user_password", "")
            message = company_module.check_login(user_name, user_password)
            if message['message'] == "success":
                pass
            else:
                return redirect(app.url_for("company_login"))
        except KeyError:
            return redirect(app.url_for("company_login"))
    else:
        pass


@app.middleware('request')
async def check_employee_session(request):
    """对员工登录进行身份检查"""
    path = request.path
    need_check = [r"/employee/\w{2,20}"]
    flag = False
    for key in need_check:
        if re.fullmatch(key, path):  # 需要验证的
            flag = True
            break
    if flag:
        """从request取出session字典，注意await"""
        session_dict = await session_interface.open(request)
        try:
            user_phone = session_dict.get("user_phone", "")
            user_password = session_dict.get("user_password", "")
            message = employee_module.check_login(user_phone, user_password)
            if message['message'] == "success":
                pass
            else:
                return redirect(app.url_for("employee_login"))
        except KeyError:
            return redirect(app.url_for("employee_login"))
    else:
        pass


@app.middleware('request')
async def check_download_excel(request):
    """对下载excel的行为进行权限检查"""
    url = request.url
    pattern = re.compile(r'^http://.{9,100}/static/downloads/excel/\d+/.+\.xls$')
    """匹配下载excel文件的路径"""
    if pattern.match(url):
        """从会话取身份信息"""
        session_dict = await session_interface.open(request)
        if "sn" in session_dict:
            company_sn_session = session_dict['sn']
            """从url取公司sn"""
            company_sn_url = url.split("/static/downloads/excel/", 1)[1].split("/")[0]
            try:
                company_sn_url = int(company_sn_url)
            except ValueError as e:
                print(e)
                company_sn_url = -1
            except TypeError as e:
                print(e)
                company_sn_url = -1
            finally:
                if company_sn_url == company_sn_session:
                    """开始查询数据库检查"""
                    flag = customer_module.can_process_excel(company_sn_session)
                    if flag is None:
                        return redirect(app.url_for("company_login"))
                    else:
                        pass
                else:
                    return redirect(app.url_for("company_login"))
        else:
            return redirect(app.url_for("company_login"))
    else:
        pass


@app.middleware('request')
async def check_register(request):
    """对用户注册进行安全检查"""
    request_path = request.path
    ip = request.ip[0]
    method = request.method
    headers = str(request.headers)
    args = str(request.args)
    form = str(request.form)
    info_dict = {
        "request_path": request_path,
        "ip": ip,
        "method": method,
        "headers": headers,
        "args": args,
        "form": form
    }
    logger.exception(str(info_dict))
    if 1:
        pass  # 关闭防火墙
    else:
        if request.path == "/show_black_ip_list":
            pass
        else:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
            cache_key = "black_ip_list"
            """检查ip是否在黑名单内"""
            back_ip_list = cache.get(cache_key)
            if back_ip_list is None:
                back_ip_list = list()
                cache.set(key=cache_key, value=back_ip_list, timeout=60 * 60 * 24 * 12)
            else:
                if ip in back_ip_list:
                    a_str = "{} 非法访问： ip:{}".format(now_str, ip)
                    back_ip_txt.write(a_str)
                    back_ip_txt.flush()

                    logger.info(a_str)
                    raise NotFound("page not find!", status_code=404)
                else:
                    pass
            path = request.path
            need_check = [r"/register\w*"]
            flag = False
            for key in need_check:
                if re.fullmatch(key, path):  # 需要验证的
                    flag = True
                    break
            if flag:
                referer = '' if request.headers.get('referer') is None else request.headers['referer']
                user_name = "" if request.form.get("user_name") is None else request.form.get("user_name")
                user_phone = "" if request.form.get("user_phone") is None else request.form.get("user_phone")
                user_phone = user_phone.strip()
                if ip.startswith("127") or ip.startswith("192"):
                    pass
                else:
                    if not check_phone(user_phone) or not validate_arg(user_name, "_") or referer == '':
                        back_ip_list = cache.get(cache_key)
                        if back_ip_list is None:
                            back_ip_list = list()
                        else:
                            pass
                        if ip not in back_ip_list:
                            back_ip_list.append(ip)
                            cache.set(key=cache_key, value=back_ip_list, timeout=60 * 60 * 24)  # 拉黑24小时
                        else:
                            pass
                        args = {"user_name": user_name, "user_phone": user_phone, "referer": referer, "ip": ip}
                        a_str = "{} 非法注册2： args:{}".format(now_str, str(args))
                        back_ip_txt.write(a_str)
                        back_ip_txt.flush()
                        logger.info(a_str)
                        raise NotFound("page not find!", status_code=404)
                    else:
                        pass
            else:
                pass


@app.middleware('request')
async def add_session_to_request(request):
    # before each request initialize a session
    # using the client's request
    await session_interface.open(request)


@app.middleware('response')
async def save_session(request, response):
    # after each request save the session,
    # pass the response to set client cookies
    await session_interface.save(request, response)


if __name__ == "__main__":
    app.run(host=host, port=port, debug=True, workers=2, log_config=LOGGING)
    # app.run(host=host, port=port, debug=True, workers=2)
