# -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import send_file
from flask import render_template
from flask import make_response
from flask import request
from flask import session
from flask_session import Session
from flask_wtf import Form
from flask import redirect
from mail_module import send_mail
import json
import datetime
import requests
import os
import json
from tools_module import *
from mail2_module import send_mail as send_mail2
import time


key_str = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
app.config['THREADED'] = True            # 多线程开启
SESSION_TYPE = "redis"
root_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(root_dir, 'templates')
hs = {"auth": AUTH}                           # 验证headers
Session(app)
port = 7005


@app.route("/favicon.ico")
def favicon_func():
    return send_file("static/img/favicon.ico")


@app.route("/")
def index_func():
    """首页重定向"""
    return redirect("/index.html")


@app.route("/fonts/<path>")
def re_fonts_func(path):
    """静态文件重定向"""
    return redirect("/static/fonts/{}".format(path))


@app.route("/css/<path>")
def re_css_func(path):
    """静态文件重定向"""
    return redirect("/static/css/{}".format(path))


@app.route("/js/<path>")
def re_js_func(path):
    """静态文件重定向"""
    return redirect("/static/js/{}".format(path))


@app.route("/img/<path>")
def re_img_func(path):
    """静态文件重定向"""
    return redirect("/static/img/{}".format(path))


@app.route("/sms/<action>", methods=['get', 'post'])
def sms_func(action):
    """短信视图"""
    mes = {"message": "success"}
    if action in ['get', 'send']:
        """发送短信"""
        form = Form()
        if form.validate_on_submit():
            phone = get_arg(request, "phone", "")
            if check_phone(phone):
                """手机号码合法"""
                u = "http://file.bhxxjs.cn/api/get_sms"
                args = {"phone": phone}
                r = None
                try:
                    r = requests.post(u, params=args, headers=hs, timeout=3)
                except Exception as e:
                    n = datetime.datetime.now()
                    t = "调用短信接口失败.{}".format(n)
                    c = "args:{}, auth:{}, error:{}".format(args, AUTH, e)
                    send_mail(title=t, content=c)
                    ms = "{} {}".format(t, c)
                    logger.exception(msg=ms)
                finally:
                    if r is None:
                        mes['message'] = "短信服务暂时不可用"
                    else:
                        status = r.status_code
                        if status != 200:
                            mes['message'] = "短信服务未工作"
                            n = datetime.datetime.now()
                            t = "调用短信接口返回了错误的状态.{}".format(n)
                            c = "args:{}, auth:{}, status:{}".format(args, AUTH, status)
                            send_mail(title=t, content=c)
                            ms = "{} {}".format(t, c)
                            logger.exception(msg=ms)
                        else:
                            mes = r.json()
                            title = "新用户注册 {}".format(datetime.datetime.now())
                            content = "手机号码: {}".format(phone)
                            send_mail2(title=title, content=content)
            else:
                """手机号码非法"""
                mes['message'] = '手机号码非法'
        else:
            mes['message'] = "提交错误,请刷新页面后重试"
    else:
        mes['message'] = '未知的操作'
    return json.dumps(mes)


@app.route("/register", methods=['get', 'post'])
def reg_func():
    """
    接收注册信息函数
    :return:
    """
    mes = {"message": "success"}
    form = Form()
    if form.validate_on_submit():
        args = get_args(request)
        args.pop('csrf_token', None)
        """检查短信验证码"""
        code = args.pop("code", "")
        """向后台提交注册信息"""
        r = None
        u = "http://192.168.1.102:8080/bhxx/register"
        u = "http://www.bhxxjs.cn:8080/bhxx/register"
        try:
            r = requests.post(u, params=args, headers=hs, timeout=3)
        except Exception as e:
            n = datetime.datetime.now()
            t = "调用注册接口失败.{}".format(n)
            c = "args:{}, auth:{}, error:{}".format(args, AUTH, e)
            send_mail(title=t, content=c)
            ms = "{} {}".format(t, c)
            logger.exception(msg=ms)
        finally:
            if r is None:
                mes['message'] = "注册服务暂时不可用"
            else:
                status = r.status_code
                if status != 200:
                    mes['message'] = "注册服务未工作"
                    n = datetime.datetime.now()
                    t = "调用注册服务接口返回了错误的状态.{}".format(n)
                    c = "args:{}, auth:{}, status:{}".format(args, AUTH, status)
                    send_mail(title=t, content=c)
                    ms = "{} {}".format(t, c)
                    logger.exception(msg=ms)
                else:
                    mes = r.json()
    else:
        mes['message'] = "提交错误,请刷新页面后重试"
    return json.dumps(mes)


@app.route("/login", methods=['get', 'post'])
def login_func():
    """
    接收登录信息函数
    :return:
    """
    mes = {"message": "success"}
    form = Form()
    if form.validate_on_submit():
        args = get_args(request)
        if 'phone' in args:
            args['login_name'] = args.pop("phone")
        args.pop('csrf_token', None)
        """向后台提交登录信息"""
        r = None
        u = "http://192.168.1.102:8080/bhxx/login"
        u = "http://www.bhxxjs.cn:8080/bhxx/login"
        try:
            r = requests.post(u, params=args, headers=hs, timeout=3)
        except Exception as e:
            n = datetime.datetime.now()
            t = "调用登录接口失败.{}".format(n)
            c = "args:{}, auth:{}, error:{}".format(args, AUTH, e)
            send_mail(title=t, content=c)
            ms = "{} {}".format(t, c)
            logger.exception(msg=ms)
        finally:
            if r is None:
                mes['message'] = "登录服务暂时不可用"
            else:
                status = r.status_code
                if status != 200:
                    mes['message'] = "登录服务未工作"
                    n = datetime.datetime.now()
                    t = "调用登录服务接口返回了错误的状态.{}".format(n)
                    c = "args:{}, auth:{}, status:{}".format(args, AUTH, status)
                    send_mail(title=t, content=c)
                    ms = "{} {}".format(t, c)
                    logger.exception(msg=ms)
                else:
                    mes = r.json()
    else:
        mes['message'] = "提交错误,请刷新页面后重试"
    return json.dumps(mes)


@app.route("/<the_path>")
def common_func(the_path):
    """通用页面视图函数"""
    path_list = os.listdir(template_dir)
    if the_path not in path_list:
        return abort(404)
    else:
        return render_template(the_path, form=Form())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)
