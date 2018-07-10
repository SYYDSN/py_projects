# -*- coding:utf8 -*-
from flask import session, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
import functools
from flask import redirect, url_for
from wtforms import SubmitField
from wtforms.validators import DataRequired
from bson.objectid import ObjectId
from flask_wtf.file import FileRequired, FileAllowed
import datetime
import json
import re
import numpy as np
import random
import hashlib
from uuid import uuid4
import base64
import urllib.request
import os
import jwt
from uuid import uuid4
from werkzeug.contrib.cache import RedisCache
from log_module import get_logger
from log_module import recode


"""公用的函数和装饰器"""
ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif', 'tif')  # 允许上传的图片后缀
cache = RedisCache()
cors_session_timeout = 600  # 跨域用户的会话信息的最大生命间隔
logger = get_logger()


def allowed_file(filename):
    """检查上传文件类型"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_platform_session(**kwargs) -> bool:
    """保存平台操作者会话信息
    :kwargs 必须包含 user_id user_name user_password三个参数
    return True代表保存成功，False代表保存失败
    """
    user_id = kwargs.get('user_id')
    user_name = kwargs.get('user_name')
    user_password = kwargs.get('user_password')
    if not (user_id and user_name and user_password):
        return False
    else:
        """验证信息写入session"""
        for k, v in kwargs.items():
            if v is not None:
                session[k] = v
        return True


def save_platform_cors_session(**kwargs) -> (str, None):
    """保存平台操作者跨域会话信息
    :kwargs 必须包含 user_id user_name user_password,sid四个参数
    return 会话id
    """
    user_id = kwargs.get('user_id')
    user_name = kwargs.get('user_name')
    user_password = kwargs.get('user_password')
    sid = kwargs.get('sid')  # 会话id
    create_date = kwargs.get('create_date')  # 会话创建时间
    result = False
    if user_id is None or None or user_name is None or user_password is None:
        pass
    else:
        """验证信息写入session"""
        now = datetime.datetime.now()
        kwargs['create_date'] = create_date if create_date else now
        kwargs['last_update_date'] = now
        sid = sid if sid else uuid4().hex
        key = "session_key_{}".format(sid)
        """
        timeout是会话刷新间隔,用来确认用户是否还在线?如果在timeout的时间内,
        没有收到用户页面发来的心跳信号,就认为用户已经离线,会删除用户的会话信息.
        默认的心跳信号(会话刷新)间隔为10分钟
        """
        result = sid if cache.set(key, kwargs, timeout=cors_session_timeout) else result
    return result


def clear_platform_session():
    """清除平台操作者会话信息，注销使用。
    return None
    """
    """去掉session中的内容"""
    keys = list(session.keys())
    [session.pop(x, None) for x in keys]
    return False


def check_platform_session(f):
    """检测管操作员是否登录的装饰器,本域和跨域用户共用"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        cors = get_arg(request, "cors", default_value=None)  # 跨域标志
        if cors == 'cors':
            """跨域用户"""
            sid = get_arg(request, "sid", default_value=None)  # 跨域会话id
            user_info = get_platform_cors_session_dict(sid)
            if user_info is None:
                return json.dumps({"message": "invalid session"})
            else:
                now = datetime.datetime.now()
                last_update_date = user_info['last_update_date']
                delta = (now - last_update_date).total_seconds()
                if delta > cors_session_timeout:
                    """会话超时"""
                    clear_platform_cors_session(sid)
                    return json.dumps({"message": "session timeout"})
                else:
                    """放行"""
                    save_platform_cors_session(**user_info)  # 保存/更新跨域的会话
                    return f(*args, **kwargs)
        else:
            """本域用户"""
            user_name = session.get("user_name")  # 检测session中的user_name
            user_password = session.get("user_password")  # user_password
            user_id = session.get("user_id")  # 检测session中的user_id
            if not (user_password and user_name and user_id):
                return redirect(url_for("manage_blueprint.login_func"))
            else:
                checked_user_obj = CompanyAdmin.find_one(user_name=user_name, user_password=user_password)
                if checked_user_obj is None:
                    """用户名和密码不正确"""
                    return redirect(url_for("manage_blueprint.login_func"))
                else:
                    if str(checked_user_obj.get_id()) == user_id:
                        """检查时不是只读管理员,如果是,进行path检查,只允许访问规定的path"""
                        if get_platform_session_arg("only_view"):
                            """是只读管理员,检查当前访问大的path"""
                            allow_paths = ["/manage/online_report"]
                            cur_path = request.path
                            if cur_path in allow_paths:
                                return f(*args, **kwargs)
                            else:
                                """不在许可路径列表内"""
                                return redirect(url_for("manage_blueprint.login_func"))
                        else:
                            return f(*args, **kwargs)
                    else:
                        return redirect(url_for("manage_blueprint.login_func"))
    return decorated_function


def get_platform_session_arg(arg_name: str, default_val: str = None) -> (str, None):
    """
    获取管理平台的session中指定的值
    :param arg_name: 参数名
    :param default_val: 默认的返回值
    :return:
    """
    arg_value = default_val
    try:
        arg_value = session[arg_name]
    except KeyError as e:
        print(e)
    except TypeError as e:
        print(e)
    finally:
        return arg_value


def get_platform_cors_session_dict(session_id: str) -> (dict, None):
    """
    获取跨域用户的信息字典.
    :param session_id:
    :return: 信息字典
    """
    key = "session_key_{}".format(session_id)
    return cache.get(key)


