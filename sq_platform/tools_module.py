# -*- coding:utf8 -*-
from flask import session, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from functools import wraps
from flask import redirect, url_for
from wtforms import SubmitField
from wtforms.validators import DataRequired
from bson.objectid import ObjectId
from flask_wtf.file import FileRequired, FileAllowed
import datetime
from error_module import pack_message
import json
import re
import numpy as np
from manage.company_module import CompanyAdmin
import random
import hashlib
from uuid import uuid4
import base64
import urllib.request
import os
from manage.company_module import Company
from uuid import uuid4
from api.data.item_module import AppLoginToken, User
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


class MyForm(FlaskForm):
    """只做cstf检测"""
    pass


class HandlerLoginForm(FlaskForm):
    """操作员登录用"""
    handler_name = StringField('handler_name', validators=[DataRequired()])
    handler_password = PasswordField('handler_password', validators=[DataRequired()])


class VisitorLoginForm(FlaskForm):
    """来宾登录用"""
    v_email = StringField('v_email', validators=[DataRequired()])


def create_rand(low_limit):
    """随机生成一个百分比,参数low_limit是最低的下限，返回的是字符串格式的百分比"""


def save_platform_session(**kwargs) -> bool:
    """保存平台操作者会话信息
    :kwargs 必须包含 user_id user_name user_password三个参数
    return True代表保存成功，False代表保存失败
    """
    user_id = kwargs.get('user_id')
    user_name = kwargs.get('user_name')
    user_password = kwargs.get('user_password')
    if not (user_id and user_name and user_password):
        """去掉session中的内容"""
        keys = list(session.keys())
        [session.pop(x) for x in keys]
        return False
    else:
        """验证信息写入session"""
        for k, v in kwargs.items():
            if v is not None:
                session[k] = v
        return True


def get_company_from_req(req: request) -> (dict, None):
    """
    根据request的host参数判断是哪个公司登录?
    :param req: flask的request对象
    :return:
    """
    domain = req.host.split(":")[0]
    default_company = {
                "_id": ObjectId("5aab48ed4660d32b752a7ee9"),
                "full_name": " 江西新振兴投资集团有限公司",
                "domain": "xzx.safego.org",
                "description": "用于高安项目的公司",
                "prefix": "xzx",
                "short_name": "新振兴"
            }
    key = 'domain_company_{}'.format(domain)
    company = cache.get(key)
    if company is None:
        f_dict = {"domain": domain}
        if domain.startswith("192.168.") or domain == "127.0.0.1":
            """开发调试状态,当前项目是新振兴"""
            company = default_company
        else:
            company = Company.find_one_plus(filter_dict=f_dict, instance=False)
        """写缓存"""
        if company is not None:
            cache.set(key=key, value=company, timeout=900)  # 15分钟
        else:
            pass
    else:
        pass
    """调试状态下,默认是新振兴公司"""
    if company is None:
        return default_company
    else:
        return company


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
    [session.pop(x) for x in keys]
    return False


def clear_platform_cors_session(sid: str) -> bool:
    """
    清除平台操作者跨域会话信息，注销使用。
    :param sid: 用户会话id
    :return: True / False
    """
    key = "session_key_{}".format(sid)
    return bool(cache.delete(key=key))


def check_platform_session(f):
    """检测管操作员是否登录的装饰器,本域和跨域用户共用"""
    @wraps(f)
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
                last_upate_date = user_info['last_update_date']
                delta = (now - last_upate_date).total_seconds()
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
            prefix = 'sf'
            user_name = session.get("user_name")  # 检测session中的user_name
            user_password = session.get("user_password")  # user_password
            user_id = session.get("user_id")  # 检测session中的user_id
            prefix = prefix if session.get("prefix") is None else session.get("prefix")
            if not (user_password and user_name and user_id):
                return redirect(url_for("manage_blueprint.login_func", prefix=prefix))
            else:
                checked_user_obj = CompanyAdmin.find_one(user_name=user_name, user_password=user_password)
                if checked_user_obj is None:
                    """用户名和密码不正确"""
                    return redirect(url_for("manage_blueprint.login_func", prefix=prefix))
                else:
                    if str(checked_user_obj.get_id()) == user_id:
                        return f(*args, **kwargs)
                    else:
                        return redirect(url_for("manage_blueprint.login_func", prefix=prefix))
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
    @wraps(f)
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
                    cache.set(key, user_id, timeout=7200)  # 缓存2小时
            """比对是否一致?"""
            if user_id is not None:
                kwargs['user_id'] = user_id  # 把user_id作为地一个参数传递给视图函数
            else:
                # token验证失败
                logger.exception("app token验证失败: {}".format(ms))
                message = pack_message({"message": "success"}, 3008, token=token)
                return json.dumps(message)
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


def get_datetime_from_str(date_str: str) -> datetime.datetime:
    """
    根据字符串返回datetime对象
    :param date_str: 表示时间的字符串."%Y-%m-%d %H:%M:%S  "%Y-%m-%d %H:%M:%S.%f 或者 "%Y-%m-%d
    :return: datetime.datetime对象
    """
    if isinstance(date_str, (datetime.datetime, datetime.date)):
        return date_str
    elif isinstance(date_str, str):
        date_str.strip()
        search = re.search(r'\d{4}.\d{1,2}.*\d', date_str)
        if search:
            date_str = search.group()
            pattern_0 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d$')  # 时间匹配2017-01-01
            pattern_1 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d$')  # 时间匹配2017-01-01 12:00:00
            pattern_2 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d\.\d+$') # 时间匹配2017-01-01 12:00:00.000
            pattern_3 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d\s\d+$') # 时间匹配2017-01-01 12:00:00 000
            pattern_4 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d$')  # 时间匹配2017-01-01T12:00:00
            pattern_5 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\.\d+$') # 时间匹配2017-01-01T12:00:00.000
            pattern_6 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\.\d{1,3}Z$')  # 时间匹配2017-01-01T12:00:00.000Z
            pattern_7 = re.compile(r'^[1-2]\d{3}-[01]?\d-[0-3]?\dT[012]?\d:[0-6]?\d:[0-6]?\d\s\d+$')  # 时间匹配2017-01-01T12:00:00 000

            if pattern_7.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S %f")
            elif pattern_6.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            elif pattern_5.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            elif pattern_4.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            elif pattern_3.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %f")
            elif pattern_2.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
            elif pattern_1.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            elif pattern_0.match(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d")
            else:
                ms = "get_datetime_from_str() 参数 {} 时间字符串格式不符合要求 2017-01-01或者2917-01-01 12:00:00".format(date_str)
                print(ms)
                logger.info(ms, exc_info=True, stack_info=True)
        else:
            ms = "get_datetime_from_str() 参数 {} 时间字符串格式匹配失败".format(date_str)
            print(ms)
            logger.info(ms, exc_info=True, stack_info=True)
    else:
        ms = "get_datetime_from_str() 参数 {} 格式错误，期待str，得到一个 {}".format(date_str, type(date_str))
        print(ms)
        logger.info(ms, exc_info=True, stack_info=True)


def round_datetime(the_datetime: datetime.datetime) -> datetime.datetime:
    """
    对一个datetime进行取整,去掉小时分和毫秒,只保留年月日
    :param the_datetime: 待取整的对象
    :return: 取整后的对象
    """
    if isinstance(the_datetime, datetime.datetime):
        return datetime.datetime.strptime(the_datetime.strftime("%F"), "%Y-%m-%d")
    else:
        raise TypeError("期待一个datetime.datetime类型,的到一个{}类型".format(type(the_datetime)))


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


