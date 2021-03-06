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
from module.online_module import get_online_report
from module.online_module import MonthActive
import json
from json import JSONDecodeError
from module.user_module import *
from module.graph_module import *
from module.project_module import *
from mongo_db import get_datetime_from_str
import pyquery
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
    此方法目前无效,没有使用
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


@app.route("/", methods=['get'])
@check_platform_session
def index_func2():
    """首页2,跳转到登录页"""
    return redirect("/login")


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
            save_dict['user_id'] = mes['data']['_id']
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


@app.route("/login_out", methods=['post'])
@check_platform_session
def login_out_func():
    """注销"""
    clear_platform_session()
    return json.dumps({"message": "success"})


@app.route("/online_report", methods=['post', 'get'])
@check_platform_session
def online_report_func():
    """在线人数报告页面"""
    if request.method.lower() == "get":
        data = get_online_report()
        return render_template("online_report.html", data=data)
    else:
        user_id = get_arg(request, "user_id", None)
        if user_id is None:
            """查询月活跃数据"""
            year = get_arg(request, "year", None)
            month = get_arg(request, "month", None)
            now = datetime.datetime.now()
            year = now.year if year is None else int(year)
            month = now.month if month is None else int(month)
            data = MonthActive.find_chart_info(year=year, month=month)
            return json.dumps(data)
        else:
            """查询个人的上线情况,目前没实现"""
            return abort(404)


