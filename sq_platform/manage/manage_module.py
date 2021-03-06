# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, Blueprint, abort, make_response
from flask import send_file
from flask_wtf.form import FlaskForm
import os
from api.data.item_module import GPS
from tools_module import *
import amap_module
import random
import math
import json
import json.decoder
from io import BytesIO
from manage.company_module import *
from api.data.item_module import User
from api.data.item_module import Track
from log_module import get_logger
from api.user import security_module
from werkzeug.contrib.cache import RedisCache
from mongo_db import get_datetime_from_str
from api.data.violation_module import ViolationRecode
from api.data.violation_module import Penalty
from role.role_module import Role
from role.role_module import Func
from api.data.accident_module import AccidentData
from api.data.accident_module import Accident
from manage.company_module import Employee

"""管理页面模块/后台管理/登录"""

manage_blueprint = Blueprint("manage_blueprint", __name__, url_prefix="/manage", template_folder="templates/manage")
logger = get_logger()
cache = RedisCache()


@manage_blueprint.route("/hello", methods=['post', 'get'])
def hello():
    form = FlaskForm()
    if request.method.lower() == "get":
        # return render_template("hello_world.html", form=form)
        return render_template("manage/base_template_light.html", form=form)
    else:
        if form.validate_on_submit():
            return "ok"
        else:
            return "404"


@manage_blueprint.route("/app_version_table", methods=['get', 'post'])
def app_version_table_func():
    """查看版本汇总信息"""
    if request.method.lower() == "get":
        return render_template("manage/app_version_table.html", )
    elif request.method.lower() == "post":
        app_versions = User.app_version_list()
        app_versions.sort(key=lambda obj: datetime.datetime.strptime(
            "1970-10-10 00:00:00" if obj.get("last_update") is None else obj.get("last_update"), "%Y-%m-%d %H:%M:%S"),
                          reverse=True)

        """计算统计信息"""
        version_dict = {}
        for user in app_versions:
            version = "too old" if user.get('app_version') is None else user.get('app_version')
            if version not in version_dict:
                version_dict[version] = 1
            else:
                count = version_dict[version]
                version_dict[version] = count + 1
        res = {"list": app_versions, "dict": version_dict}
        resp = make_response(json.dumps(res))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        resp.headers['Access-Control-Allow-Headers'] = allow_headers
        return resp
    else:
        return abort(405)


@manage_blueprint.route("/online_report")
@check_platform_session
@log_request_args
def online_report_view_func():
    """观察员的在线报告页面"""
    company_id = get_platform_session_arg("company_id", None)
    if company_id is None:
        return redirect(url_for("manage_blueprint.login_func"))
    else:
        """在线状态过滤器,0表示全部, 1/在线,-1/离线"""
        filter_online = get_arg(request, "filter_online", 0)
        if isinstance(filter_online, str) and filter_online.isdigit():
            filter_online = int(filter_online)
        company = Company.find_by_id(company_id)
        resp = company.online_report(filter_online=filter_online)
        return render_template("manage/online_report.html", data=resp)


@manage_blueprint.route("/online")
@check_platform_session
@log_request_args
def online_report_func():
    """管理员的在线报告页面"""
    company_id = get_platform_session_arg("company_id", None)
    if company_id is None:
        return redirect(url_for("manage_blueprint.login_func"))
    else:
        head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
        """在线状态过滤器,0表示全部, 1/在线,-1/离线"""
        filter_online = get_arg(request, "filter_online", 0)
        if isinstance(filter_online, str) and filter_online.isdigit():
            filter_online = int(filter_online)
        company = Company.find_by_id(company_id)
        resp = company.online_report(filter_online=filter_online)
        return render_template("manage/online_report_light.html", data=resp, head_img_url=head_img_url)


@manage_blueprint.route("/block_employee_list", methods=['get', 'post'])
@check_platform_session
def block_employee_list_func():
    """用户管理屏蔽列表的页面"""
    user_id = get_platform_session_arg("user_id")
    company_id = get_platform_session_arg("company_id")
    head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
    user = Employee.find_by_id(user_id)
    block_list = Employee.get_block_id_list(user_id, to_str=True)
    if request.method.lower() == "get" and isinstance(user, Employee):
        company_dbref = user.get_attr("company_id")
        if company_dbref is None:
            post_dict, dept_dict = {}, {}
        else:
            company_id = company_dbref.id
            post_dict = Company.all_post(company_id)
            dept_dict = Company.all_dept(company_id, can_json=True)
        employee_list = Company.all_employee(company_id=company_id, can_json=True)
        current_user_name = user.get_attr("phone_num") if user.get_attr("real_name", "") == '' \
            else user.get_attr("real_name", "")
        return render_template("manage/block_employee_list.html", block_list=block_list, employee_list=employee_list,
                               post_dict=post_dict, dept_dict=dept_dict, current_user_name=current_user_name,
                               head_img_url=head_img_url)
    elif request.method.lower() == "get" and not isinstance(user, Employee):
        return redirect(url_for("manage_blueprint.login_func"))
    elif user is None:
        return json.dumps({"message": "错误的sid"})
    elif request.method.lower() == "post" and isinstance(user, Employee):
        """用户的post请求"""
        message = {"message": "success"}
        action = get_arg(request, "action", None)
        if action == "base_info":
            """获取基础信息,用于填充页面"""
            company_dbref = user.get_attr("company_id")
            if company_dbref is None:
                post_dict, dept_dict = {}, {}
            else:
                post_dict = Company.all_post(company_id)
                dept_dict = Company.all_dept(company_id, can_json=True)
            employee_list = Company.all_employee(company_id, can_json=True)
            current_user_name = user.get_attr("phone_num") if user.get_attr("real_name", "") == '' \
                else user.get_attr("real_name", "")
            data = {
                "block_list": block_list, "employee_list": employee_list,
                "post_dict": post_dict, "dept_dict": dept_dict, "current_user_name": current_user_name
            }
            message['data'] = data
        elif action == "edit":
            """向阻止列表添加或者删除用户"""
            block_id = get_arg(request, "block_id", None)
            if isinstance(block_id, str) and len(block_id) == 24:
                if block_id in block_list:
                    message = Employee.remove_block_id(user_id, block_id)
                else:
                    message = Employee.add_block_id(user_id, block_id)
                get_archives_from_cache(current_user_id=user_id, clear=True)  # 清缓存
                key = "all_last_position_{}".format(user_id)
                cache.delete(key=key)  # 清除最后的位置信息的缓存
            else:
                message['message'] = "参数 {} 不合法".format(block_id)
        else:
            message['message'] = "不理解的操作"
        return json.dumps(message)
    else:
        return abort(405)


@manage_blueprint.route("/test_ws_client")
def test_ws_client():
    """web-socket客户端测试页面"""
    return render_template("manage/test_ws_client.html")


@manage_blueprint.route("/<key>_error_code", methods=['post', 'get'])
@check_platform_session
def process_error_code(key):
    if request.method.lower() == "get":
        if key == "show":
            """显示所有的错误代码和注释"""
    return "ok"


