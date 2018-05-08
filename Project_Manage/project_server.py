# -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import make_response
from flask import render_template
from flask_debugtoolbar import DebugToolbarExtension
from flask import render_template_string
from flask import send_file
from flask import request
from werkzeug.contrib.cache import RedisCache
from flask_session import Session
from log_module import get_logger
import json
from json import JSONDecodeError
from module.user_module import *
from module.project_module import *
from mongo_db import get_datetime_from_str
from tools_module import *
import calendar
import os
from mongo_db import db_name


secret_key = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
# app.config['SERVER_NAME'] = "127.0.0.1:8001"  此域名下的所有子域名的session都会接受
Session(app)


cache = RedisCache()
logger = get_logger()
port = 8001


def get_token() -> (None, str):
    """
    从请求头获取token的方法。
    :return:
    """
    token = request.headers.get("token")
    return token


def verify_token(f):
    """
    检测跨域用户的token，是否拥有此功能的权限？,和本域的不同，跨域的只能对post请求数据的行为进行限制。
    限制的方法如下：
    首先，post请求的url包含如下的方式：
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """验证token"""

        """本域用户"""
        user_name = session.get("user_name")  # 检测session中的user_name
        user_password = session.get("user_password")  # user_password
        if not (user_name and user_password):
            return redirect(url_for("teacher_login_func"))
        else:
            checked_user_obj = user_module.User.login(user_name=user_name, user_password=user_password)
            if not checked_user_obj:
                """用户名和密码不正确"""
                return redirect(url_for("teacher_login_func"))
            else:
                return f(*args, **kwargs)
    return decorated_function


@app.route("/index", methods=['get'])
@check_platform_session
def index_func():
    """首页"""
    return "hello world"


@app.route("/check_token", methods=['post', 'get'])
def check_session_func():
    """检查token，这是一个测试函数，token"""
    token = get_token()
    return token


@app.route("/login", methods=['post', 'get'])
def login_func():
    """登录页"""
    if request.method.lower() == "get":
        login_title = "Login"
        return render_template("login_new.html", login_title=login_title)
    elif request.method.lower() == "post":
        user_name = get_arg(request, "user_name")
        user_password = get_arg(request, "user_password")
        """管理员用户 proot/P@root1234"""
        mes = User.login(user_name, user_password)
        if mes['message'] == "success":
            save_dict = mes['data']
            save_dict['user_name'] = user_name
            save_dict['user_password'] = user_password
            save_dict['allow_view'] = mes['data']['allow_view']
            save_dict['allow_edit'] = mes['data']['allow_edit']
            save_platform_session(**save_dict)

        else:
            clear_platform_session()
        resp = make_response(json.dumps(mes))
        # resp.headers.set("Access-Control-Allow-Origin", "*")
        return resp
    else:
        return abort(405)


@app.route("/manage_<key1>/<key2>", methods=['post', 'get'])
@check_platform_session
def manage_user_func(key1, key2):
    """
    管理页面,只有proot用户能访问
    key1 是页面的类别,key2是不同的操作,其中get请求不需要key2
    """
    group = get_platform_session_arg("group")
    if group == "admin":
        if request.method.lower() == "get":
            """获取全部category"""
            categories = Category.get_all(ignore=["invalid"], can_json=True)
            categories.sort(key=lambda obj: obj['name'])
            if key1 == "user":
                """用户管理界面"""
                category_names = [x['name'] for x in categories]
                column_length = 4 + len(category_names)
                users = User.get_all(can_json=True)
                new_users = list()
                for user in users:
                    allow_view = user['allow_view']
                    allow_edit = user['allow_edit']
                    category_list = list()
                    temp = dict()
                    temp['_id'] = user['_id']
                    temp['nick_name'] = "" if user.get('nick_name') is None else user.get('nick_name')
                    temp['user_name'] = user['user_name']
                    temp['status'] = user['status']
                    temp['create_date'] = user['create_date']
                    for category in categories:
                        category_id = category['_id']
                        if category_id in allow_view:
                            status1 = 1
                        else:
                            status1 = 0
                        if category_id in allow_edit:
                            status2 = 1
                        else:
                            status2 = 0
                        category_list.append({"_id": category_id, "name": category['name'], "status": (status1, status2)})
                    temp['category_list'] = category_list
                    new_users.append(temp)

                return render_template("manage_user.html", category_names=category_names, key=key1,
                                       column_length=column_length, categories=categories, users=new_users)
            elif key1 == "category":
                """类别管理"""
                return render_template("manage_category.html", key=key1, categories=categories)
            else:
                return abort(404)
        elif request.method.lower() == "post":
            if key1 == "user":
                """用户管理"""
                mes = {"message": "success"}
                if key2 == "add":
                    """添加用户"""
                    user_name = get_arg(request, "user_name", None)
                    nick_name = get_arg(request, "nick_name", None)
                    user_password = get_arg(request, "user_password", None)
                    allow_view = list()
                    allow_edit = list()
                    try:
                        allow_view = json.loads(get_arg(request, "allow_view"))
                    except JSONDecodeError as e:
                        ms = "添加用户失败，arg：{}， 错误原因：{}".format(get_args(request), e)
                        print(ms)
                        logger.exception(ms)
                    try:
                        allow_edit = json.loads(get_arg(request, "allow_edit"))
                    except JSONDecodeError as e:
                        ms = "添加用户失败，arg：{}， 错误原因：{}".format(get_args(request), e)
                        print(ms)
                        logger.exception(ms)
                    args = {
                        "nick_name": nick_name,
                        "user_name": user_name,
                        "user_password": user_password,
                        "allow_view": [ObjectId(x) for x in allow_view],
                        "allow_edit": [ObjectId(x) for x in allow_edit]
                    }
                    args = {k: v for k, v in args.items() if v is not None}
                    r = None
                    try:
                        r = User.add_user(**args)
                    except Exception as e:
                        mes['message'] = str(e)
                    finally:
                        if r is None and mes['message'] == "success":
                            mes['message'] = "添加失败"
                        else:
                            pass
                elif key2 == "edit":
                    """编辑"""
                    user_id = get_arg(request, "user_id")
                    update_dict = None
                    try:
                        update_dict = json.loads(get_arg(request, "update_dict"))
                    except JSONDecodeError as e:
                        print(e)
                    finally:
                        if update_dict is None:
                            mes['message'] = 'update字典不能为空'
                        else:
                            r = None
                            try:
                                r = User.update_user(user_id=user_id, update_dict=update_dict)
                            except Exception as e:
                                mes['message'] = str(e)
                            finally:
                                if r is None and mes['message'] == "success":
                                    mes['message'] = "编辑失败"
                                else:
                                    pass
                elif key2 == "delete":
                    """删除类别"""
                    o_id = get_arg(request, "o_id")
                    r = None
                    try:
                        r = Category.delete_instance(o_id=o_id)
                    except Exception as e:
                        mes['message'] = str(e)
                    finally:
                        if r is None and mes['message'] == "success":
                            mes['message'] = "删除失败"
                        else:
                            pass
                else:
                    return abort(401)  # 未授权
                return json.dumps(mes)
            elif key1 == "category":
                """类别管理"""
                mes = {"message": "success"}
                if key2 == "add":
                    """添加"""
                    args = get_args(request)
                    r = None
                    try:
                        r = Category.add_instance(**args)
                    except Exception as e:
                        mes['message'] = str(e)
                    finally:
                        if r is None and mes['message'] == "success":
                            mes['message'] = "添加失败"
                        else:
                            pass
                elif key2 == "edit":
                    """编辑"""
                    o_id = get_arg(request, "o_id")
                    update_dict = None
                    try:
                        update_dict = json.loads(get_arg(request, "update_dict"))
                    except JSONDecodeError as e:
                        print(e)
                    finally:
                        if update_dict is None:
                            mes['message'] = 'update字典不能为空'
                        else:
                            r = None
                            try:
                                r = Category.update_instance(o_id=o_id, update_dict=update_dict)
                            except Exception as e:
                                mes['message'] = str(e)
                            finally:
                                if r is None and mes['message'] == "success":
                                    mes['message'] = "编辑失败"
                                else:
                                    pass
                elif key2 == "delete":
                    """删除类别"""
                    o_id = get_arg(request, "o_id")
                    r = None
                    try:
                        r = Category.delete_instance(o_id=o_id)
                    except Exception as e:
                        mes['message'] = str(e)
                    finally:
                        if r is None and mes['message'] == "success":
                            mes['message'] = "删除失败"
                        else:
                            pass
                else:
                    return abort(401)  # 未授权
                return json.dumps(mes)
            else:
                return abort(403)  # 禁止访问
        else:
            return abort(405)
    else:
        return redirect(url_for("login_func"))


@app.route("/home_<key1>/<key2>", methods=['post', 'get'])
@check_platform_session
def home_func(key1, key2):
    """
    主页，是除管理员外，其他用户可以访问的页面
    :param key1:
    :param key2:
    :return:
    """
    user_name = get_platform_session_arg("user_name")
    now = datetime.datetime.now()
    categories = Category.get_all(can_json=True)
    category_dict = {x['_id']: x for x in categories}
    group = get_platform_session_arg("group")
    allow_view_ids = get_platform_session_arg("allow_view")
    if allow_view_ids is None:
        clear_platform_session()
        return redirect(url_for("login_func"))
    allow_view = [category_dict[x]['path'] for x in allow_view_ids]
    allow_edit_ids = get_platform_session_arg("allow_edit")
    if allow_edit_ids is None:
        clear_platform_session()
        return redirect(url_for("login_func"))
    allow_edit = [category_dict[x]['path'] for x in allow_edit_ids]
    all_projects = Project.get_all(can_json=True)
    allow_edit_projects = dict()  # 允许编辑的项目的字典,key是category的id
    allow_edit_pid_name = list()     # 允许编辑的项目的id和name组成的字典的数组
    allow_edit_pids = list()     # 允许编辑的项目的id组成的数组
    for x in allow_edit_ids:
        p_list = list()
        for y in all_projects:
            category_id = y['category_id']
            if category_id == x:
                p_id = y['_id']
                allow_edit_pids.append(p_id)
                allow_edit_pid_name.append({"_id": p_id, "name": y['name']})
                p_list.append(y)
        allow_edit_projects[x] = p_list
    modules = Module.get_all(can_json=True)
    allow_edit_modules = dict()  # 允许编辑的模块的字典,key是project的id
    module_map = dict()  # 模块的id和name的字典
    allow_edit_mids = list()  # 允许编辑的模块的id组成的数组
    for m in modules:
        m_id = m['_id']
        allow_edit_mids.append(m_id)
        module_map[m_id] = m['name']
        p_id = m['project_id']
        begin_date = get_datetime_from_str(m['begin_date'])
        end_date = get_datetime_from_str(m['end_date']) if m.get("end_date") is not None else now
        date_range = Module.calculate_date_range(begin_date, end_date)  # 计算工期
        m['date_range'] = date_range
        m['begin_date'] = begin_date.strftime("%F")
        m['end_date'] = end_date.strftime("%F")
        m_list = allow_edit_modules.get(p_id)
        if m_list is None:
            m_list = list()
        m_list.append(m)
        allow_edit_modules[p_id] = m_list
    year = int(get_arg(request, "y")) if get_arg(request, "y", "").isdecimal() else now.year
    month = int(get_arg(request, "m")) if get_arg(request, "m", "").isdecimal() else now.month
    current_month_str = "{}年{}月".format(year, month)
    first_day, last_day = 1, calendar.monthrange(year, month)[-1]
    days = list()
    week_dict = {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"}
    weeks = list()
    for i in range(first_day, last_day + 1):
        days.append(i)
        day = datetime.date(year=year, month=month, day=i)
        weeks.append(week_dict[day.weekday()])
    """取项目和category的对应关系"""
    project_map = {x['_id']: x['name'] for x in all_projects}
    project_category_map = {x["_id"]: {"name": category_dict[x['category_id']]['name'], "_id": x['category_id']}
                            for x in all_projects if x['category_id'] in category_dict}
    if group != "worker":
        """管理员不能访问此页面"""
        return redirect(url_for("login_func"))
    else:
        cur_method = request.method.lower()
        if cur_method == "get":
            if key1 == "all":
                first_day_in_month = get_datetime_from_str("{}-{}-{} 0:0:0".format(year, month, first_day))
                last_day_in_month = get_datetime_from_str("{}-{}-{} 23:59:59".format(year, month, last_day))
                """登录后的主页，所有用户都能查看所有任务"""
                f = {
                    "status": {"$nin": ['invalid']},
                    "begin_date": {"$lte": last_day_in_month},
                    "end_date": {"$gte": first_day_in_month}
                }
                s = {"project_id": -1, "module_id": -1, "status": -1, "type": -1, "begin_date": -1}
                tasks = Task.find_plus(filter_dict=f, sort_dict=s, to_dict=True, can_json=False)
                """将查询到的本月数据进行整理，以方便页面显示"""
                min_line_count = 20 if len(tasks) < 20 else len(tasks)  # 最小行数
                rows = list()  # 干特图的行组成的数组
                """任务状态字典,注意normal需要判断是否已开始任务？"""
                status_dict = {"normal": "正常",
                               "complete": "完成",
                               "fail":  "失败",
                               "drop":  "放弃",
                               "suspend": "暂停",
                               "delay": "超期"}
                for line in range(min_line_count + 1):
                    task = None
                    try:
                        task = tasks[line]
                        """计算任务工期"""
                        begin_date = get_datetime_from_str(m['begin_date'])
                        end_date = get_datetime_from_str(m['end_date']) if task.get("end_date") is not None else now
                        date_range = Task.calculate_date_range(begin_date, end_date)
                        task['date_range'] = date_range
                        task['begin_date_str'] = begin_date.strftime("%F")  # 注意，只有task的字段名不同
                        task['end_date_str'] = end_date.strftime("%F")  # 注意，只有task的字段名不同
                    except IndexError as e:
                        print(e)
                    finally:
                        pass
                    row = list()
                    if task is None:
                        row = [""] * last_day
                    else:
                        """截取任务处于本月时间区间内的你部分，计算这一部分的开始和结束的day"""
                        begin_data_task = task['begin_date']
                        begin_data_task = first_day_in_month if begin_data_task < first_day_in_month else begin_data_task
                        end_data_task = task['end_date']
                        end_data_task = last_day_in_month if end_data_task > last_day_in_month else end_data_task
                        begin_day = begin_data_task.day
                        end_day = end_data_task.day
                        for day in range(first_day, last_day + 1):
                            if begin_day <= day <= end_day:
                                if day == end_day:
                                    status = status_dict[task['status']]
                                    project_id = str(task['project_id'].id)
                                    project_name = project_map[project_id]
                                    category_name = project_category_map[project_id]['name']
                                    the_begin_date = task['begin_date']
                                    if status == "正常":
                                        if the_begin_date <= now:
                                            status = "推进中"
                                        else:
                                            status = "未开始"
                                    temp = {
                                        "_id": str(task['_id']),
                                        "category_name": category_name,
                                        "project_name": project_name,
                                        "begin_date": the_begin_date.strftime("%F"),
                                        "end_date": task['end_date'].strftime("%F"),
                                        "type": task['type'],
                                        "status": status,
                                        "name": task['name'],
                                        "colspan": (end_day - begin_day) + 1
                                    }
                                    row.append(temp)
                                else:
                                    pass
                            else:
                                row.append("")
                    rows.append(row)
                """左侧导航部分的项目列表,计算项目工期"""
                for p in all_projects:
                    begin_date = get_datetime_from_str(p['begin_date'])
                    end_date = get_datetime_from_str(p['end_date']) if p.get("end_date") is not None else now
                    date_range = Project.calculate_date_range(begin_date, end_date)
                    p['date_range'] = date_range
                    p['begin_date'] = begin_date.strftime("%F")
                    p['end_date'] = end_date.strftime("%F")
                """左侧导航部分的模块列表,模块工期在前面求allow_edit_modules时已计算"""
                """左侧导航部分的功能列表,计算功能工期"""
                missions = Mission.get_all(can_json=True)
                module_mission_dict = dict()  # 模块和功能的对应字典
                for m in missions:
                    m_id = m['module_id']
                    m_list = module_mission_dict.get(m_id)
                    if m_list is None:
                        m_list = list()
                    m_list.append(m)
                    module_mission_dict[m_id] = m_list
                    begin_date = get_datetime_from_str(m['begin_date'])
                    end_date = get_datetime_from_str(m['end_date']) if m.get("end_date") is not None else now
                    date_range = Project.calculate_date_range(begin_date, end_date)
                    m['date_range'] = date_range
                    m['begin_date'] = begin_date.strftime("%F")
                    m['end_date'] = end_date.strftime("%F")
                """获取全部类别的树状图数据"""
                m_mi_dict = get_dict(missions, key="module_id", value_keys=["_id", "name", "status"])
                p_m_dict = get_dict(modules, key="project_id", value_keys=["_id", "name", "status"])
                for k, v in p_m_dict.items():
                    for x in v:
                        item = list() if m_mi_dict.get(x['_id']) is None else m_mi_dict[x['_id']]
                        x['children'] = item
                c_p_dict = get_dict(all_projects, key='category_id', value_keys=["_id", "name", "status"])
                for k, v in c_p_dict.items():
                    for x in v:
                        item = list() if p_m_dict.get(x['_id']) is None else p_m_dict[x['_id']]
                        x['children'] = item
                c_list = [{"_id": x['_id'], "name": x['name'], "children": list() if c_p_dict.get(x['_id']) is None
                else c_p_dict[x['_id']]} for x in categories]
                tree_dict = {"name": "苏秦网络", "children": c_list}
                return render_template("home_template.html", trs=rows, allow_edit=allow_edit, categories=categories,
                                       allow_view=allow_view, cur_method=cur_method, days=days, weeks=weeks,
                                       current_month=current_month_str, allow_edit_projects=allow_edit_projects,
                                       allow_edit_modules=allow_edit_modules, nav_projects=all_projects,
                                       nav_modules=modules, nav_missions=missions, tasks=tasks, tree_dict=tree_dict,
                                       module_mission_dict=module_mission_dict, allow_edit_pids=allow_edit_pids,
                                       allow_edit_mids=allow_edit_mids, user_name=user_name)
            elif key1 in ['web', 'app', 'platform']:
                part = get_arg(request, "part", "chart")  # url参数，用于确认处于哪一个子导航下？
                return redirect("/home_all/view")
                # return render_template("category_chart.html", key1=key1, key2=key2, part=part)
            else:
                return abort(404)
        elif cur_method == "post":
            mes = {"message": "success"}
            if key1 == "project":
                """项目"""
                if key2 == "add":
                    """添加"""
                    args = get_args(request)
                    category_id = args.get("category_id")
                    if category_id is None or len(category_id) != 24:
                        mes['message'] = "category_id参数错误"
                    else:
                        category_dbref = DBRef(collection=Category.get_table_name(), id=ObjectId(category_id),
                                               database=db_name)
                        args['category_id'] = category_dbref
                        r = None
                        try:
                            r = Project.add_instance(**args)
                        except Exception as e:
                            mes['message'] = str(e)
                        finally:
                            if r is None and mes['message'] == "success":
                                mes['message'] = "添加失败"
                            else:
                                pass
                elif key2 == "edit":
                    """编辑"""
                    args = get_args(request)
                    if "_id" in args:
                        o_id = args.pop("_id")
                        category_id = args.get("category_id")
                        if category_id is None or len(category_id) != 24:
                            mes['message'] = "category_id参数错误"
                        else:
                            category_dbref = DBRef(collection=Category.get_table_name(), id=ObjectId(category_id),
                                                   database=db_name)
                            args['category_id'] = category_dbref
                            begin_date = get_datetime_from_str(args.get("begin_date"))
                            if isinstance(begin_date, datetime.datetime):
                                args['begin_date'] = begin_date
                            end_date = get_datetime_from_str(args.get("end_date"))
                            if isinstance(end_date, datetime.datetime):
                                args['end_date'] = end_date
                            r = Project.update_instance(o_id, args)
                            if r is None:
                                mes['message'] = "保存失败,请检查错误日志"
                            else:
                                pass
                    else:
                        mes['message'] = "id必须"
                elif key2 == "get":
                    """查询"""
                    o_id = get_arg(request, "_id", None)
                    if isinstance(o_id, str) and len(o_id) == 24:
                        o_id = mongo_db.get_obj_id(o_id)
                        pro = Project.find_one_plus(filter_dict={"_id": o_id}, instance=False, can_json=True)
                        if pro is None:
                            mes['message'] = "找不到对应的记录"
                        else:
                            category = category_dict.get(pro['category_id'])
                            if category is not None:
                                pro['category_name'] = category['name']
                                pro['category_path'] = category['path']
                            mes['data'] = pro
                    else:
                        mes['message'] = "id不合法错误"
                else:
                    return abort(401)
            elif key1 == "module":
                """模块"""
                if key2 == "add":
                    """添加"""
                    args = get_args(request)
                    project_id = args.get("project_id")
                    if project_id is None or len(project_id) != 24:
                        mes['message'] = "project_id参数错误"
                    else:
                        project_dbref = DBRef(collection=Project.get_table_name(), id=ObjectId(project_id),
                                              database=db_name)
                        args['project_id'] = project_dbref
                        r = None
                        try:
                            r = Module.add_instance(**args)
                        except Exception as e:
                            mes['message'] = str(e)
                        finally:
                            if r is None and mes['message'] == "success":
                                mes['message'] = "添加失败"
                            else:
                                pass
                elif key2 == "edit":
                    """编辑"""
                    args = get_args(request)
                    if "_id" in args:
                        o_id = args.pop("_id")
                        project_id = args.get("project_id")
                        if project_id is None or len(project_id) != 24:
                            mes['message'] = "project_id参数错误"
                        else:
                            project_dbref = DBRef(collection=Project.get_table_name(), id=ObjectId(project_id),
                                                  database=db_name)
                            args['project_id'] = project_dbref
                            begin_date = get_datetime_from_str(args.get("begin_date"))
                            if isinstance(begin_date, datetime.datetime):
                                args['begin_date'] = begin_date
                            end_date = get_datetime_from_str(args.get("end_date"))
                            if isinstance(end_date, datetime.datetime):
                                args['end_date'] = end_date
                            r = Module.update_instance(o_id, args)
                            if r is None:
                                mes['message'] = "保存失败,请检查错误日志"
                            else:
                                pass
                    else:
                        mes['message'] = "id必须"
                elif key2 == "get":
                    """查询"""
                    o_id = get_arg(request, "_id", None)
                    if isinstance(o_id, str) and len(o_id) == 24:
                        o_id = mongo_db.get_obj_id(o_id)
                        mod = Module.find_one_plus(filter_dict={"_id": o_id}, instance=False, can_json=True)
                        if mod is None:
                            mes['message'] = "找不到对应的记录"
                        else:
                            project_name = project_map.get(mod['project_id'])
                            if project_name is not None:
                                mod['project_name'] = project_name
                            mes['data'] = mod
                    else:
                        mes['message'] = "id不合法错误"
                elif key2 == "children":
                    """查询所属的mission"""
                    module_id = get_arg(request, "module_id", None)
                    if isinstance(module_id, str) and len(module_id) == 24:
                        dbref = DBRef(database=db_name, collection=Module.get_table_name(), id=ObjectId(module_id))
                        f = {"module_id": dbref, "status": {"$nin": ['invalid']}}
                        ms = Mission.find_plus(filter_dict=f, can_json=True)
                        mes['data'] = ms
                    else:
                        mes['message'] = "id不合法错误"
                else:
                    return abort(401)
            elif key1 == "task":
                """模块"""
                if key2 == "add":
                    """添加"""
                    args = get_args(request)
                    project_id = args.get("project_id")
                    module_id = args.get("module_id")
                    mission_id = args.pop("mission_id", None)
                    if project_id is None or len(project_id) != 24:
                        mes['message'] = "project_id参数错误"
                    elif module_id is None or len(module_id) != 24:
                        mes['message'] = "module_id参数错误"
                    else:
                        project_dbref = DBRef(collection=Project.get_table_name(), id=ObjectId(project_id),
                                              database=db_name)
                        module_dbref = DBRef(collection=Module.get_table_name(), id=ObjectId(module_id),
                                             database=db_name)
                        if mission_id is not None:
                            mission_dbref = DBRef(collection=Mission.get_table_name(), id=ObjectId(mission_id),
                                                 database=db_name)
                            args['mission_id'] = mission_dbref
                        args['project_id'] = project_dbref
                        args['module_id'] = module_dbref
                        r = None
                        try:
                            r = Task.add_instance(**args)
                        except Exception as e:
                            mes['message'] = str(e)
                        finally:
                            if r is None and mes['message'] == "success":
                                mes['message'] = "添加失败"
                            else:
                                pass
                elif key2 == "edit":
                    """编辑"""
                    args = get_args(request)
                    if "_id" in args:
                        o_id = args.pop("_id")
                        project_id = args.get("project_id")
                        module_id = args.get("module_id")
                        mission_id = args.pop("mission_id", None)
                        if project_id is None or len(project_id) != 24:
                            mes['message'] = "project_id参数错误"
                        elif module_id is None or len(module_id) != 24:
                            mes['message'] = "module_id参数错误"
                        else:
                            project_dbref = DBRef(collection=Project.get_table_name(), id=ObjectId(project_id),
                                                  database=db_name)
                            module_dbref = DBRef(collection=Module.get_table_name(), id=ObjectId(module_id),
                                                 database=db_name)
                            if mission_id is not None:
                                mission_dbref = DBRef(collection=Mission.get_table_name(), id=ObjectId(mission_id),
                                                      database=db_name)
                                args['mission_id'] = mission_dbref
                            args['project_id'] = project_dbref
                            args['module_id'] = module_dbref
                            begin_date = get_datetime_from_str(args.get("begin_date"))
                            if isinstance(begin_date, datetime.datetime):
                                args['begin_date'] = begin_date
                            end_date = get_datetime_from_str(args.get("end_date"))
                            if isinstance(end_date, datetime.datetime):
                                args['end_date'] = end_date
                            r = Task.update_instance(o_id, args)
                            if r is None:
                                mes['message'] = "保存失败,请检查错误日志"
                            else:
                                pass
                    else:
                        mes['message'] = "id必须"
                elif key2 == "delete":
                    """删除"""
                    o_id = get_arg(request, "_id", None)
                    if isinstance(o_id, str) and len(o_id) == 24:
                        t = Task.find_by_id(o_id)
                        if isinstance(t, Task):
                            if t.delete_self():
                                pass
                            else:
                                mes['message'] = "删除失败,请检查错误日志"
                        else:
                            mes['message'] = "没有找到对应的实例"
                    else:
                        mes['message'] = "id不合法错误"
                elif key2 == "get":
                    """查询"""
                    o_id = get_arg(request, "_id", None)
                    if isinstance(o_id, str) and len(o_id) == 24:
                        o_id = mongo_db.get_obj_id(o_id)
                        task = Task.find_one_plus(filter_dict={"_id": o_id}, instance=False, can_json=True)
                        if task is None:
                            mes['message'] = "找不到对应的记录"
                        else:
                            module_name = module_map.get(task['module_id'])
                            if module_name is not None:
                                task['module_name'] = module_name
                            project_name = project_map.get(task['project_id'])
                            if project_name is not None:
                                task['project_name'] = project_name
                            mes['data'] = task
                    else:
                        mes['message'] = "id不合法错误"
                else:
                    return abort(401)
            elif key1 == "mission":
                """功能"""
                if key2 == "add":
                    """添加"""
                    args = get_args(request)
                    project_id = args.get("project_id")
                    module_id = args.get("module_id")
                    if project_id is None or len(project_id) != 24:
                        mes['message'] = "project_id参数错误"
                    elif module_id is None or len(module_id) != 24:
                        mes['message'] = "module_id参数错误"
                    else:
                        project_dbref = DBRef(collection=Project.get_table_name(), id=ObjectId(project_id),
                                              database=db_name)
                        module_dbref = DBRef(collection=Module.get_table_name(), id=ObjectId(module_id),
                                             database=db_name)
                        args['project_id'] = project_dbref
                        args['module_id'] = module_dbref
                        r = None
                        try:
                            r = Mission.add_instance(**args)
                        except Exception as e:
                            mes['message'] = str(e)
                        finally:
                            if r is None and mes['message'] == "success":
                                mes['message'] = "添加失败"
                            else:
                                pass
                elif key2 == "edit":
                    args = get_args(request)
                    if "_id" in args:
                        o_id = args.pop("_id")
                        project_id = args.get("project_id")
                        module_id = args.get("module_id")
                        if project_id is None or len(project_id) != 24:
                            mes['message'] = "project_id参数错误"
                        elif module_id is None or len(module_id) != 24:
                            mes['message'] = "module_id参数错误"
                        else:
                            project_dbref = DBRef(collection=Project.get_table_name(), id=ObjectId(project_id),
                                                  database=db_name)
                            module_dbref = DBRef(collection=Module.get_table_name(), id=ObjectId(module_id),
                                                 database=db_name)
                            args['project_id'] = project_dbref
                            args['module_id'] = module_dbref
                            begin_date = get_datetime_from_str(args.get("begin_date"))
                            if isinstance(begin_date, datetime.datetime):
                                args['begin_date'] = begin_date
                            end_date = get_datetime_from_str(args.get("end_date"))
                            if isinstance(end_date, datetime.datetime):
                                args['end_date'] = end_date
                            r = Mission.update_instance(o_id, args)
                            if r is None:
                                mes['message'] = "保存失败,请检查错误日志"
                            else:
                                pass
                    else:
                        mes['message'] = "id必须"
                elif key2 == "delete":
                    """删除"""
                    o_id = get_arg(request, "_id", None)
                    if isinstance(o_id, str) and len(o_id) == 24:
                        mis = Mission.find_by_id(o_id)
                        if isinstance(mis, Mission):
                            """检查是否有对应的task"""
                            f = {"mission_id": mis.get_dbref(), "status": {"$nin": ['invalid']}}
                            ts = Task.find_plus(filter_dict=f, can_json=True)
                            l = len(ts)
                            if l == 0:
                                if mis.delete_self():
                                    pass
                                else:
                                    mes['message'] = "删除失败,请检查错误日志"
                            else:
                                ms = "有{}个有效的任务和本功能,故无法删除本功能.".format(l)
                                mes['message'] = ms
                        else:
                            mes['message'] = "没有找到对应的实例"
                    else:
                        mes['message'] = "id不合法错误"
                elif key2 == "get":
                    """查询"""
                    o_id = get_arg(request, "_id", None)
                    if isinstance(o_id, str) and len(o_id) == 24:
                        o_id = mongo_db.get_obj_id(o_id)
                        mis = Mission.find_one_plus(filter_dict={"_id": o_id}, instance=False, can_json=True)
                        if mis is None:
                            mes['message'] = "找不到对应的记录"
                        else:
                            module_name = module_map.get(mis['module_id'])
                            if module_name is not None:
                                mis['module_name'] = module_name
                            project_name = project_map.get(mis['project_id'])
                            if project_name is not None:
                                mis['project_name'] = project_name
                            mes['data'] = mis
                    else:
                        mes['message'] = "id不合法错误"

                else:
                    return abort(401)
            else:
                return abort(403)
            return json.dumps(mes)
        else:
            return abort(405)


@app.after_request
def allow_cross_domain(response):
    """允许跨域资源访问管理"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    allow_headers = "Referer,Accept,Origin,User-Agent,X-Auth-Token"
    response.headers['Access-Control-Allow-Headers'] = allow_headers
    # 也可以在此设置cookie
    # resp.set_cookie('username', 'the username')
    return response


if __name__ == '__main__':
    # app.debug = True  # 这一行必须在toolbar = DebugToolbarExtension(app)前面,否则不生效
    # toolbar = DebugToolbarExtension(app)  # 开启html调试toolbar
    # app.run(host="0.0.0.0", port=port, threaded=True)  # 开启DebugToolbar的调试模式. 对应app.debug = True
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)  # 一般调试模式