@app.route("/flow_chart", methods=['post', 'get'])
@check_platform_session
def flow_chart_func():
    """
    流程图页面
    存在权限混乱的问题,暂时没解决.
    1. 用户只能操作自己创建的图,别人创建的图只能浏览不能修改和删除
    2. 现阶段,还不能对已创建的图的信息进行修改.
    """
    user_id = get_platform_session_arg("user_id")
    if user_id is None:
        return redirect(url_for("login_func"))
    else:
        user = User.find_by_id(o_id=user_id)
        if request.method.lower() == "get":
            digraph_list = MyDigraph.find_plus(filter_dict=dict(), to_dict=True)
            _id = get_arg(request, "did", "")
            if len(_id) == 24:
                for x in digraph_list:
                    if str(x['_id']) == _id:
                        digraph = x
                        digraph['_id'] = _id
                        digraph.pop("image")
                        digraph['time'] = digraph['time'].strftime("%Y-%m-%d %H:%M:%S")
                        digraph['owner'] = str(digraph['owner'].id)
                        new_editors = list()
                        for y in digraph['editors']:
                            new_editors.append(str(y.id))
                        digraph['editors'] = new_editors
                        break
            return render_template("flow_chart.html", digraph_list=digraph_list, _id=_id)
        elif request.method.lower() == "post":
            mes = {"message": "success"}
            init = json.loads(get_arg(request, "init", "{}"))
            the_class = get_arg(request, "class", None)
            the_type = get_arg(request, "type", None)
            if the_type not in ['save', 'delete', 'view']:
                mes['message'] = "不支持的操作:{}".format(the_type)
            else:
                if the_class == "digraph":
                    """对图的操作"""
                    init['owner'] = user_id
                    if the_type == "save":
                        """添加/编辑图"""
                        digraph = MyDigraph(**init)
                        r = digraph.save_plus(upsert=True)
                        if isinstance(r, ObjectId):
                            mes['_id'] = str(r)
                        else:
                            mes['message'] = "保存失败"
                    elif the_type == "view":
                        mes = dict()
                        f = {"_id": ObjectId(get_arg(request, "did", None))}
                        digraph = MyDigraph.find_one_plus(filter_dict=f, instance=True)
                        html = digraph.get_attr('image')
                        if html == b"":
                            svg = ""
                        else:
                            pq = pyquery.PyQuery(html)
                            pq.find("svg")
                            svg = pq.outer_html()
                        data = dict()
                        data['svg'] = svg
                        node_dict = dict()
                        edge_dict = dict()
                        nodes = digraph.get_attr('nodes')
                        edges = digraph.get_attr('edges')
                        for node in nodes:
                            node['_id'] = node['name']
                            node['name'] = node['desc']
                            node_dict[node['_id']] = node
                        for edge in edges:
                            edge_dict[edge['_id']] = edge
                        data['title'] = digraph.get_attr("name")
                        data['node_dict'] = node_dict
                        data['edge_dict'] = edge_dict
                        mes['data'] = data
                    elif the_type == 'delete':
                        """删除图"""
                        did = init.pop("did")
                        f = {"_id": ObjectId(did)}
                        r = MyDigraph.find_one_and_delete(filter_dict=f)
                        if isinstance(r, dict):
                            f = dict()
                            one = MyDigraph.find_one_plus(filter_dict=f, instance=False, can_json=True)
                            if one is None:
                                pass
                            else:
                                mes['_id'] = one['_id']
                        else:
                            mes['message'] = "删除失败"
                    else:
                        mes['message'] = '不支持的操作'
                elif the_class == "edge":
                    """对弧的操作"""
                    if the_type == "save":
                        """添加/编辑弧"""
                        did = init.pop("did")
                        digraph = MyDigraph.find_by_id(o_id=did)
                        edges = digraph.get_attr('edges')
                        _id = init.get("_id")
                        if _id:
                            for edge in edges:
                                if edge['_id'] == init['_id']:
                                    edge['tail_name'] = init['tail_name']
                                    edge['head_name'] = init['head_name']
                                    edge['label'] = init['label']
                                    edge['desc'] = init['desc']
                                    break
                        else:
                            edges.append(Edge(**init))
                        digraph.set_attr("edges", edges)
                        html = digraph.draw()
                        pq = pyquery.PyQuery(html)
                        pq.find("svg")
                        svg = pq.outer_html()
                        r = digraph.save_plus(upsert=True)
                        if isinstance(r, ObjectId):
                            data = dict()
                            data['svg'] = svg
                            data['title'] = digraph.get_attr("name")
                            node_dict = dict()
                            edge_dict = dict()
                            nodes = digraph.get_attr('nodes')
                            edges = digraph.get_attr('edges')
                            for node in nodes:
                                node['_id'] = node['name']
                                node['name'] = node['desc']
                                node_dict[node['_id']] = node
                            for edge in edges:
                                edge_dict[edge['_id']] = edge
                            data['title'] = digraph.get_attr("name")
                            data['node_dict'] = node_dict
                            data['edge_dict'] = edge_dict
                            mes['data'] = data
                        else:
                            mes['message'] = "保存失败"
                    elif the_type == 'delete':
                        """删除弧"""
                        did = init.pop("did")
                        digraph = MyDigraph.find_by_id(o_id=did)
                        edges = digraph.get_attr('edges')
                        for i, edge in enumerate(edges):
                            if edge['_id'] == init['_id']:
                                edges.pop(i)
                                break
                        digraph.set_attr("edges", edges)
                        html = digraph.draw()
                        pq = pyquery.PyQuery(html)
                        pq.find("svg")
                        svg = pq.outer_html()
                        r = digraph.save_plus(upsert=True)
                        if isinstance(r, ObjectId):
                            data = dict()
                            data['svg'] = svg
                            data['title'] = digraph.get_attr("name")
                            node_dict = dict()
                            edge_dict = dict()
                            nodes = digraph.get_attr('nodes')
                            edges = digraph.get_attr('edges')
                            for node in nodes:
                                node['_id'] = node['name']
                                node['name'] = node['desc']
                                node_dict[node['_id']] = node
                            for edge in edges:
                                edge_dict[edge['_id']] = edge
                            data['title'] = digraph.get_attr("name")
                            data['node_dict'] = node_dict
                            data['edge_dict'] = edge_dict
                            mes['data'] = data
                        else:
                            mes['message'] = "删除失败"
                    else:
                        mes['message'] = '不支持的操作'
                elif the_class == "node":
                    """对节点的操作"""
                    if the_type == "save":
                        """添加/编辑节点"""
                        did = init.pop("did")
                        digraph = MyDigraph.find_by_id(o_id=did)
                        nodes = digraph.get_attr('nodes')
                        if "name" not in init:
                            """新节点"""
                            nodes.append(Node(**init))
                        else:
                            for node in nodes:
                                if node['name'] == init['name']:
                                    node['shape'] = init['shape']
                                    node['label'] = init['label']
                                    node['desc'] = init['desc']
                                    break
                        digraph.set_attr("nodes", nodes)
                        html = digraph.draw()
                        pq = pyquery.PyQuery(html)
                        pq.find("svg")
                        svg = pq.outer_html()
                        r = digraph.save_plus(upsert=True)
                        if isinstance(r, ObjectId):
                            data = dict()
                            data['svg'] = svg
                            data['title'] = digraph.get_attr("name")
                            node_dict = dict()
                            edge_dict = dict()
                            nodes = digraph.get_attr('nodes')
                            edges = digraph.get_attr('edges')
                            for node in nodes:
                                node['_id'] = node['name']
                                node['name'] = node['desc']
                                node_dict[node['_id']] = node
                            for edge in edges:
                                edge_dict[edge['_id']] = edge
                            data['title'] = digraph.get_attr("name")
                            data['node_dict'] = node_dict
                            data['edge_dict'] = edge_dict
                            mes['data'] = data
                        else:
                            mes['message'] = "保存失败"
                    elif the_type == 'delete':
                        """删除节点"""
                        did = init.pop("did")
                        digraph = MyDigraph.find_by_id(o_id=did)
                        nodes = digraph.get_attr('nodes')
                        for i, node in enumerate(nodes):
                            if node['name'] == init['name']:
                                nodes.pop(i)
                                break
                        digraph.set_attr("nodes", nodes)
                        html = digraph.draw()
                        pq = pyquery.PyQuery(html)
                        pq.find("svg")
                        svg = pq.outer_html()
                        r = digraph.save_plus(upsert=True)
                        if isinstance(r, ObjectId):
                            data = dict()
                            data['svg'] = svg
                            data['title'] = digraph.get_attr("name")
                            node_dict = dict()
                            edge_dict = dict()
                            nodes = digraph.get_attr('nodes')
                            edges = digraph.get_attr('edges')
                            for node in nodes:
                                node['_id'] = node['name']
                                node['name'] = node['desc']
                                node_dict[node['_id']] = node
                            for edge in edges:
                                edge_dict[edge['_id']] = edge
                            data['title'] = digraph.get_attr("name")
                            data['node_dict'] = node_dict
                            data['edge_dict'] = edge_dict
                            mes['data'] = data
                        else:
                            mes['message'] = "删除失败"
                    else:
                        mes['message'] = '不支持的操作'
                else:
                    mes['message'] = '错误的对象类型:{}'.format(the_class)
            return json.dumps(mes)
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
                        category_list.append(
                            {"_id": category_id, "name": category['name'], "status": (status1, status2)})
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
                    args = get_args(request)
                    o_id = args.pop("_id", None)
                    r = None
                    try:
                        r = Category.update_instance(o_id=o_id, update_dict=args)
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
    allow_edit_pid_name = list()  # 允许编辑的项目的id和name组成的字典的数组
    allow_edit_pids = list()  # 允许编辑的项目的id组成的数组
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
    cur_user_allow_edit_category_list = get_platform_session_arg("allow_edit")
    for m in modules:
        m_id = m['_id']
        if m['category_id'] in cur_user_allow_edit_category_list:
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
    year = int(get_arg(request, "year")) if get_arg(request, "year", "").isdecimal() else now.year
    month = int(get_arg(request, "month")) if get_arg(request, "month", "").isdecimal() else now.month
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
                               "fail": "失败",
                               "drop": "放弃",
                               "suspend": "暂停",
                               "delay": "超期"}
                task_dict = dict()  # 任务字典,用于向前端传递任务信息
                print_error = True
                for line in range(min_line_count + 1):
                    task = None
                    try:
                        task = tasks[line]
                        """计算任务工期"""
                        begin_date = get_datetime_from_str(task['begin_date'])
                        end_date = get_datetime_from_str(task['end_date']) if task.get("end_date") is not None else now
                        date_range = Task.calculate_date_range(begin_date, end_date)
                        task['date_range'] = date_range
                        task['begin_date_str'] = begin_date.strftime("%F")  # 注意，只有task的字段名不同
                        task['end_date_str'] = end_date.strftime("%F")  # 注意，只有task的字段名不同
                    except IndexError as e:
                        if print_error:
                            ms = "计算任务工期出现错误,{}, 一般情况下可忽略".format(e)
                            print(ms)
                            print_error = False
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
                                    raw_status = task['status']
                                    status = status_dict[raw_status]
                                    project_id = str(task['project_id'].id)
                                    project_name = project_map[project_id]
                                    category_name = project_category_map[project_id]['name']
                                    the_begin_date = task['begin_date']
                                    description = "" if task.get('description') is None else task['description']
                                    if status == "正常":
                                        if the_begin_date <= now:
                                            status = "推进中"
                                        else:
                                            status = "未开始"
                                    task_id = str(task['_id'])
                                    temp = {
                                        "_id": task_id,
                                        "category_name": category_name,
                                        "project_name": project_name,
                                        "begin_date": the_begin_date.strftime("%F"),
                                        "end_date": task['end_date'].strftime("%F"),
                                        "type": task['type'],
                                        "status": status,
                                        "raw_status": raw_status,
                                        "date_range": task['date_range'],
                                        "name": task['name'],
                                        "description": description,
                                        "colspan": (end_day - begin_day) + 1
                                    }
                                    task_dict[task_id] = temp
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
                tree_dict = {"name": "必弘信息", "children": c_list}  # 产品架构树
                """ 求下个月第一天"""
                next_month_first = get_datetime_from_str("{}-{}-{}".format(year, month, last_day)) + \
                                   datetime.timedelta(days=1)
                """ 求上个月最后一天"""
                prev_month_last = get_datetime_from_str("{}-{}-1".format(year, month)) - datetime.timedelta(days=1)
                next_year = next_month_first.year
                next_month = next_month_first.month
                prev_year = prev_month_last.year
                prev_month = prev_month_last.month
                return render_template("home_template.html", trs=rows, allow_edit=allow_edit, categories=categories,
                                       allow_view=allow_view, cur_method=cur_method, days=days, weeks=weeks,
                                       current_month=current_month_str, allow_edit_projects=allow_edit_projects,
                                       allow_edit_modules=allow_edit_modules, nav_projects=all_projects,
                                       nav_modules=modules, nav_missions=missions, tasks=tasks, tree_dict=tree_dict,
                                       module_mission_dict=module_mission_dict, allow_edit_pids=allow_edit_pids,
                                       allow_edit_mids=allow_edit_mids, user_name=user_name, task_dict=task_dict,
                                       next_year=next_year, next_month=next_month, prev_year=prev_year,
                                       prev_month=prev_month)
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
                        begin_date = get_datetime_from_str(args.pop('begin_date', None))
                        end_date = get_datetime_from_str(args.pop('end_date', None))
                        if not isinstance(begin_date, datetime.datetime) or not isinstance(end_date, datetime.datetime):
                            mes['message'] = "开始和结束时间不能为空"
                        elif begin_date > end_date:
                            mes['message'] = "开始时间不能晚于结束时间"
                        else:
                            args['begin_date'] = begin_date
                            args['end_date'] = end_date
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
                            begin_date = get_datetime_from_str(args.pop('begin_date', None))
                            end_date = get_datetime_from_str(args.pop('end_date', None))
                            if not isinstance(begin_date, datetime.datetime) or not isinstance(end_date,
                                                                                               datetime.datetime):
                                mes['message'] = "开始和结束时间不能为空"
                            elif begin_date > end_date:
                                mes['message'] = "开始时间不能晚于结束时间"
                            else:
                                args['begin_date'] = begin_date
                                args['end_date'] = end_date
                                r = Project.update_instance(o_id, args)
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
                        pro = Project.find_by_id(o_id)
                        if isinstance(pro, Project):
                            """检查是否有对应的module"""
                            f = {"project_id": pro.get_dbref(), "status": {"$nin": ['invalid']}}
                            mods = Module.find_plus(filter_dict=f, can_json=True)
                            mod_l = len(mods)
                            if mod_l == 0:
                                pro.set_attr("status", "invalid")
                                result = pro.save_plus()
                                if result:
                                    pass
                                else:
                                    mes['message'] = "删除失败,请检查错误日志"
                            else:
                                ms = "多个有效的模块/任务和此项目相关,无法删除."
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
                        begin_date = get_datetime_from_str(args.pop('begin_date', None))
                        end_date = get_datetime_from_str(args.pop('end_date', None))
                        if not isinstance(begin_date, datetime.datetime) or not isinstance(end_date, datetime.datetime):
                            mes['message'] = "开始和结束时间不能为空"
                        elif begin_date > end_date:
                            mes['message'] = "开始时间不能晚于结束时间"
                        else:
                            args['begin_date'] = begin_date
                            args['end_date'] = end_date
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
                            begin_date = get_datetime_from_str(args.pop('begin_date', None))
                            end_date = get_datetime_from_str(args.pop('end_date', None))
                            if not isinstance(begin_date, datetime.datetime) or not isinstance(end_date,
                                                                                               datetime.datetime):
                                mes['message'] = "开始和结束时间不能为空"
                            elif begin_date > end_date:
                                mes['message'] = "开始时间不能晚于结束时间"
                            else:
                                args['begin_date'] = begin_date
                                args['end_date'] = end_date
                                r = Module.update_instance(o_id, args)
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
                        mod = Module.find_by_id(o_id)
                        if isinstance(mod, Module):
                            """检查是否有对应的task"""
                            f = {"module_id": mod.get_dbref(), "status": {"$nin": ['invalid']}}
                            ts = Task.find_plus(filter_dict=f, can_json=True)
                            ts_l = len(ts)
                            """检查是否有对应的mission"""
                            mis = Mission.find_plus(filter_dict=f, can_json=True)
                            mis_l = len(mis)
                            if mis_l == 0 and ts_l == 0:
                                mod.set_attr("status", "invalid")
                                result = mod.save_plus()
                                if result:
                                    pass
                                else:
                                    mes['message'] = "删除失败,请检查错误日志"
                            else:
                                ms = "有{}个有效的任务,{}个有效的功能和本模块相关,故无法删除本模块.".format(ts_l, mis_l)
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
                        begin_date = get_datetime_from_str(args.pop('begin_date', None))
                        end_date = get_datetime_from_str(args.pop('end_date', None))
                        if not isinstance(begin_date, datetime.datetime) or not isinstance(end_date, datetime.datetime):
                            mes['message'] = "开始和结束时间不能为空"
                        elif begin_date > end_date:
                            mes['message'] = "开始时间不能晚于结束时间"
                        else:
                            args['begin_date'] = begin_date
                            args['end_date'] = end_date
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
                            begin_date = get_datetime_from_str(args.pop('begin_date', None))
                            end_date = get_datetime_from_str(args.pop('end_date', None))
                            if not isinstance(begin_date, datetime.datetime) or not isinstance(end_date,
                                                                                               datetime.datetime):
                                mes['message'] = "开始和结束时间不能为空"
                            elif begin_date > end_date:
                                mes['message'] = "开始时间不能晚于结束时间"
                            else:
                                args['begin_date'] = begin_date
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
                            t.set_attr("status", "invalid")
                            result = t.save_plus()
                            if result:
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
                        begin_date = get_datetime_from_str(args.pop('begin_date', None))
                        end_date = get_datetime_from_str(args.pop('end_date', None))
                        if not isinstance(begin_date, datetime.datetime) or not isinstance(end_date, datetime.datetime):
                            mes['message'] = "开始和结束时间不能为空"
                        elif begin_date > end_date:
                            mes['message'] = "开始时间不能晚于结束时间"
                        else:
                            args['begin_date'] = begin_date
                            args['end_date'] = end_date
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
                            begin_date = get_datetime_from_str(args.pop('begin_date', None))
                            end_date = get_datetime_from_str(args.pop('end_date', None))
                            if not isinstance(begin_date, datetime.datetime) or not isinstance(end_date,
                                                                                               datetime.datetime):
                                mes['message'] = "开始和结束时间不能为空"
                            elif begin_date > end_date:
                                mes['message'] = "开始时间不能晚于结束时间"
                            else:
                                args['begin_date'] = begin_date
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
                            length = len(ts)
                            if length == 0:
                                mis.set_attr("status", "invalid")
                                result = mis.save_plus()
                                if result:
                                    pass
                                else:
                                    mes['message'] = "删除失败,请检查错误日志"
                            else:
                                ms = "有{}个有效的任务和本功能有关,故无法删除本功能.".format(length)
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