@manage_blueprint.route("/login", methods=['post', 'get'])
def login_func():
    """
    登录页,
    针对新振兴项目,现在决定需求如下:
    1. 固定的几个部门/组管理员 手动添加
    2. 权限为基于方法的权限,不再推进基于角色的权限.(基于角色的权限管理暂停)
    3. 不考虑跨域用户
    """
    if request.method.lower() == "get":
        return render_template("manage/login.html")
    elif request.method.lower() == "post":
        """验证用户身份"""
        message = {"message": "success"}
        """取登录参数"""
        user_name = get_arg(request, "user_name", None)
        user_password = get_arg(request, "user_password", None)
        if user_name is None or user_name == '' or user_password == '' or user_password is None:
            message['message'] = '用户名或密码不能为空'
        else:
            user_password = user_password.lower()
            """登录参数合法,开始验证"""
            args = {"user_name": user_name}
            admin = CompanyAdmin.find_one_plus(filter_dict=args, instance=False)
            if admin is None:
                message['message'] = "用户名不存在或手机未注册"
            else:
                if user_password != admin['user_password']:
                    message['message'] = "密码错误"
                elif admin.get("user_status") != 1:
                    message['message'] = "账户未启用"
                else:
                    """登录成功,写入会话"""
                    args['user_id'] = str(admin['_id'])  # 写入用户id的str格式.
                    args['user_password'] = user_password
                    args['company_id'] = str(admin['company_id'].id)
                    only_view = admin.get("only_view", "True")
                    args['only_view'] = only_view
                    message['only_view'] = only_view
                    save_platform_session(**args)

        return json.dumps(message)
    else:
        return abort(400, "unknown request")


@manage_blueprint.route("/register", methods=['post', 'get'])
def register_func():
    """注册页"""
    if request.method.lower() == "get":
        login_title = '注册页'
        return render_template("manage/register.html", login_title=login_title)
    elif request.method.lower() == "post":
        """检查register"""
        message = {"message": "success"}
        phone_num = get_arg(request, "phone_num")
        sms_code = get_arg(request, "sms_code")
        user_password = get_arg(request, "user_password")
        args = {"phone_num": phone_num, "sms_code": sms_code, "user_password": user_password}
        message['data'] = args
        return json.dumps(message)
    else:
        return abort(400, "unknown request")


@manage_blueprint.route("/logout", methods=['get'])
@check_platform_session
def logout_func():
    """平台用户注销函数"""
    if request.method.lower() == "get":
        sid = get_arg(request, "sid", None)
        if sid:
            """跨域用户"""
            clear_platform_cors_session(sid)
            return json.dumps({"message": "success"})
        else:
            clear_platform_session()
            return redirect(url_for("manage_blueprint.login_func"))
    else:
        return abort(400, "unknown request")


@manage_blueprint.route("/track", methods=['get'])
@check_platform_session
def track_page_func():
    """展示用户轨迹页面"""
    head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
    real_name = get_platform_session_arg("real_name")
    if request.method.lower() == "get":
        return render_template("manage/show_track_light.html", head_img_url=head_img_url, real_name=real_name)


@manage_blueprint.route("/subordinates_base_info", methods=['get', 'post'])
@check_platform_session
def subordinates_base_info_func():
    """获取下属的基本身份信息"""
    res = {"message": "success"}
    company_id = get_platform_session_arg("company_id")
    if company_id is None:
        return abort(404, "company_id is none")
    else:
        employees = Company.all_employee(company_id=company_id, can_json=True)
        if employees is not None:
            employees = {
                x['_id']:
                    {
                        "real_name": ("" if x.get("official_name") is None else x['official_name']) if x.get(
                      'real_name') is None else x['real_name'],
                        "employee_number": x.get('employee_number', '')
                    }
                for x in employees}
            res['data'] = employees
    return json.dumps(res)


@manage_blueprint.route("/last_positions", methods=['post'])
@check_platform_session
def last_positions_func() -> dict:
    """
    根据用户id，获取他所能查看的员工的最后的位置信息，注意这里的用户指的是公司管理员
    """
    res = {"message": "success"}
    company_id = get_platform_session_arg("company_id")
    employees = Company.all_employee(company_id=company_id)
    data = list()
    if len(employees) > 0:
        debug = False  # 调试开关,生产环境保持False,调试请置True
        if debug:
            key = "last_position_cache_{}".format(company_id)
            data = cache.get(key)  # 调试用设置
            if data is not None:
                pass
            else:
                data = Track.get_last_position([x['_id'] for x in employees])  # 获取最后的点信息
                data = list(data.values())
                cache.set(key, data, timeout=300)  # 调试用设置
        else:
            data = Track.get_last_position([x['_id'] for x in employees])  # 获取最后的点信息
            data = list(data.values())
    else:
        pass
    res['data'] = data
    return json.dumps(res)


@manage_blueprint.route("/track_info", methods=['post'])
@check_platform_session
def track_info():
    """获取历史轨迹信息的接口"""
    message = {"message": "success", 'data': []}
    ids = get_arg(request, "ids", "[]")
    ids = json.loads(ids)
    if len(ids) == 0:
        pass  # 没有选择司机
    else:
        user_list = [User.find_by_id(user_id) for user_id in ids]
        user_list = [x.get_dbref() for x in user_list if isinstance(x, User)]
        if len(user_list) == 0:
            message['message'] = "用户id错误！"
        else:
            date_list = json.loads(get_arg(request, "date", "[]"))
            end_date = None  # 结束时间
            begin_date = None  # 开始时间
            if len(date_list) == 1:
                begin_date = get_datetime_from_str(date_list[0])
            elif len(date_list) > 1:
                end_date = get_datetime_from_str(date_list[1])
                begin_date = get_datetime_from_str(date_list[0])
            else:
                pass

            if end_date is None or begin_date is None or (end_date - begin_date).total_seconds() > 0:
                data = list()
                count = 0  # 轨迹点计数
                for user_id in user_list:
                    track_dict = Track.get_tracks_list(user_id, begin_date, end_date)
                    temp = dict()
                    temp['user_id'] = str(user_id.id)
                    l = len(track_dict['track_list'])
                    count += l  # 计算track点的数量
                    if l > 100:
                        # 如果轨迹点大于一定的数据,就假设他是有行车事件的
                        filter_dict = {
                            "user_id": user_id,
                            "event_time": {
                                "$lte": end_date,
                                "$gte": begin_date
                            }
                        }
                        events = security_module.DrivingEvent.find_plus(filter_dict=filter_dict, to_dict=True,
                                                                        can_json=True)
                        track_dict['event_list'] = events
                    temp['track_dict'] = track_dict
                    data.append(temp)
                message['data'] = data  # 轨迹点的容器
                message['count'] = count
            else:
                message['message'] = "开始时间必须早于结束时间"
    return json.dumps(message)


@manage_blueprint.route("/<key>_user_info", methods=['post', 'get'])
@check_platform_session
def user_info_func(key) -> str:
    """
    用户信息的获取,编辑跨域用户使用
    :param key:
    :return:
    """
    message = {"message": "success"}
    sid = get_arg(request, "sid", None)
    user_dict = get_platform_cors_session_dict(sid)
    if user_dict:
        user_id = user_dict['user_id']
        user = User.find_by_id(user_id)
        if isinstance(user, User):
            if key == "get":
                """获取用户信息"""
                data = user.to_flat_dict()
                message['data'] = data
            else:
                message['message'] = "未知的请求类型"
        else:
            clear_platform_cors_session(sid)
            message['message'] = "错误的sid"
    else:
        message['message'] = "错误的sid"
    return json.dumps(message)


@manage_blueprint.route("/", methods=['get'])
def index_alas_func():
    """首页重定向"""
    return redirect(url_for("manage_blueprint.index_func"))


