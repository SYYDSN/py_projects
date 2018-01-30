# -*- coding:utf8 -*-
from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from functools import wraps
from flask import redirect, url_for
from wtforms import SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired, FileAllowed
import datetime
import random
import hashlib
from uuid import uuid4
import base64
import urllib.request
import os
from urllib.parse import unquote, urlparse
from login_module import *

"""公用的函数和装饰器"""
ALLOWED_EXTENSIONS = ('png', 'jpg', 'jpeg', 'gif', 'tif', 'pdf')  # 允许上传的图片后缀


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


def validate_admin_identity(user_name, user_password):
    """验证操作者身份"""
    if not user_name or not user_password:
        """去掉session中的内容"""
        keys = session.keys()
        [session.pop(x) for x in keys]
        return False
    else:
        message = admin_login(user_name, user_password)
        if message['message'] == 'success':
            """验证信息写入session"""
            session['user_name'] = user_name
            session['user_password'] = user_password
            session['user_sn'] = message['user_sn']
            return True
        else:
            """去掉session中的内容"""
            keys = list(session.keys())
            [session.pop(x) for x in keys]
            return False


def login_required_handler(f):
    """检测管操作员是否登录的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        handler_name = session.get("handler_name")  # 检测session中的account
        handler_password = session.get("handler_password")  # 检测session中的password
        if handler_name is None or handler_password is None:  # 会话检测失败
            return redirect(url_for("handler_login"))
        else:
            result = validate_admin_identity(handler_name, handler_password)
            if not result:
                return redirect(url_for("handler_login"))
        return f(*args, **kwargs)

    return decorated_function


def login_admin_require(f):
    """检测管操作员是否登录的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_name = session.get("user_name")  # 检测session中的account
        user_password = session.get("user_password")  # 检测session中的password
        if user_name is None or user_password is None:  # 会话检测失败
            return redirect(url_for("admin_login"))
        else:
            result = validate_admin_identity(user_name, user_password)
            if not result:
                return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return decorated_function


def get_arg(req, arg, default_value=''):
    """
    flask的request获取参数的简化方法，可以获取get和post的参数。共有三个参数
    1.req  当前的请求。一般都是传入当前上下文的request
    2.arg  参数名称
    3.default_value  未获取到参数时的默认值。默认情况下是空字符
    return 获取到的参数(字符串或默认值)
    """
    temp = req.args.get(arg)
    if temp is None:
        temp = default_value if req.form.get(arg) is None else req.form.get(arg)
    return temp


def get_args(req):
    """一次性取出所有取参数集，注意，参数的值不能是json对象"""
    the_form = req.form
    arg_dict = {key: the_form[key] for key in the_form.keys()}
    return arg_dict


def current_datetime(number=0):
    """获取当前的日期和时间，以字符串类型返回，格式为：2016-12-19 14:33:03
    number是指在当前日期上延后多少天，默认是0
    """
    now = datetime.datetime.now() + datetime.timedelta(days=number)
    return now.strftime("%Y-%m-%d %H:%M:%S")


