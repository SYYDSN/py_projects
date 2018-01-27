# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, Blueprint, abort, make_response
from flask_wtf.form import FlaskForm
import os
from api.data.item_module import GPS
from tools_module import *
import amap_module
import random
from manage.company_module import *
from api.data.item_module import User
from api.data.item_module import Track
from log_module import get_logger
from api.user import security_module
from werkzeug.contrib.cache import RedisCache


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
        return render_template("manage/app_version_table.html",)
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


@manage_blueprint.route("/block_employee_list", methods=['get', 'post'])
@check_platform_session
def block_employee_list_func():
    """用户管理屏蔽列表的页面"""
    sid = get_arg(request, "sid")
    user_dict = get_platform_cors_session_dict(sid)  # 跨域用户
    if user_dict:
        user_id = user_dict['user_id']
    else:
        user_id = get_platform_session_arg("user_id")
    user = Employee.find_by_id(user_id)
    block_list = Employee.get_block_id_list(user_id, to_str=True)
    if request.method.lower() == "get" and isinstance(user, Employee):
        company_dbref = user.get_attr("company_id")
        if company_dbref is None:
            post_dict, dept_dict = {}, {}
        else:
            company_id = company_dbref.id
            post_dict = Company.all_post(company_id)
            dept_dict = Company.all_dept(company_id)
        employee_list = Employee.subordinates_instance(user_id, True, True)
        current_user_name = user.get_attr("phone_num") if user.get_attr("real_name", "") == '' \
            else user.get_attr("real_name", "")
        return render_template("manage/block_employee_list.html", block_list=block_list, employee_list=employee_list,
                               post_dict=post_dict, dept_dict=dept_dict, current_user_name=current_user_name)
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
                company_id = company_dbref.id
                post_dict = Company.all_post(company_id)
                dept_dict = Company.all_dept(company_id)
            employee_list = Employee.subordinates_instance(user_id)
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
                cache.delete(key=key)   # 清除最后的位置信息的缓存
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
    登录页
    跨域登录/注册的用户必须带上 cros=True的参数.
    登录成功后.
    跨域用户每次请求的时候需要带上sid参数(会话id)
    此参数会在跨域用户登录成功时返回给客户.
    登录成功的跨域用户,每隔十秒需要做一次心条请求.以确认会话在线.(心跳请求的接口函数在tornado服务器上)
    """
    if request.method.lower() == "get":
        login_title = '登录'
        return render_template("manage/login.html", login_title=login_title)
    elif request.method.lower() == "post":
        """验证用户身份"""
        message = {"message": "success"}
        user_name = get_arg(request, "user_name")
        user_password = get_arg(request, "user_password")
        cors = get_arg(request, "cors", None)
        args = {"user_name": user_name, "user_password": user_password}
        result = User.find_one(**args)
        if result is None:
            message['message'] = "用户名或密码错误"
        else:
            """登录成功,写入会话"""
            args['user_id'] = str(result.get_id())  # 写入用户id的str格式.
            """写入用户所在公司的查询前缀"""
            company_obj = result.get_attr("company_id")
            if company_obj is None:
                pass
            else:
                company_id = company_obj.id
                prefix = Company.find_by_id(company_id).get_attr("prefix")
                if prefix is None:
                    pass
                else:
                    args['prefix'] = prefix
            if cors == "cors":
                """如果是跨域用户"""
                save_res = save_platform_cors_session(**args)
            else:

                save_res = save_platform_session(**args)
            if not save_res:
                """写入会话失败"""
                try:
                    raise ValueError("会话保存失败，args={}".format(str(args)))
                except ValueError as e:
                    print(e)
                    message['message'] = "会话保存失败"
                    logger.exception("error:")
            elif isinstance(save_res, str):
                """这是跨域用户返回的会话id"""
                message['sid'] = save_res
            else:
                pass
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


@manage_blueprint.route("/show_track", methods=['get'])
@check_platform_session
def show_track_func():
    """展示用户轨迹页面"""
    if request.method.lower() == "get":
        return render_template("manage/show_track_light.html")


@manage_blueprint.route("/subordinates_base_info", methods=['post'])
@check_platform_session
def subordinates_base_info_func():
    """获取下属的基本身份信息.包含自己"""
    res = {"message": "success"}
    user_id = get_platform_session_arg("user_id")
    base_info_list = Employee.subordinates_instance(user_id)
    if base_info_list is None:
        res['message'] = "user_id错误"
    else:
        if len(base_info_list) == 0:
            me = Employee.find_by_id(user_id).to_flat_dict()
            res['data'] = [me]
        res['data'] = base_info_list
    return json.dumps(res)


@manage_blueprint.route("/last_positions", methods=['post'])
def last_positions_func()->dict:
    """
    根据用户id，获取他所能查看的员工的最后的位置信息，
    """
    res = {"message": "success"}
    user_id = get_platform_session_arg("user_id")
    user_id = user_id  # user_id = "debug" 是调试用，查看所有的人的位置
    subordinate_id_list = Employee.subordinates_id(user_id)  # 获取下属/能查看的用户列表。
    if subordinate_id_list is None:
        """user_id错误"""
        mes = "user_id错误"
        res['message'] = mes
    else:
        if len(subordinate_id_list) == 0:
            """没有下属，只能查看自己的位置了"""
            subordinate_id_list = [mongo_db.get_obj_id(user_id)]
        key = "all_last_position_{}".format(user_id)
        user_position_dict = cache.get(key)
        if user_position_dict is None:
            user_position_dict = Track.get_last_position(subordinate_id_list)  # 获取最后的点信息
            cache.set(key, user_position_dict, timeout=60)
        else:
            pass
        user_position_list = list(user_position_dict.values())
        res['data'] = user_position_list
    return json.dumps(res)


@manage_blueprint.route("/track_info", methods=['post', 'get'])
def track_info():
    """获取运动轨迹信息"""
    message = {"message": "success"}
    phone_num = get_arg(request, "phone_num", "15618317376")
    if not check_phone(phone_num) and not check_iot_phone(phone_num):
        message['message'] = "{} 不是正确的手机号码".format(phone_num)
    else:
        user = User.find_one(phone_num=phone_num)
        if user is None:
            message['message'] = "号码 {} 尚未注册！".format(phone_num)
        else:
            user_id = User.find_one(phone_num=phone_num).get_id()
            begin_date = get_arg(request, "begin_date", None)  # 开始时间
            end_date = get_arg(request, "end_date", datetime.datetime.now())  # 结束时间
            end_date = get_datetime_from_str(end_date)
            begin_date = get_datetime_from_str(begin_date)
            if end_date is None or begin_date is None or (end_date - begin_date).total_seconds() > 0:
                data = Track.get_tracks_list(user_id, begin_date, end_date)
                message['data'] = data
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
        # user_header_img = "../static/image/head_img/default_02.png"  # 用户头像
        return render_template("manage/index_light.html")
    else:
        return abort(405)


@manage_blueprint.route("/driver_list", methods=["get"])
@check_platform_session
def driver_list_func():
    if request.method.lower() == "get":
        """员工/司机列表页"""
        page_title = "员工列表"
        return render_template("manage/driver_list_light.html", page_title=page_title)
    else:
        return abort(405)


# @manage_blueprint.route("/employee_list", methods=["get"])
# @check_platform_session
# def employee_list_func():
#     if request.method.lower() == "get":
#         """员工/司机列表页,旧，要被废止"""
#         page_title = "员工列表"
#         return render_template("manage/employee_list.html", page_title=page_title)
#     else:
#         return abort(405)


@manage_blueprint.route("/driver_detail", methods=["get", "post"])
@check_platform_session
def driver_detail_func():
    if request.method.lower() == "get":
        """员工/司机详情"""
        return render_template("manage/driver_detail_light.html")
    elif request.method.lower() == "post":
        """根据用户id查询详细档案"""
        current_id = get_platform_session_arg("user_id")  # 已登录用户的id
        if current_id is None:
            current_id = get_platform_cors_session_dict(get_arg(request, "sid"))
        message = {"message": "success"}
        user_id = get_arg(request, "user_id", None)  # 待查询的用户的id
        date_str = get_arg(request, "date", None)  # 查询的日期 2013-12-12
        prefix = get_platform_session_arg("prefix", None)  # 当前用户所在公司前缀
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


@manage_blueprint.route("/get_driver_list", methods=['post', 'get'])
@check_platform_session
def get_driver_list_func() -> str:
    """
    根据用户session中的身份信息,查询用户的下属信息的列表,如果没有下属信息,那就返回自己的个人信息.
    注意,这里返回的都是简要信息,用于创建列表和侧边栏,详细信息用get_employee_archives接口获取.
    :return: 消息字典的json,其中包含下属身份信息的的列表
    """
    sid = get_arg(request, "sid", None)
    user_dict = get_platform_cors_session_dict(sid)
    if user_dict:
        user_id = user_dict['user_id']
    else:
        user_id = get_platform_session_arg("user_id")
    raw_user_id = user_id
    message = {"message": "success"}
    if user_id is None:
        message['message'] = "没有检测到用户id存在"
    else:
        #此方式虽然合理,但速度太慢,改为从缓存获取
        # try:
        #     user_id = mongo_db.get_obj_id(user_id)
        # except Exception:
        #     user_id = None
        # finally:
        #     if user_id is None:
        #         message['message'] = "错误的user_id:{}".format(raw_user_id)
        #     else:
        #         team = Employee.subordinates_id(user_id)
        #         if len(team) == 0:
        #             team = [user_id]
        #         else:
        #             pass
        #         # 获取用户的档案.
        #         team_info = Employee.get_archives_cls(team)
        """从缓存获取信息"""
        team_info = get_archives_from_cache(user_id)
        team_info = [{"_id": x['_id'], "real_name": x['real_name'] if x.get('real_name') else x.get('phone_num'),
                      "head_img_url": x['head_img_url']} for x in team_info.values()]
        message['data'] = team_info
    return json.dumps(message)


@manage_blueprint.route("/get_employee_archives", methods=['post', 'get'])
@check_platform_session
def get_employee_archives_func():
    """
    get_employee_list_func 函数的增强版
    根据用户session中的身份信息,查询用户的下属信息的详细档案(包含安全等级和安全报告),如果没有下属信息,那就返回自己的详细档案.
    注意,这里返回的都是详细信息,用于用户管理模块和显示用户详细资料.
    :return: 消息字典的json,其中包含下属档案信息的的列表
    """
    sid = get_arg(request, "sid", None)
    user_dict = get_platform_cors_session_dict(sid)
    if user_dict:
        user_id = user_dict['user_id']
    else:
        user_id = get_platform_session_arg("user_id")
    # user_id = ObjectId("59895177de713e304a67d30c")
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
    if request.method.lower() == "get":
        """报表"""
        page_title = "报表"
        return render_template("manage/report_page.html", page_title=page_title)
    elif request.method.lower() == "post":
        """从缓存取虚拟数据"""
        sid = get_arg(request, "sid", None)
        user_dict = get_platform_cors_session_dict(sid)
        if user_dict:
            user_id = user_dict['user_id']
        else:
            user_id = get_platform_session_arg("user_id")
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
            "member_count": member_count,     # 成员统计
            "total_time": total_time,         # 时长统计
            "total_mileage": total_mileage,   # 里程统计
            "speed_avg": speed_avg,           # 平均速度
            "cnt_rapi_acce": cnt_rapi_acce,   # 急加速统计
            "cnt_shar_turn": cnt_shar_turn,   # 急转统计
            "cnt_sudd_brak": cnt_sudd_brak,   # 急刹统计
            "scr_synt": scr_synt              # 平均综合/安全指数
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