@manage_blueprint.route("/index", methods=['get'])
@check_platform_session
def index_func():
    """展示自定义的点的信息，用于实时显示一批司机的信息。后台的首页"""
    if request.method.lower() == "get":
        """返回页面"""
        head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")  # 用户头像
        real_name = get_platform_session_arg("real_name")
        company_id = get_platform_session_arg("company_id")
        return render_template("manage/index_light.html", head_img_url=head_img_url,
                               real_name=real_name, company_id=company_id)
    else:
        return abort(405)


@manage_blueprint.route("/driver", methods=["get"])
@check_platform_session
def driver_func():
    company_id = get_platform_session_arg("company_id")
    employees = Company.get_employee_in_cache(company_id=company_id)
    emp_dict = {x['_id']: x for x in employees}
    if request.method.lower() == "get":
        """司机详情页页"""
        page_title = "司机"
        cur_user_id = get_arg(request, "cur_user_id", None)
        page = get_arg(request, "page", None)
        if cur_user_id is None or cur_user_id not in emp_dict:
            """用户不存在或者用户不在查看范围内"""
            return redirect(url_for("manage_blueprint.login_func"))
        else:
            head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
            cur_user = emp_dict[cur_user_id]  # 被查看用户基本资料
            max_day = mongo_db.last_day_of_month(datetime.datetime.now())
            return render_template("manage/driver_light.html", page_title=page_title, head_img_url=head_img_url,
                               cur_user=cur_user, employees=employees, max_day=max_day)
    else:
        return abort(405)


@manage_blueprint.route("/data_chart", methods=["get"])
@check_platform_session
def data_chart_func():
    company_id = get_platform_session_arg("company_id")
    company_id = ObjectId(company_id)
    emps = Company.get_employee_in_cache(company_id=company_id)
    """计算人数,车辆数,时长"""
    count_person = 0  # 统计人数
    count_truck = 0   # 统计车辆
    count_time = 0  # 驾驶时长,目前的单位是分钟
    for emp in emps:
        count_person += 1
        if emp.get("plate_number"):
            count_truck += 1
        online_time = emp.get("online_time")
        if online_time:
            count_time += online_time if isinstance(online_time, float) else float(online_time)
    hour = int(count_time / 60)  # 小时
    minute = int(count_time % 60)  # 分
    if request.method.lower() == "get":
        """数据报表"""
        page_title = "数据报表"
        step = get_arg(request, 'step', "month")  # 取时间粒度
        end = get_arg(request, 'date', None)  # 取时间
        if end is not None:
            if step == "month":
                end = mongo_db.get_datetime_from_str("{}-1".format(end))
            elif step == "year":
                end = mongo_db.get_datetime_from_str("{}-1-1".format(end))
            else:
                end = mongo_db.get_datetime_from_str(end)

        chart_data = Company.chart_data(company_id=company_id, end=end, step=step)
        head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")  # 用户头像
        reason_dict = Penalty.all_reason()
        return render_template("manage/data_chart_light.html", page_title=page_title, head_img_url=head_img_url,
                               chart_data=chart_data, reason_dict=reason_dict, minute=minute, hour=hour,
                               count_person=count_person, count_truck=count_truck)
    else:
        return abort(405)


@manage_blueprint.route("/driver_detail", methods=["get", "post"])
@check_platform_session
def driver_detail_func():
    """司机详情页.20180606废止,以driver_func替代"""
    current_id = get_platform_session_arg("user_id")
    head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
    real_name = get_platform_session_arg("real_name")
    if request.method.lower() == "get":
        """员工/司机详情"""
        return render_template("manage/driver_detail_light.html", head_img_url=head_img_url, real_name=real_name)
    elif request.method.lower() == "post":
        """根据用户id查询详细档案"""
        if current_id is None:
            current_id = get_platform_cors_session_dict(get_arg(request, "sid"))
        message = {"message": "success"}
        user_id = get_arg(request, "user_id", None)  # 待查询的用户的id
        date_str = get_arg(request, "date", None)  # 查询的日期 2013-12-12
        raw_user_id = user_id
        if user_id is None:
            message['message'] = "用户id不能为空"
        else:
            user_id = mongo_db.get_obj_id(user_id)
            if not isinstance(user_id, ObjectId):
                message['message'] = "错误的用户id:{}".format(raw_user_id)
            else:
                """从缓存中取用户基本资料的数据"""
                member_archives = get_archives_from_cache(current_user_id=str(current_id))
                archive = member_archives.get(user_id)
                if archive is None:
                    message['message'] = "没有查询到相关数据"
                else:
                    message['data'] = archive  # 先添加个人资料部分
                    """查询报告"""
                    report = list()
                    try:
                        report = security_module.SecurityReport.query_report(prefix, str(user_id), date_str)
                    except Exception as e:
                        ms = "args={}".format({"user_id": user_id, "prefix": prefix, "date_str": date_str})
                        message['message'] = "查询异常,没有返回正常的数据"
                        logger.exception("driver_detail_func Error! {}".format(ms))
                        print(e)
                    finally:
                        if len(report) == 0:
                            pass
                        else:
                            """把报告内容附加到档案中"""
                            _source = report[0]['_source']
                            archive['total_mileage'] = _source['drive_distance'].rstrip("km")  # 总里程    公里, 注意,这是个str
                            archive['driving_hours_sum'] = _source['drive_time']  # 总时长    小时
                            archive['max_speed'] = _source['max_speed']  # 最高时速  公里/小时
                            archive['oil_cost'] = _source['oil_cost']  # 油耗     升/百公里
                            archive['reset_time'] = _source['reset_time']  # 休息次数
                            archive['drive_score'] = _source['drive_score']  # 驾驶得分
                            archive['drive_age'] = _source['drive_age']  # 驾龄
                            archive['bad_drive_action'] = _source['bad_drive_action']  # 不良驾驶事件, 字典的数组
                            archive['health'] = _source['health']  # 健康记录, 字典的数组
                            archive['rank'] = _source['drive_rank']  # 排名
                            archive['report_datetime'] = _source['report_datetime'].split("T")[0]  # 报告日期
                            message['data'] = archive
        return json.dumps(message)
    else:
        return abort(405)


@manage_blueprint.route("/driver_list", methods=['post', 'get'])
@check_platform_session
def get_driver_list_func() -> str:
    """
    根据用户session中的身份信息,查询用户的下属信息的列表,如果没有下属信息,那就返回自己的个人信息.
    注意,这里返回的都是简要信息,用于创建列表和侧边栏,详细信息用get_employee_archives接口获取.
    :return: 消息字典的json,其中包含下属身份信息的的列表
    """
    company_id = get_platform_session_arg("company_id")
    employees = Company.get_employee_in_cache(company_id=company_id)
    if request.method.lower() == "post":
        """返回Ajax请求的结果"""
        message = dict()
        message['message'] = "success"
        message['data'] = employees
        return json.dumps(message)
    elif request.method.lower() == "get":
        """返回列表页"""
        head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
        return render_template("manage/driver_list_light.html", drivers=employees, head_img_url=head_img_url)
    else:
        return abort(405)