def is_allow_email(email):
    """检查来宾的email是否被允许访问，并在许可的时间段,被允许的文件写在allow_email文件里"""
    file_path = os.path.join(os.path.split(__file__)[0], "allow_email")
    adict = dict()
    if os.path.exists(file_path):
        with open(file_path, mode="r", encoding="utf8") as f:
            for line in f:
                line = line.strip("\n")
                if line == "":
                    pass
                elif line.startswith("#"):
                    """注释掉的内容"""
                    pass
                else:
                    line_list = [x.strip(" ") for x in line.split(" ") if x.strip(" ") != ""]
                    line_dict = dict()
                    if line_list[0].endswith("@e-ai.com.cn"):
                        line_dict['email'] = line_list[0]
                        line_dict['name'] = line_list[1]
                    else:
                        line_dict = dict(zip(['email', 'name', 'begin', 'end'], line_list))
                    adict[line_list[0]] = line_dict
        """开始检查ip"""
        if email in adict.keys():
            temp = adict[email]
            try:
                begin = datetime.datetime.strptime(temp['begin'], "%Y-%m-%d|%H:%M")
                end = datetime.datetime.strptime(temp['end'], "%Y-%m-%d|%H:%M")
                now = datetime.datetime.now()
                """检查起止时间是否在允许范围内"""
                if begin <= now <= end:
                    return True
                else:
                    return False
            except KeyError as e:
                print(e)
                return True
        else:
            return False


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
    """
    try:
        ip = req.headers["X-Forwarded-For"].split(":")[0]
    except KeyError as e:
        ip = req.remote_addr  # 注意：tornado是 remote_ip
    if ip.find(",") != -1:
        """处理微信登录时转发的双ip"""
        ip = ip.split(",")[0]
    return ip


def rebuild_url(raw_url):
    """
    重新组装分页查询的url，主要是为了解决页码的问题，
    :param raw_url:
    :return: 三个值
    1.重建后的url，类似 http://...?xx&index= 的样式，最后只需要添加一个页码就好了。
    2.一个除了index页码之外的查询条件组成的字典，目的是为了提供给例如统计总数之类的方法的筛选条件。
    3.索引的值，如果索引信息为空，返回1.
    """
    url = unquote(raw_url)
    obj = urlparse(url)
    path = obj.path
    query = obj.query
    index = 1
    query_dict = dict()
    query_str_list = list()
    temp = ''
    if query != "":
        for x in query.split("&"):
            if x.startswith("index="):
                try:
                    index = int(x.split("=")[-1])
                except ValueError:
                    index = 1
            else:
                query_str_list.append(x)
                temp_list = x.split("=", 1)
                query_dict[temp_list[0]] = unquote(temp_list[1])
        temp = "&".join(query_str_list)
    new_url = "{}://{}?{}".format(obj.scheme, obj.path, "{}&index=".format(temp))
    return new_url, query_dict, index


"""定义的全局字段"""
kv_beijing = {'hospital_name': "医院名称", 'hospital_type': "医疗机构类型",
              'ticket_num': '单号', 'ticket_type': '发票类型', 'user_name': '姓名',
              'user_sex': "性别", 'user_type': '医保类型', 'user_num': '社会保障号码',
              'cost_class': '收费明细左', 'all_count': '合计', 'cash_count': '现金支付金额',
              'self_count': '个人账户支付金额', 'ybtc_count': '医保统筹支付金额',
              'fj_count': '附加支付金额', 'cash_flzf': '自负2', 'cash_zifu': '自付1',
              'cash_zifei': '自费', 'current_year_count': '当年账户余额',
              'all_year_count': '历年账户余额', 'cost_detail': '项目明细右',
              'prev_pay_count': '预存帐户支付', 'prev_pay_balance': '预存帐户余额',
              'ticket_date': '发票日期', 'zone': '地区', 'MZDEZF': "门诊大额支付", 'YBFWNFY': '本次医保范围内金额',
              'TXBCZF': '退休补充支付', 'YBFWNFYLJ': '累计医保内范围金额', 'CFDJE': '超封顶金额',
              'CJBZZF': '残军补助支付', 'NDMZDELJZF': '年度门诊大额累计支付', 'DWBCXZF': '单位补充险',
              'bczfhgz': '本次支付后个人账户余额', 'QFJE': '起付金额', 'XJZF': '个人支付金额', 'ZHZF': '个人账户支付',
              'JJZF': '基金支付'}

kv_shanghai = {'hospital_name': "医院名称", 'hospital_type': "医疗机构类型",
              'ticket_num': '单号', 'ticket_type': '发票类型', 'user_name': '姓名',
              'user_sex': "性别", 'user_type': '医保类型', 'user_num': '社会保障号码',
              'cost_class': '收费项目', 'all_count': '合计', 'cash_count': '现金支付金额',
              'self_count': '个人账户支付金额', 'ybtc_count': '医保统筹支付金额',
              'fj_count': '附加支付金额', 'cash_flzf': '现金支付-分类自负', 'cash_zifu': '现金支付-自负',
              'cash_zifei': '现金支付-自费', 'current_year_count': '当年账户余额',
              'all_year_count': '历年账户余额', 'cost_detail': '项目明细',
              'prev_pay_count': '预存帐户支付', 'prev_pay_balance': '预存帐户余额',
              'ticket_date': '发票日期', 'zone': '地区'}