@app.route("/sf_chart")
def sf_chart_func():
    """顺丰演示"""
    title = "行车事件"
    events = [{'type': '超速', 'user_id': '59cda964ad01be237680e29d', 'end_speed': 100.224,
               'end': '2017-12-21 01:12:58', 'altitude': 15.0, 'av_speed': 97.0188679245283,
               'longitude': 121.24908854166667, 'begin': '2017-12-21 01:12:56',
               "user_name": "栾新军",
               'latitude': 31.282752278645834, 'begin_speed': 73.152},
              {'type': '急加速', 'user_id': '59cda964ad01be237680e29d', 'end_speed': 100.224,
               'end': '2017-12-21 01:12:58', 'altitude': 15.0, 'speed_delta': 10.641509433962264,
               "user_name": "栾新军",
               'longitude': 121.24908854166667, 'begin': '2017-12-21 01:12:56',
               'latitude': 31.282752278645834, 'begin_speed': 73.152},
              {'type': '超速', 'user_id': '59cda964ad01be237680e29d', 'end_speed': 74.772,
               'end': '2017-12-12 00:11:51', 'altitude': 14.0, 'av_speed': 93.31432114073156,
               "user_name": "栾新军",
               'longitude': 119.54578396267361, 'begin': '2017-12-12 00:11:50',
               'latitude': 32.042974175347226, 'begin_speed': 75.744},
              {'type': '超速', 'user_id': '5ab0ae831315e00e3cb61db8', 'end_speed': 80.64,
               "user_name": "童小平",
               'end': '2018-05-09 15:19:49', 'altitude': 139.69, 'av_speed': 121.806,
               'longitude': 112.34155490451388, 'begin': '2018-05-09 15:19:47',
               'latitude': 28.62666232638889, 'begin_speed': 81.756},
              {'type': '急加速', 'user_id': '5ab0ae831315e00e3cb61db8', 'end_speed': 13.536,
               "user_name": "童小平",
               'end': '2018-04-16 16:10:31', 'altitude': -0.6, 'speed_delta': 13.536,
               'longitude': 113.1507630750868, 'begin': '2018-04-16 16:10:30',
               'latitude': 28.128487141927085, 'begin_speed': 0.0},
              {'type': '急加速', 'user_id': '5aaf2f3ee39a7b6f4b6ce26f', 'end_speed': 30.852,
               'end': '2018-04-17 18:38:36', 'altitude': 26.0, 'speed_delta': 30.852,
               'longitude': 115.3997252061632, 'begin': '2018-04-17 18:38:35',
               "user_name": "刘江鹏",
               'latitude': 28.435247395833333, 'begin_speed': 0.0}]

    return render_template("sf_chart.html", title=title, events=events)


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
    """socketIO启动方式,不能进入调试模式"""
    # from flask_socketio import SocketIO
    # socketio = SocketIO(app)
    # socketio.run(app=app, host="0.0.0.0", port=port, threaded=True)