@manage_blueprint.route("/get_employee_archives", methods=['post', 'get'])
@check_platform_session
def get_employee_archives_func():
    """
    get_employee_list_func 函数的增强版
    根据用户session中的身份信息,查询用户的下属信息的详细档案(包含安全等级和安全报告),如果没有下属信息,那就返回自己的详细档案.
    注意,这里返回的都是详细信息,用于用户管理模块和显示用户详细资料.
    :return: 消息字典的json,其中包含下属档案信息的的列表
    """
    user_id = get_platform_session_arg("user_id")
    raw_user_id = user_id
    message = {"message": "success"}
    if user_id is None:
        message['message'] = "用户id不能为空"
    else:
        user_id = mongo_db.get_obj_id(user_id)
        if not isinstance(user_id, ObjectId):
            message['message'] = "错误的用户id:{}".format(raw_user_id)
        else:
            """临时策略，显示虚拟的数据"""
            key = "employee_archives"
            clear = get_arg(request, "clear")
            if clear:  # 清除旧数据
                cache.delete(key)
                message['message'] = 'clear success'
            else:
                """从缓存取数据"""
                member_archives = get_archives_from_cache(current_user_id=str(user_id))
                archive_list = list(member_archives.values())
                message['data'] = archive_list
    return json.dumps(message)


@manage_blueprint.route("/report_page", methods=["get", "post"])
@check_platform_session
def report_page_func():
    user_id = get_platform_session_arg("user_id")
    head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
    real_name = get_platform_session_arg("real_name")
    if request.method.lower() == "get":
        """报表"""
        page_title = "报表"
        return render_template("manage/report_page.html", page_title=page_title, head_img_url=head_img_url,
                               real_name=real_name)
    elif request.method.lower() == "post":
        """从缓存取虚拟数据"""
        member_archives = get_archives_from_cache(current_user_id=user_id)
        """开始聚合数据"""
        member_count = len(member_archives)  # 人数
        total_time = int(sum([v['driving_hours_sum'] for k, v in member_archives.items()]))
        total_mileage = int(sum([v['total_mileage'] for k, v in member_archives.items()]))
        speed_avg = 0 if total_time == 0 else int(total_mileage / total_time)
        cnt_rapi_acce = sum([v['sum_cnt_rapi_acce'] for k, v in member_archives.items()])
        cnt_shar_turn = sum([v['sum_cnt_shar_turn'] for k, v in member_archives.items()])
        cnt_sudd_brak = sum([v['sum_cnt_sudd_brak'] for k, v in member_archives.items()])
        scr_synt = sum([v['scr_synt'] for k, v in member_archives.items()]) / len(member_archives)
        message = {"message": "success"}
        data = {
            "member_count": member_count,  # 成员统计
            "total_time": total_time,  # 时长统计
            "total_mileage": total_mileage,  # 里程统计
            "speed_avg": speed_avg,  # 平均速度
            "cnt_rapi_acce": cnt_rapi_acce,  # 急加速统计
            "cnt_shar_turn": cnt_shar_turn,  # 急转统计
            "cnt_sudd_brak": cnt_sudd_brak,  # 急刹统计
            "scr_synt": scr_synt  # 平均综合/安全指数
        }
        message['data'] = data
        return json.dumps(message)


def get_archives_from_cache(current_user_id: str, clear: bool = False) -> dict:
    """
    从缓存获取员工档案。这是一个临时函数。
    为了在测试阶段提供下属档案。正式环境中将被移除。
    :param current_user_id: 当前用户id
    :param clear: 是否清除数据
    :return: 数据字典
    """
    """从缓存取虚拟数据"""

    key = "employee_archives_{}".format(current_user_id)
    if clear:
        cache.delete(key)
        return {"message": "success"}
    else:
        member_archives = cache.get(key)
        if member_archives is not None and len(member_archives) > 0:
            # if -1 > 0:
            pass
        else:
            """没有取到缓存的话，就生成一个虚拟数据"""
            # 先获取下属的列表
            user_id = mongo_db.get_obj_id(current_user_id)
            member_id_list = Employee.subordinates_id(user_id)
            if len(member_id_list) == 0:
                member_id_list = [user_id]
            # 先获取用户的档案.
            member_archives = Employee.get_archives_cls(member_id_list)
            if isinstance(member_archives, list) and len(member_archives) > 0:
                """获取到档案了"""
                member_archives = {mongo_db.get_obj_id(x['_id']): x for x in member_archives}
            else:
                member_archives = dict()
                """不在查询安全报告进行,安全报告的统计工作以后由ai模块完成"""
                # """从AI模块查询安全报告"""
                # user_id_str = " ".join([str(x) for x in member_id_list])
                # prefix = get_platform_session_arg("prefix", default_val=None)
                # reports = security_module.SecurityReport.query_report(user_id_str)
                # reports.sort(key=lambda obj: obj['_source']['drive_score'], reverse=True)
                # print(reports)
                # for index, item in enumerate(reports):
                #     """把报告内容附加到档案中"""
                #     user_id = mongo_db.get_obj_id(item['_id'])
                #     archive = member_archives.get(user_id)
                #     archive['rank'] = index + 1  # 排名
                #     _source = item['_source']
                #     archive['total_mileage'] = _source['drive_distance'].rstrip("km")  # 总里程    公里, 注意,这是个str
                #     archive['driving_hours_sum'] = _source['drive_time']               # 总时长    小时
                #     archive['max_speed'] = _source['max_speed']                        # 最高时速  公里/小时
                #     archive['oil_cost'] = _source['oil_cost']                          # 油耗     升/百公里
                #     archive['reset_time'] = _source['reset_time']                      # 休息次数
                #     archive['drive_score'] = _source['drive_score']                    # 驾驶得分
                #     archive['drive_age'] = _source['drive_age']                        # 驾龄
                #     archive['bad_drive_action'] = _source['bad_drive_action']  # 不良驾驶事件, 字典的数组
                #     archive['health'] = _source['health']  # 健康记录, 字典的数组
                """
                不良驾驶事件字典的格式
                {
                  "speeding_drive": {                           # 不良驾驶行为类别：    type:string
                  "datetime" : "2017-12-07T20:00:00",           # 不良驾驶行为发生时间: type:date
                  "longitude" : 121.0,                          # 不良驾驶发生经度：    type: float
                  "latitude" : 23.9,                            # 不良驾驶发生纬度：    type: float
                  "altitude" : 50.0                             # 不良驾驶发生海拔：    type: float
                },
                """

                """
                健康记录字典的格式
                {
                "type":      "heart rate"                               # 心率
                "datetime":  "2017-12-07T20:00:00",                     # 心率时间:date
                "value":     75                                         # 心率值: int
                }
                """

            # 旧的方法,2017-12-19关闭
            # """计算平均综合指数,计算排名"""
            # rank_list = [{
            #     "user_id": k, "scr_synt": round(sum([i.get_attr("scr_synt") for i in v]) / len(v)),
            #     "driving_hours_sum": round(sum([j.get_attr("sum_time") for j in v]) / 60),
            #     "avg_speed": round(sum([j.get_attr("avg_speed") for j in v]) / len(v)),
            #     "sum_cnt_shar_turn":sum([j.get_attr("cnt_shar_turn") for j in v]),
            #     "sum_cnt_sudd_brak":sum([j.get_attr("cnt_sudd_brak") for j in v]),
            #     "sum_cnt_rapi_acce":sum([j.get_attr("cnt_rapi_acce") for j in v]),
            #     "sum_look_phone":sum([j.get_attr("look_phone") for j in v]),
            #     "sum_call_phone":sum([j.get_attr("call_phone") for j in v]),
            #     "total_mileage":sum([j.get_attr("sum_mile") for j in v]),
            #     "avg_emotion_status":round(sum([j.get_attr("emotion_status") for j in v]) / len(v)),
            #     "avg_life_habits":round(sum([j.get_attr("life_habits") for j in v]) / len(v)),
            # } for k, v in reports.items()]
            # rank_list.sort(key=lambda obj: obj['scr_synt'], reverse=True)
            # rank_dict = {}
            # for i, n in enumerate(rank_list):
            #     rank = i + 1
            #     n_id = n.pop('user_id')
            #     n['rank'] = rank
            #     n["reports"] = [x.to_flat_dict() for x in reports[n_id]]
            #     rank_dict[n_id] = n
            # for user_id, archives in member_archives.items():
            #     archives.update(rank_dict[user_id])

            cache.set(key, member_archives, timeout=60 * 60 * 12)
        return member_archives


