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
import base64
import random
import hashlib
from uuid import uuid4
import urllib.request
import os
from uuid import uuid4
from werkzeug.contrib.cache import RedisCache
from log_module import get_logger
from module.system_module import Root
from module.system_module import User


"""公用的函数和装饰器"""
ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif', 'tif')  # 允许上传的图片后缀
logger = get_logger()


def allowed_file(filename):
    """检查上传文件类型"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class MyForm(FlaskForm):
    """只做cstf检测"""
    pass


def save_platform_session(**kwargs) -> bool:
    """保存平台操作者会话信息
    :kwargs 必须包含 user_id user_name user_password三个参数
    return True代表保存成功，False代表保存失败
    """
    user_id = kwargs.get('_id')
    if not user_id:
        return False
    else:
        """验证信息写入session"""
        for k, v in kwargs.items():
            if v is not None:
                session[k] = v
        return True


def clear_platform_session():
    """清除平台操作者会话信息，注销使用。
    return None
    """
    """去掉session中的内容"""
    keys = list(session.keys())
    [session.pop(x, None) for x in keys]
    return False


def check_session(f):
    """检测用户是否登录的装饰器"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("_id")  # 检测session中的user_id
        if isinstance(user_id, ObjectId):
            user = User.find_by_id(o_id=user_id, to_dict=True)
        else:
            user = None
        if user is None:
            return redirect(url_for("user_blueprint.login_func"))
        else:
            kwargs['user'] = user
            return f(*args, **kwargs)
    return decorated_function


def check_root_session(f):
    """检测root用户是否登录的装饰器"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("_id")  # 检测session中的user_id
        if isinstance(user_id, ObjectId):
            user = Root.find_by_id(o_id=user_id, to_dict=True)
        else:
            user = None
        if user is None:
            return redirect(url_for("root_blueprint.login_func"))
        else:
            kwargs['root'] = user
            return f(*args, **kwargs)
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


def check_phone(phone):
    """检查手机号码的合法性，合法的手机返回True"""
    if phone is None:
        return False
    elif isinstance(phone, str) or isinstance(phone, int):
        phone = str(phone).strip()
        if len(phone) == 11 and phone.isdigit() and phone.startswith("1"):
            try:
                int(phone)
                return True
            except ValueError:
                return False
        else:
            return False
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
    arg_dict = dict() if arg_dict is None else arg_dict
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


def normal_distribution_range(bottom_value: (float, int), top_value: (float, int), list_length: int = 1000,
                              value_type: (type, str) = float, decimal_length: int = 1) -> list:
    """
    生成一个正态分布的数组
    :param bottom_value: 正态分布的最小值.
    :param top_value: 正态分布的最大值.
    :param list_length: 返回的数组的长度.
    :param value_type: 返回的数组的元素的类型,默认是float,如果设置为int,那么decimal_length参数将无效.
    :param decimal_length: value_type参数为float的情况下,返回的元素保留几位小数点?默认为1,value_type为int此参数无效.
    :return: 数组
    """
    if not isinstance(bottom_value, float):
        try:
            bottom_value = float(bottom_value)
        except ValueError as e:
            ms = "{}不能转换成一个float对象".format(bottom_value)
            raise ValueError(ms)
        except TypeError as e:
            ms = "{}不能转换成一个float对象".format(bottom_value)
            raise TypeError(ms)
        finally:
            pass
    if not isinstance(top_value, float):
        try:
            top_value = float(top_value)
        except ValueError as e:
            ms = "{}不能转换成一个float对象".format(top_value)
            raise ValueError(ms)
        except TypeError as e:
            ms = "{}不能转换成一个float对象".format(top_value)
            raise TypeError(ms)
        finally:
            pass
    if not isinstance(list_length, int):
        try:
            list_length = int(list_length)
        except ValueError as e:
            ms = "{}不能转换成一个int对象".format(list_length)
            raise ValueError(ms)
        except TypeError as e:
            ms = "{}不能转换成一个int对象".format(list_length)
            raise TypeError(ms)
        finally:
            if list_length < 0:
                raise ValueError("list_length必须是一个正整数.")
    if value_type == int or value_type == float:
        pass
    else:
        if isinstance(value_type, str):
            value_type = value_type.lower()
            if value_type == "int":
                value_type = int
            elif value_type == "float":
                value_type = float
            else:
                ms = "错误的value_type参数:{}".format(value_type)
                raise ValueError(ms)
        else:
            ms = "value_type参数类型错误,期待一个str/type,得到一个{}".format(type(value_type))
            raise TypeError(ms)
    if value_type == int:
        decimal_length = 0
    else:
        if isinstance(decimal_length, int):
            pass
        else:
            try:
                decimal_length = int(decimal_length)
            except ValueError as e:
                ms = "{}不能转换成一个int对象".format(decimal_length)
                raise ValueError(ms)
            except TypeError as e:
                ms = "{}不能转换成一个int对象".format(decimal_length)
                raise TypeError(ms)
            finally:
                if list_length < 0:
                    raise ValueError("decimal_length必须是一个正整数.")
    """开始生产数组"""
    if top_value == bottom_value:
        """等值数组"""
        value = round(float(top_value), decimal_length) if value_type == float else int(top_value)
        return [value] * list_length
    else:
        """开始计算中间值和步长"""
        middle_value = (bottom_value + (top_value - bottom_value) / 2) if top_value > bottom_value else (
            top_value + (bottom_value - top_value) / 2)
        step = abs((top_value - bottom_value)) / 10
    raw_range = np.random.randn(list_length)
    res = [float(str(round(middle_value + step * (-5 if i < -5 else (5 if i > 5 else i)),
                           decimal_length))) if value_type == float else int(
        middle_value + step * (-5 if i < -5 else (5 if i > 5 else i))) for i in raw_range]
    return res


def expand_list(set_list: (list, tuple)) -> list:
    """
    展开嵌套的数组或者元组
    :param set_list: 嵌套的元组或者数组
    :return: 数组
    调用方式 result = expand_list([1,2,[3,4],[5,6,7]])
    """
    res = list()
    for arg in set_list:
        if isinstance(arg, (list, tuple)):
            res.extend(expand_list(arg))
        else:
            res.append(arg)
    return res


if __name__ == "__main__":
        pass



