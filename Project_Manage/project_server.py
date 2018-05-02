# -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import make_response
from flask import render_template
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
from tools_module import *
import os


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
            save_platform_session(**save_dict)

        else:
            clear_platform_session()
        resp = make_response(json.dumps(mes))
        # resp.headers.set("Access-Control-Allow-Origin", "*")
        return resp
    else:
        return abort(405)


@app.route("/manage_<key1>/<key2>", methods=['post', 'get'])
def manage_user_func(key1, key2):
    """
    管理页面,只有proot用户能访问
    key1 是页面的类别,key2是不同的操作,其中get请求不需要key2
    """
    if request.method.lower() == "get":
        """获取全部category"""
        categories = Category.get_all(ignore=["invalid"], can_json=True)
        categories.sort(key=lambda obj: obj['name'])
        if key1 == "user":
            """用户管理界面"""
            category_names = [x['name'] for x in categories]
            column_length = 4 + len(category_names)
            return render_template("manage_user.html", category_names=category_names, key=key1,
                                   column_length=column_length, categories=categories)
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
                                mes['message'] = "添加失败"
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
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)