@manage_blueprint.route("/violation", methods=["get", "post"])
@check_platform_session
def violation_func():
    """违章页面"""

    head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
    """获取基本下属信息,用于身份验证,防止越权查看信息"""
    company_id = get_platform_session_arg("company_id")
    if company_id is None:
        return abort(404, "company_id is none")
    else:
        es = Company.all_employee(company_id=company_id, can_json=False)
        employees = dict()
        eids = list()
        if len(es) > 0:
            for e in es:
                e_id = e['_id']
                o = {
                        "real_name": ("" if e.get("official_name") is None else e['official_name']) if e.get(
                      'real_name') is None else e['real_name'],
                        "employee_number": e.get('employee_number', '')
                    }
                eids.append(e_id)
                employees[str(e_id)] = o
        else:
            pass

        if request.method.lower() == "get":
            """返回页面"""
            a_url = "violation?"  # 待拼接url地址,这里是相对地址
            user_id = get_arg(request, "user_id", None)  # 筛选条件 user_id
            if isinstance(user_id, str) and len(user_id) == 24:
                a_url += "user_id={}".format(user_id)
                user_id = ObjectId(user_id)
            city = get_arg(request, "city", None)
            if city is not None and city != "":
                if a_url.endswith("?"):
                    a_url += "city={}".format(city)
                else:
                    a_url += "&city={}".format(city)
            plate_number = get_arg(request, "plate_number", None)
            if plate_number is not None and plate_number != "":
                if a_url.endswith("?"):
                    a_url += "plate_number={}".format(plate_number)
                else:
                    a_url += "&plate_number={}".format(plate_number)
            vio_status = get_arg(request, "vio_status", None)  # vio_status is None  查询所有类型的违章记录
            ms = "vio_status={}".format(vio_status)
            if vio_status is None:
                pass
            else:
                try:
                    vio_status = int(vio_status)
                except ValueError as e:
                    logger.exception(ms)
                    print(e)
                except TypeError as e:
                    logger.exception(ms)
                    print(e)
                except Exception as e:
                    logger.exception(ms)
                    print(e)
                finally:
                    vio_status = None if not isinstance(vio_status, int) else vio_status
                    if vio_status is not None and vio_status != "":
                        if a_url.endswith("?"):
                            a_url += "vio_status={}".format(vio_status)
                        else:
                            a_url += "&vio_status={}".format(vio_status)
            fine = get_arg(request, "fine", None)
            if fine is not None and fine != "":
                if a_url.endswith("?"):
                    a_url += "fine={}".format(fine)
                else:
                    a_url += "&fine={}".format(fine)
            end_date_str = get_arg(request, "end_date", None)
            end_date = get_datetime_from_str(end_date_str)
            if end_date is None:
                end_date = datetime.datetime.now()
            else:
                if a_url.endswith("?"):
                    a_url += "end_date={}".format(end_date_str)
                else:
                    a_url += "&end_date={}".format(end_date_str)
            begin_date_str = get_arg(request, "begin_date", None)
            begin_date = get_datetime_from_str(begin_date_str)
            if begin_date is None or (begin_date - end_date).total_seconds() >= 0:
                begin_date = end_date - datetime.timedelta(days=1365)
            else:
                if a_url.endswith("?"):
                    a_url += "begin_date={}".format(begin_date_str)
                else:
                    a_url += "&begin_date={}".format(begin_date_str)
            num = get_arg(request, "num", None)
            if num is not None and num != "":
                ms = "num={}".format(num)
                try:
                    num = int(num)
                except ValueError as e:
                    logger.exception(ms)
                    print(e)
                except TypeError as e:
                    logger.exception(ms)
                    print(e)
                except Exception as e:
                    logger.exception(ms)
                    print(e)
                finally:
                    num = 8 if not isinstance(num, int) else num

                if a_url.endswith("?"):
                    a_url += "num={}".format(num)
                else:
                    a_url += "&num={}".format(num)
            else:
                num = 8
            cur_index = get_arg(request, "cur_index", 1)
            ms = "cur_index={}".format(cur_index)
            try:
                cur_index = int(cur_index)
            except ValueError as e:
                logger.exception(ms)
                print(e)
            except TypeError as e:
                logger.exception(ms)
                print(e)
            except Exception as e:
                logger.exception(ms)
                print(e)
            finally:
                cur_index = 1 if not isinstance(cur_index, int) else cur_index
                cur_index = 1 if cur_index < 1 else cur_index
            if a_url.endswith("?"):
                a_url += "cur_index={}"
            else:
                a_url += "&cur_index={}"
            vio_list = list()
            vio_count = 0
            if (user_id is not None and user_id not in eids) or len(eids) == 0:
                """待查看用户不在权限范围内"""
                vio_list = list()
                vio_count = 0  # 违章条数
            else:
                user_id = eids if user_id is None else user_id
                # user_id = None  # 调试时打开,以尽可能多的获取违章记录
                args = {
                    "user_id": user_id,
                    "city": city,
                    "plate_number": plate_number,
                    "vio_status": vio_status,
                    "fine": fine,
                    "end_date": end_date,
                    "begin_date": begin_date,
                    "index": cur_index,
                    "num": num
                }
                data = ViolationRecode.page(**args)
                vio_list = data['data']
                vio_count = data['count']  # 违章条数

            """处理分页"""
            page_count = math.ceil(vio_count / num)  # 共计多少页?
            """确认分页范围"""
            min_index = cur_index - 2
            min_index = 1 if min_index < 1 else min_index
            max_index = cur_index + 2
            max_index = page_count if max_index > page_count else max_index
            index_list = [{"page_num": x, "page_url": a_url.format(x)} for x in list(range(min_index, max_index + 1))]
            prev_page_url = a_url.format((min_index if cur_index - 1 < min_index else cur_index - 1))
            next_page_url = a_url.format((max_index if cur_index + 1 > max_index else cur_index + 1))
            cur_page_url = a_url.format(cur_index)

            """违章状态字典"""
            vio_dict = {"1": "未处理", "2": "处理中", "3": "已处理", "4": "不支持"}
            return render_template("manage/violation_light.html", drivers=employees, pages=index_list,
                                   page_count=page_count, vio_list=vio_list, vio_count=vio_count,
                                   head_img_url=head_img_url, prev_page_url=prev_page_url, next_page_url=next_page_url,
                                   cur_page_url=cur_page_url, vio_status=vio_status, vio_dict=vio_dict)
            pass
        elif request.method.lower() == "post":
            """各种接口"""
            mes = {"message": "success"}
            the_type = get_arg(request, "the_type")
            if the_type == "update_user_id":
                """修改违章记录所有人"""
                vio_id = get_arg(request, "vio_id")
                user_id = get_arg(request, "user_id")
                filter_dict = {"_id": ObjectId(vio_id)}
                user_id = None if user_id == "" else ObjectId(user_id)
                update_dict = {"$set": {"user_id": user_id}}
                ViolationRecode.find_one_and_update_plus(filter_dict=filter_dict, update_dict=update_dict)
                return json.dumps(mes)
            else:
                return abort(403, "不支持的操作")
        else:
            return abort(405, "不支持的操作")