def login_required_app(f):
    """检测管app用户是否登录的装饰器"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        req_args = get_args(request)
        headers = request.headers
        api_url = request.path
        auth_token = request.headers.get("auth_token", None)
        token = request.headers.get("token", None)
        check = token if auth_token is None or auth_token == "" else auth_token
        ms = "api={}, args={}, auth_token={}, token={}, headers={}".format(api_url, req_args, auth_token, token, headers)
        recode(ms)
        if check is None or check == "":
            # 会话检测失败
            logger.exception("app token 获取失败: {}".format(ms))
            message = pack_message({"message": "success"}, 3009, token=token)
            return json.dumps(message)
        else:
            key = "token_{}".format(check)
            user_id = cache.get(key)
            if user_id is None:
                user_id = AppLoginToken.get_id_by_token(token=check).get("user_id", None)
                if user_id is None:
                    # token验证失败
                    logger.exception("app token验证失败: {}".format(ms))
                    message = pack_message({"message": "success"}, 3008, token=token)
                    return json.dumps(message)
                else:
                    kwargs['user_id'] = user_id  # 把user_id作为地一个参数传递给视图函数
                    cache.set(key, user_id, timeout=1200)  # 缓存20分钟
            else:
                kwargs['user_id'] = user_id  # 把user_id作为地一个参数传递给视图函数
        return f(*args, **kwargs)

    return decorated_function


def check_phone(phone):
    """检查手机号码的合法性，合法的手机返回True"""
    if phone is None:
        return False
    elif isinstance(phone, str) or isinstance(phone, int):
        phone = str(phone).strip()
        if len(phone) == 11 and phone.startswith("1"):
            try:
                int(phone)
                return True
            except ValueError:
                return False
        else:
            return False
    else:
        return False


def check_iot_phone(phone):
    """检查手机号码的是不是合法的物联网卡，合法的返回True"""
    pattern = re.compile(r'^1064\d{9}$')
    if pattern.match(phone):
        return True
    else:
        return False


def str_format_list(result, local=False):
    """对数据库查询的结果中的datetime和date对象进行格式化，第一个参数是查询的结果集，元组类型。
    第二个参数是是否用中文年月日表示。以list类型返回处理过的结果"""
    data = []
    if result is not None:
        for x in result:
            if isinstance(x, datetime.datetime):
                temp = x.strftime("%Y{}%m{}%d{} %H{}%M{}%S{}")
                if local:
                    temp = temp.format("年", "月", "日", "时", "分", "秒")
                else:
                    temp = temp.format("-", "-", "", ":", ":", "")
                data.append(temp)
            elif isinstance(x, datetime.date):
                temp = x.strftime("%Y{}%m{}%d{}")
                if local:
                    temp = temp.format("年", "月", "日")
                else:
                    temp = temp.format("-", "-", "")
                data.append(temp)
            else:
                data.append(x)
    else:
        pass
    return data


def get_arg(req, arg, default_value: (str, bool, None)=''):
    """
    flask的request获取参数的简化方法，可以获取get和post的参数。共有三个参数
    1.req  当前的请求。一般都是传入当前上下文的request
    2.arg  参数名称
    3.default_value  未获取到参数时的默认值。默认情况下是空字符
    return 获取到的参数(字符串或默认值)
    """
    temp = req.args.get(arg)
    if temp is None:
        temp = (req.json.get(arg) if req.json is not None else None) if req.form.get(arg) is None else req.form.get(arg)
    temp = default_value if temp is None or temp == '' else temp
    return temp


def get_args(req):
    """一次性取出所有取参数集，注意，参数的值不能是json对象"""
    the_form = req.form
    arg_dict = {k: v for k, v in the_form.items()}
    if len(arg_dict) == 0:
        arg_dict = {k: v for k, v in req.args.items()}
    if len(arg_dict) == 0:
        arg_dict = req.json
    return arg_dict


def get_datetime(number=0, to_str=True):
    """获取日期和时间，以字符串类型返回，格式为：2016-12-19 14:33:03
    number是指在当前日期上延后多少天，默认是0
    to_str 是指是否转换为字符串格式
    """
    now = datetime.datetime.now() + datetime.timedelta(days=number)
    if to_str:
        return now.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return now


def get_real_ip(req):
    """
    获取当前请求的真实ip。参数只有一个：
    1.req  当前的请求。一般都是传入当前上下文的request
    return ip地址(字符串格式)
    注意，如果前端的反向代理服务器是nginx的话，需要在配置文件中加上几句。
    在location / 配置下面的proxy_pass   http://127.0.0.1:5666; 后面加上
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    然后才可以用headers["X-Forwarded-For"]取真实ip
    虽然只加proxy_set_header X-Real-IP $remote_addr;这一句的话。
    也可以用request.headers["X-Real-IP"]获取。
    但为了和IIS的兼容性。还是需要再加一句
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    参数
    :parm req: flask 是request对象，
    tornado是 tornado.web.RequestHandler.request或者tornado.websocket.WebSocketHandler.reuest
    """
    try:
        ip = req.headers["X-Forwarded-For"].split(":")[0]
    except KeyError as e:
        ip = req.remote_addr  # 注意：tornado是 request.remote_ip   flask是 req.remote_addr
    if ip.find(",") != -1:
        """处理微信登录时转发的双ip"""
        ip = ip.split(",")[0]
    return ip


if __name__ == "__main__":
    pass

