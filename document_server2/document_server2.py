# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import session
from flask import abort
from flask import send_file
from toolbox.tools_module import get_arg
from toolbox.tools_module import check_session
from toolbox.my_filter import mount_plugin
from flask_session import Session
from redis import Redis
from module.user_module import *
from module.md_module import *
import datetime


app = Flask(__name__)
key_str = os.urandom(24)  # 生成密钥，为session服务。
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_REDIS'] = Redis(host="47.98.113.173", password="yilu2018", port=6379)  # redis连接
# app.config['SESSION_TYPE'] = "filesystem"  # session类型
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间


Session(app)
port = 9500
mount_plugin(app)  # 注册jinja2的自定义过滤器


def nav_bar():
    """
    导航栏数据
    :return:
    """
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
            {"name": "提取打印条码", "path": "/manage/code_export"},
            {"name": "导出查询替换", "path": "/manage/code_pickle"},
        ]},
        {"name": "生产任务", "path": "/manage/task_summary", "class": "fa fa-server", "children": [
            # {"name": "生产任务概况", "path": "/manage/task_summary"},  # 暂时不用
            {"name": "生产任务列表", "path": "/manage/task_manage"},
            {"name": "条码回传记录", "path": "/manage/task_sync"}
        ]},
        {"name": "系统管理", "path": "/manage/user", "class": "fa fa-bar-chart", "children": [
            {"name": "权限组管理", "path": "/manage/role"},
            {"name": "用户管理", "path": "/manage/user"}
        ]}
    ]
    navs = [
        {"name": "文档管理", "path": "/document_list", "class": "fa fa-exclamation-circle", "children": [
            {"name": "文档列表", "path": "/document_list"},
        ]}
    ]
    return navs


@app.route("/hello")
def hello_func():
    return "hello world!"


@app.route('/favicon.ico')
def favicon_func():
    return send_file("static/image/favicon.ico")


@app.route('/login', methods=['get', 'post'])
def login_func():
    if request.method.lower() == 'get':
        return render_template("login.html")
    else:
        user_name = get_arg(request, "user_name")
        password = get_arg(request, "password")
        mes = User.login(user_name=user_name, password=password)
        if mes['message'] == "success":
            session['user_id'] = mes['data']['id']
        return json.dumps(mes)


@app.route('/logout', methods=['get', 'post'])
def logout_func():
    session.clear()
    return redirect(url_for("login_func"))


@app.route("/html/<file_name>", methods=['get', 'post'])
@check_session
def common_func(user: dict, file_name: str = ""):
    """
    通用视图函数
    :param user:
    :param file_name:
    :return:
    """
    names = os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates"))
    file_name = file_name.lower()
    if file_name.endswith(".html"):
        pass
    else:
        file_name = "{}.html".format(file_name.split(".")[0])
    if file_name in names:
        if request.method.lower() == "get":
            kw = dict()
            kw['cur_user'] = user
            kw['navs'] = nav_bar()
            if file_name == "document_list.html":
                """文档列表页"""
                series_list = Document.get_series()
                kw['series_list'] = series_list
                page_index = get_arg(request, "page_num", 1)  # 页码
                file_series = get_arg(request, "file_series", "全部")  # 文件类别
                f = dict()
                if file_series == "全部":
                    pass
                else:
                    f['file_series'] = file_series
                word = get_arg(request, "word",  None)  # 关键词
                if word is None:
                    pass
                else:
                    f['word'] = word
                kw.update(Document.paginate(where=f, page_index=page_index))
            return render_template(file_name, **kw)
        else:
            """各种请求"""
    else:
        return abort(404)


@app.route("/download_file/<_id>")
def download_func(_id):
    """
    下载文件
    :param _id:
    :return:
    """
    f_id = None
    try:
        f_id = int(_id)
    except Exception as e:
        print(e)
    finally:
        if isinstance(f_id, int):
            resp = Document.get_file_path(file_id=f_id)
            file_path = resp['file_path']
            file_name = resp['file_name']
            file_type = resp['file_type']
            """把文件名的中文从utf-8转成latin-1,这是防止中文的文件名造成的混乱"""
            file_name = file_name.encode().decode('latin-1')
            return send_file(
                filename_or_fp=file_path,
                attachment_filename=file_name,
                as_attachment=False,
                mimetype=file_type
            )
        else:
            return abort(404)


@app.route("/read_file")
def read_file_func():
    """
    读取
    :return:
    """
    _id = get_arg(request, "_id", None)
    f_id = None
    try:
        f_id = int(_id)
    except Exception as e:
        print(e)
    finally:
        if isinstance(f_id, int):
            resp = Document.get_file_path(file_id=f_id)
            file_path = resp['file_path']
            file_name = resp['file_name']
            file_type = resp['file_type']
            if file_type.find("markdown") != -1:
                with open(file=file_path, encoding="utf-8", mode="r") as f:
                    text = f.read()
                resp = {
                    "text": text,
                    "file_name": file_name,
                    "file_type": file_type
                }
            else:
                resp = {"file_name": file_name, "text": "不支持的文件格式: {}".format(file_name)}
            return json.dumps(resp)
        else:
            return abort(404)


@app.route("/upload", methods=['post', 'get'])
@check_session
def upload_func(user: dict):
    """
    上传文件
    :param user:
    :return:
    """
    resp = Document.upload_file(req=request, user=user, force=True)
    return json.dumps(resp)


@app.route("/remove_one", methods=['post', 'get'])
@check_session
def remove_one_func(user: dict):
    """
    删除文件
    :param user:
    :return:
    """
    doc_id = get_arg(request, "doc_id", -1)
    user_id = user['id']
    resp = Document.upload_file(user_id=user_id, doc_id=doc_id)
    return json.dumps(resp)


@app.route("/check_name", methods=['post', 'get'])
@check_session
def check_name_func(user: dict):
    """
    上传时,检查文件名是否重复.
    :return:
    """
    file_name = get_arg(request, "file_name", "")



@app.route("/self_info", methods=['post', 'get'])
@check_session
def self_info(user: dict):
    """
    修改个人信息
    :param user:
    :return:
    """
    mes = {"message": "success"}
    r_id = get_arg(request, "_id", 0)
    _id = 0
    try:
        _id = int(r_id)
    except Exception as e:
        print(e)
    finally:
        if _id == 0:
            mes['message'] = "错误的用户id"
        else:
            if user['id'] == _id:
                t = get_arg(request, "type")
                if t == "change_nick":
                    nick_name = get_arg(request, "nick_name", "")
                    mes = User.change_nick(user_id=user['id'], nick_name=nick_name)
                elif t == "change_pw":
                    pw_old = get_arg(request, "pw_old", "")
                    pw_n1 = get_arg(request, "pw_n1", "")
                    pw_n2 = get_arg(request, "pw_n2", "")
                    mes = User.change_pw(user_id=user['id'], old_pw=pw_old, pw1=pw_n1, pw2=pw_n2)
                else:
                    mes['message'] = "未知的操作: {}".format(t)
            else:
                mes['message'] = "只能修改自己的信息"
        return json.dumps(mes)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