@manage_blueprint.route("/warning", methods=["get", "post"])
@check_platform_session
def warning_func():
    """预警记录页面"""
    head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
    """获取基本下属信息,用于身份验证,防止越权查看信息"""
    company_id = get_platform_session_arg("company_id")
    if company_id is None:
        return abort(404, "company_id is none")
    else:
        employees = Company.all_employee(company_id=company_id, can_json=True)
        if employees is not None:
            employees = {
                x['_id']:
                    {
                        "real_name": ("" if x.get("official_name") is None else x['official_name']) if x.get(
                      'real_name') is None else x['real_name'],
                        "employee_number": x.get('employee_number', '')
                    }
                for x in employees}

        if request.method.lower() == "get":
            """返回页面"""
            a_url = "warning?"  # 待拼接url地址,这里是相对地址
            user_id = get_arg(request, "user_id", None)
            if user_id is not None and user_id != "":
                a_url += "user_id={}".format(user_id)
            tip_status = get_arg(request, "tip_status", None)
            ms = "tip_status={}".format(tip_status)
            if tip_status is not None:
                try:
                    tip_status = int(tip_status)
                except ValueError as e:
                    logger.exception(ms)
                    print(e)
                except TypeError as e:
                    logger.exception(ms)
                    print(e)
                except Exception as e:
                    logger.exception(ms)
                    print(e)
                finally:
                    tip_status = None if not isinstance(tip_status, int) else tip_status
            else:
                pass
            if tip_status is not None and tip_status != "":
                if a_url.endswith("?"):
                    a_url += "tip_status={}".format(tip_status)
                else:
                    a_url += "&tip_status={}".format(tip_status)
            types_str = get_arg(request, "event_type", None)  # 预警类型列表
            event_type = None
            if types_str is not None and types_str != "":
                if a_url.endswith("?"):
                    a_url += "event_type={}".format(types_str)
                else:
                    a_url += "&event_type={}".format(types_str)
                event_type = [types_str]
            else:
                pass
            active_tip_str = get_arg(request, "active_tip", "[]")  # 主动提醒列表
            active_tip = None
            if types_str is not None and types_str != "":
                if a_url.endswith("?"):
                    a_url += "active_tip={}".format(active_tip_str)
                else:
                    a_url += "&active_tip={}".format(active_tip_str)
                active_tip = json.loads(active_tip_str)
            else:
                pass
            end_date_str = get_arg(request, "end_date", None)
            end_date = get_datetime_from_str(end_date_str)
            if end_date is None:
                end_date = datetime.datetime.now()
            else:
                if a_url.endswith("?"):
                    a_url += "end_date={}".format(end_date_str)
                else:
                    a_url += "&end_date={}".format(end_date_str)
            begin_date_str = get_arg(request, "begin_date", None)
            begin_date = get_datetime_from_str(begin_date_str)
            if begin_date is None or (begin_date - end_date).total_seconds() >= 0:
                begin_date = end_date - datetime.timedelta(days=1365)
            else:
                if a_url.endswith("?"):
                    a_url += "begin_date={}".format(begin_date_str)
                else:
                    a_url += "&begin_date={}".format(begin_date_str)
            num = get_arg(request, "num", None)
            if num is not None and num != "":
                ms = "num={}".format(num)
                try:
                    num = int(num)
                except ValueError as e:
                    logger.exception(ms)
                    print(e)
                except TypeError as e:
                    logger.exception(ms)
                    print(e)
                except Exception as e:
                    logger.exception(ms)
                    print(e)
                finally:
                    num = 8 if not isinstance(num, int) else num

                if a_url.endswith("?"):
                    a_url += "num={}".format(num)
                else:
                    a_url += "&num={}".format(num)
            else:
                num = 8
            cur_index = get_arg(request, "cur_index", 1)
            ms = "cur_index={}".format(cur_index)
            try:
                cur_index = int(cur_index)
            except ValueError as e:
                logger.exception(ms)
                print(e)
            except TypeError as e:
                logger.exception(ms)
                print(e)
            except Exception as e:
                logger.exception(ms)
                print(e)
            finally:
                cur_index = 1 if not isinstance(cur_index, int) else cur_index
            if a_url.endswith("?"):
                a_url += "cur_index={}"
            else:
                a_url += "&cur_index={}"
            event_list = list()
            event_count = 0
            if user_id is not None and user_id not in employees:
                """待查看用户不在权限范围内"""
                pass
            else:
                args = {
                    "user_id": user_id,
                    "tip_status": tip_status,
                    "event_type": event_type,
                    "end_date": end_date,
                    "begin_date": begin_date,
                    "index": cur_index,
                    "num": num
                }
                data = security_module.DrivingEvent.page(**args)
                event_list = data['data']
                event_count = data['count']  # 违章条数

            """处理分页"""
            page_count = math.ceil(event_count / num)  # 共计多少页?
            """确认分页范围"""
            min_index = cur_index - 2
            min_index = 1 if min_index < 1 else min_index
            max_index = cur_index + 2
            max_index = page_count if max_index > page_count else max_index
            index_list = [{"page_num": x, "page_url": a_url.format(x)} for x in list(range(min_index, max_index + 1))]
            prev_page_url = a_url.format((min_index if cur_index - 1 < min_index else cur_index - 1))
            next_page_url = a_url.format((max_index if cur_index + 1 > max_index else cur_index + 1))
            cur_page_url = a_url.format(cur_index)
            """违章状态字典"""
            return render_template("manage/warning_light.html", drivers=employees, pages=index_list,
                                   active_tip=active_tip, page_count=page_count, event_list=event_list,
                                   event_count=event_count, prev_page_url=prev_page_url, next_page_url=next_page_url,
                                   cur_page_url=cur_page_url, head_img_url=head_img_url)

        elif request.method.lower() == "post":
            """各种接口"""
            mes = {"message": "success"}
            the_type = get_arg(request, "the_type")
            if the_type == "change_tip_status":
                """更改提醒状态"""
                event_ids = get_arg(request, "event_id")
                event_ids = json.loads(event_ids)
                event_ids = [ObjectId(x) for x in event_ids]
                filter_dict = {"_id": {"$in": event_ids}}
                update_dict = {"$set": {"tip_status": 1}}
                res = security_module.DrivingEvent.update_many_plus(filter_dict=filter_dict, update_dict=update_dict)
                return json.dumps(mes)
            else:
                return abort(403, "不支持的操作")
        else:
            return abort(405, "不支持的操作")


@manage_blueprint.route("/accident", methods=["get", "post"])
@check_platform_session
def accident_func():
    """事故(历史)页面"""
    head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
    """获取基本下属信息,用于身份验证,防止越权查看信息"""
    company_id = get_platform_session_arg("company_id")
    user_id = get_platform_session_arg("user_id")
    if company_id is None:
        return abort(404, "company_id is none")
    else:
        employees = Company.all_employee(company_id=company_id, can_json=True)
        e_dict = {x['_id']: {
            "real_name": x['real_name'] if x.get("real_name") else
            (x['official_name'] if x.get("official_name") else x['phone_num']),
            "head_img_url": x.get("head_img_url", "/static/image/head_img/default_01.png")
        } for x in employees}
        if request.method.lower() == "get":
            """返回页面事故列表页"""
            """开始取地址栏参数"""
            a_url = "accident?"  # 待拼接url地址,这里是相对地址
            driver_id = get_arg(request, "driver_id", None)  # 司机名
            if driver_id is not None and driver_id != "" and len(driver_id) == 24:
                a_url += "driver_id={}".format(driver_id)
                driver_id = ObjectId(driver_id)
            city = get_arg(request, "city", None)  # 城市
            if city is not None and city != "":
                if a_url.endswith("?"):
                    a_url += "city={}".format(city)
                else:
                    a_url += "&city={}".format(city)

            plate_number = get_arg(request, "plate_number", None)  # 车牌
            if plate_number is not None and plate_number != "":
                if a_url.endswith("?"):
                    a_url += "plate_number={}".format(plate_number)
                else:
                    a_url += "&plate_number={}".format(plate_number)

            status_str = get_arg(request, "status", None)  # 处理状态
            if isinstance(status_str, str) and status_str.isdigit():
                status = int(status_str)
            else:
                status = -1
            if status in [0, 1]:
                ms = "status={}".format(status)
                if a_url.endswith("?"):
                    a_url += "{}".format(ms)
                else:
                    a_url += "&{}".format(ms)
            end_date_str = get_arg(request, "end_date", None)  # 截至时间
            end_date = get_datetime_from_str(end_date_str)
            if end_date is None:
                end_date = datetime.datetime.now()
            else:
                if a_url.endswith("?"):
                    a_url += "end_date={}".format(end_date_str)
                else:
                    a_url += "&end_date={}".format(end_date_str)
            begin_date_str = get_arg(request, "begin_date", None)  # 开始时间
            begin_date = get_datetime_from_str(begin_date_str)
            begin_date = None if begin_date is None or (begin_date - end_date).total_seconds() >= 0 else begin_date
            if begin_date is None:
                pass
            else:
                if a_url.endswith("?"):
                    a_url += "begin_date={}".format(begin_date_str)
                else:
                    a_url += "&begin_date={}".format(begin_date_str)

            num_str = get_arg(request, "num", None)   # 每页多少条记录?
            if isinstance(num_str, str) and num_str.isdigit():
                num = int(num_str)
            else:
                num = 8
            if num_str is None:
                pass
            else:
                ms = "num={}".format(num)
                if a_url.endswith("?"):
                    a_url += "{}".format(ms)
                else:
                    a_url += "&{}".format(ms)

            cur_index_str = get_arg(request, "cur_index", None)  # 当前是第几页?
            if isinstance(cur_index_str, str) and cur_index_str.isdigit():
                cur_index = int(cur_index_str)
            else:
                cur_index = 1
            if cur_index_str is None:
                pass
            else:
                ms = "cur_index={}".format(cur_index)
                if a_url.endswith("?"):
                    a_url += "{}".format(ms)
                else:
                    a_url += "&{}".format(ms)

            args = {
                "driver_id": driver_id,
                "writer": user_id,
                "city": city,
                "plate_number": plate_number,
                "status": status,
                "end_date": end_date,
                "begin_date": begin_date,
                "index": cur_index,
                "num": num
            }
            error = None
            try:
                data = Accident.page(**args)
                acc_list = data['data']
                acc_dict = {x['_id']: x for x in acc_list}
                acc_count = data['count']  # 事故条数
            except Exception as e:
                print(e)
                error = str(e)
            finally:
                if error is None:
                    """处理分页"""
                    page_count = math.ceil(acc_count / num)  # 共计多少页?
                    """确认分页范围"""
                    min_index = cur_index - 2
                    min_index = 1 if min_index < 1 else min_index
                    max_index = cur_index + 2
                    max_index = page_count if max_index > page_count else max_index
                    index_list = [{"page_num": x, "page_url": a_url.format(x)} for x in list(range(min_index, max_index + 1))]
                    prev_page_url = a_url.format((min_index if cur_index - 1 < min_index else cur_index - 1))
                    next_page_url = a_url.format((max_index if cur_index + 1 > max_index else cur_index + 1))
                    cur_page_url = a_url.format(cur_index)
                    return render_template("manage/accident_light.html", drivers=employees, pages=index_list,
                                           page_count=page_count, acc_list=acc_list, acc_count=acc_count,
                                           head_img_url=head_img_url, e_dict=e_dict, acc_dict=acc_dict,
                                           prev_page_url=prev_page_url, next_page_url=next_page_url,
                                           cur_page_url=cur_page_url, status=status)
                else:
                    abort(401, error)
        elif request.method.lower() == "post":
            """各种接口"""
            return abort(403, "不支持的操作")
        else:
            return abort(405, "不支持的方法")


@manage_blueprint.route("/<prefix>_accident", methods=["get", "post"])
@check_platform_session
def process_accident_func(prefix):
    """对事故信息的添加,修改,删除"""
    head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
    """获取基本下属信息,用于身份验证,防止越权查看信息"""
    company_id = get_platform_session_arg("company_id")
    if company_id is None:
        return abort(404, "company_id is none")
    else:
        employees = Company.all_employee(company_id=company_id, can_json=True)
        e_dict = {x['_id']: x['real_name'] if x.get("real_name") else (
            x['official_name'] if x.get("official_name") else x['phone_num']) for x in employees}
        if prefix == "update":
            """编辑事故信息的页面或者接口"""
            if request.method.lower() == "get":
                """返回编辑/新增事故信息的页面"""
                acc_id = get_arg(request, "a_id", None)
                accident = dict()
                if acc_id is None:
                    """新增事故信息"""
                    pass
                else:
                    accident = security_module.Accident.find_by_id(acc_id)
                    if isinstance(accident, security_module.Accident):
                        accident = accident.to_flat_dict()
                    else:
                        pass
                acc_type = ["追尾碰撞", "双车刮蹭", "部件失效", "车辆倾覆"]
                return render_template("manage/update_accident_light.html", acc=accident, acc_type=acc_type,
                                       head_img_url=head_img_url, e_dict=e_dict)
            elif request.method.lower() == "post":
                """提交事故"""
                mes = {"message": "success"}
                user_id = get_platform_session_arg("user_id")
                if isinstance(user_id, str) and len(user_id) == 24:
                    writer = DBRef(database=mongo_db.db_name, collection="user_info", id=ObjectId(user_id))
                    args = get_args(request)
                    """
                    delete 用来确认是否是删除对象. 有就是删除,无就是insert和update
                    insert和update用_id的有无来判断.无是insert,有就是update
                    """
                    delete = args.pop("delete", "0")
                    _id = args.get('_id')
                    if delete == "1" and isinstance(_id, str) and len(_id) == 24:
                        """删除事故"""
                        f = {"writer": writer, "_id": ObjectId(_id)}
                        r = Accident.find_one_and_delete(filter_dict=f)
                        if r:
                            pass
                        else:
                            mes['message'] = "删除失败"
                    else:
                        """insert和update"""
                        a_status = args.get('status', 0)
                        try:
                            a_status = int(a_status)
                        except Exception as e:
                            print(e)
                            a_status = 0
                        finally:
                            args['status'] = a_status
                        args['writer'] = writer
                        driver_id = None
                        try:
                            driver_id = ObjectId(args['driver_id'])
                        except Exception as e:
                            print(e)
                            mes['message'] = str(e)
                        finally:
                            if isinstance(driver_id, ObjectId):
                                args['driver_id'] = driver_id
                                args['last_update'] = datetime.datetime.now()
                                accident = Accident(**args)
                                _id = None
                                error = None
                                try:
                                    _id = accident.save_plus()
                                except Exception as e:
                                    logger.exception(e)
                                    error = e
                                    print(e)
                                finally:
                                    if isinstance(_id, ObjectId):
                                        pass
                                    else:
                                        mes['message'] = "插入失败,错误原因:{}".format(str(error))
                            else:
                                pass
                else:
                    mes['message'] = "身份验证失败"
                return json.dumps(mes)
            else:
                return abort(404)
        else:
            return abort(404, "页面不存在")


@manage_blueprint.route("/test_page/<uid>")
@check_platform_session
def test_page_func(uid):
    """
    用于测试web功能的页面.
    :param uid: token,用于简单的身份验证
    :return:
    """
    today_uid = "1025de51f1654c0bbc91fae8d88f7939"
    if uid != today_uid:
        return abort(404)
    else:
        return render_template("test_page.html")


@manage_blueprint.route("/upload_file", methods=['post'])
@check_platform_session
def upload_accident_file_func():
    """
    接收页面上传的事故相关文件,以GridFS的形式保存在数据库中.最常见的情况是为富文本编辑器服务
    :return:
    """
    mes = {"message": "success"}
    files = {k: v for k, v in request.files.items()}
    user_id = get_platform_session_arg("user_id", None)
    if len(files) == 0:
        mes['message'] = "没有发现上传的文件"
    elif not (isinstance(user_id, str) and len(user_id) == 24):
        mes['message'] = "身份验证失败"
    else:
        owner = DBRef(database=mongo_db.db_name, collection="user_info", id=ObjectId(user_id))
        """存在一次上传多个文件的可能性,但现在不予考虑"""
        for collection, file in files.items():
            data = dict()
            args = dict()
            file_name = file.filename
            args['file_name'] = file_name
            args['file_type'] = file.content_type
            args['owner'] = owner
            _id = mongo_db.BaseFile.save_cls(file_obj=file, collection=collection, **args)
            # _id = AccidentData.save_cls(file_obj=file, **args)
            if isinstance(_id, ObjectId):
                _id = str(_id)
                data['_id'] = _id
                data['url'] = mongo_db.BaseFile.format_url(file_id=_id, file_name=file_name, collection=collection)
                mes['data'] = data
            else:
                mes['message'] = "保存文件失败"
    return json.dumps(mes)


@manage_blueprint.route("/fs/<collection>/<o_id>/<file_name>", methods=['get'])
@check_platform_session
def rebuild_file_func(collection, o_id, file_name):
    """
    显示GridFS里的文件.
    :param collection: 表名
    :param o_id:
    :param file_name:
    :return:
    """
    user_id = get_platform_session_arg("user_id", None)
    owner = DBRef(database=mongo_db.db_name, collection="user_info", id=ObjectId(user_id))
    f = {"_id": ObjectId(o_id), "file_name": file_name, "owner": owner}
    file = mongo_db.BaseFile.find_one_cls(filter_dict=f, collection=collection, instance=False)
    """分析查询结果"""
    if file is None:
        return abort(404)
    else:
        file_name = file['file_name']
        file_type = file['file_type']
        file_data = file['data']
        resp = make_response(send_file(BytesIO(file_data), attachment_filename=file_name, as_attachment=True,
                                       mimetype=file_type))
        """把文件名的中文从utf-8转成latin-1,这是防止中文的文件名造成的混乱"""
        resp.headers["Content-Disposition"] = "attachment; filename={}".format(file_name.encode().decode('latin-1'))
        return resp


@manage_blueprint.route("/<prefix>_structure", methods=["get", "post"])
@check_platform_session
def process__structure_func():
    """组织架构管理页面,暂停"""
    current_user_id = get_platform_session_arg("user_id")
    head_img_url = get_platform_session_arg("head_img_url", "static/image/head_img/default_02.png")
    current_real_name = get_platform_session_arg("real_name")


@manage_blueprint.route("/batch_insert_user", methods=['get', 'post'])
def batch_insert_user():
    """批量插入用户,需要3个参数:x_token, company_id和员工列表"""
    token = get_arg(request, 'x_token', None)  # 确认身份的
    if token == "bae96f78b38b4e21ab94dab75582918f":
        if request.method.lower() == "get":
            """示范"""
            html = """
            python3 demo code<br>
            ==========================================<br>
            import requests<br>
            import json <br>
            company_id = "5aab48ed4660d32b752a7ee9"  # 新振兴的id,<br>
            e1 = {<br>
            &nbsp;&nbsp;&nbsp;&nbsp;"phone_num": "15618318888", <br>
            &nbsp;&nbsp;&nbsp;&nbsp;"real_name": "张三",                  <br>
            &nbsp;&nbsp;&nbsp;&nbsp;"dept_id": "5ab21b2a4660d3745e53adfa",  # 新振兴的默认部门id<br>
            &nbsp;&nbsp;&nbsp;&nbsp;"post_id": "5ab21fc74660d376c982ee27"   # 新振兴的默认职务id<br>
            }<br>
            user_list = [e1,....]<br>
            x_token = "bae96f78b38b4e21ab94dab75582918f"<br>
            data = {"x_token": x_token, "company_id": company_id, "user_list": json.dumps(user_list)}<br>
            url = "http://xzx.safego.org/manage/batch_insert_user"<br>
            r = requests.post(url, data=data)<br>
            if r.status_code == 200:<br>
            &nbsp;&nbsp;&nbsp;&nbsp;print(r.json())<br>
            else:<br>
            &nbsp;&nbsp;&nbsp;&nbsp;print(r.status_code)<br>
            """
            return html
        elif request.method.lower() == "post":
            error = ''
            user_list = None
            try:
                user_list = json.loads(get_arg(request, "user_list", ''))
            except TypeError as e:
                print(e)
                error = str(e)
                logger.exception()
            except json.decoder.JSONDecodeError as e:
                print(e)
                error = str(e)
                logger.exception()
            except Exception as e:
                print(e)
                error = str(e)
                logger.exception()
            finally:
                pass
            company_id = get_arg(request, "company", '').strip()
            ms = "batch_insert_user, company_id:{}. args:{}".format(company_id, user_list)
            logger.info(ms)
            mes = {"message": "success"}
            if error != '':
                pass
            elif len(company_id) != 24:
                error = "错误的公司id:{}".format(company_id)
            elif isinstance(user_list, list):
                error = "导入的数据必须是字典的数组"
            elif len(user_list) == 0:
                error = "导入的数据为空"
            else:
                try:
                    Company.add_employee(company_id, user_list)
                except Exception as e:
                    error = "{}".format(e)
                finally:
                    if len(error) > 0:
                        mes['message'] = error
                    else:
                        pass
            mes['message'] = error
            return json.dumps(mes)
        else:
            return abort(405)

    else:
        return abort(404)
