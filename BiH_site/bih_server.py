# -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import send_file
from flask import render_template
from flask import make_response
from flask import request
from flask import session
from flask_session import Session
from flask_wtf import FlaskForm
from flask import redirect
from mail_module import send_mail
import json
import datetime
import requests
import os
import json
from tools_module import *
from mail2_module import send_mail as send_mail2
from module.user_module import UserInfo
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
    """首页"""
    form = FlaskForm()
    _id = session.get("_id", None)
    if isinstance(_id, ObjectId):
        user = UserInfo.find_by_id(o_id=_id, to_dict=True)
    else:
        user = None
    return render_template("index.html", form=form, user=user)


@app.route("/bhxxjs_web/<file_name>")
def wap_func(file_name):
    """移动端首页"""
    _id = session.get("_id", None)
    if isinstance(_id, ObjectId):
        user = UserInfo.find_by_id(o_id=_id, to_dict=True)
    else:
        user = None
    return render_template("bhxxjs_web/{}".format(file_name), form=FlaskForm(), user=user)


@app.route("/fonts/<path>")
def re_fonts_func(path):
    """静态文件重定向"""
    return redirect("/static/fonts/{}".format(path))


@app.route("/bhxxjs_web/fonts/<path>")
def re_wap_fonts_func(path):
    """移动端静态文件重定向"""
    return redirect("/static/wap/fonts/{}".format(path))


@app.route("/css/<path>")
def re_css_func(path):
    """静态文件重定向"""
    return redirect("/static/css/{}".format(path))


@app.route("/bhxxjs_web/css/<path>")
def re_wap_css_func(path):
    """移动端静态文件重定向"""
    return redirect("/static/wap/css/{}".format(path))


@app.route("/js/<path>")
def re_js_func(path):
    """静态文件重定向"""
    return redirect("/static/js/{}".format(path))


@app.route("/bhxxjs_web/js/<path>")
def re_wap_js_func(path):
    """移动端静态文件重定向"""
    return redirect("/static/wap/js/{}".format(path))


@app.route("/img/<path>")
def re_img_func(path):
    """静态文件重定向"""
    return redirect("/static/img/{}".format(path))


@app.route("/bhxxjs_web/img/<path>")
def re_wap_img_func(path):
    """移动端静态文件重定向"""
    return redirect("/static/wap/img/{}".format(path))


@app.route("/sms/<action>", methods=['get', 'post'])
def sms_func(action):
    """短信视图"""
    mes = {"message": "success"}
    if action in ['get', 'send']:
        """发送短信"""
        form = FlaskForm()
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
    form = FlaskForm()
    if form.validate_on_submit():
        args = get_args(request)
        args.pop('csrf_token', None)
        """检查短信验证码"""
        phone = args.pop("phone", "")
        code = args.pop("code", "")
        password = args.pop("password", "")
        if phone == '' or password == '' or code == '':
            mes['message'] = "缺少必要的信息"
        else:
            """检查短信验证码"""
            f = {"phone": phone, 'code': code}
            u = "http://file.bhxxjs.cn/api/validate_code"
            # u = "http://127.0.0.1:7001/api/validate_code"
            r = None
            try:
                r = requests.get(u, params=f, headers=hs)
            except Exception as e:
                n = datetime.datetime.now()
                t = "短信验证接口调用失败.{}".format(n)
                c = "args:{}, auth:{}, error:{}".format(f, AUTH, e)
                send_mail(title=t, content=c)
                ms = "{} {}".format(t, c)
                logger.exception(msg=ms)
            finally:
                status = r.status_code if hasattr(r, 'status_code') else None
                if status != 200:
                    mes['message'] = "验证短信服务未工作"
                    n = datetime.datetime.now()
                    t = "调用验证短信服务接口返回了错误的状态.{}".format(n)
                    c = "args:{}, auth:{}, status:{}".format(args, AUTH, status)
                    send_mail(title=t, content=c)
                    ms = "{} {}".format(t, c)
                    logger.exception(msg=ms)
                else:
                    r = r.json()
                    if r['message'] != "success":
                        mes['message'] = "短信验证失败"
                    else:
                        """验证成功.向后台提交注册信息"""
                        args = {"loginname": phone, "password": password}
                        r = None
                        u = "http://www.bhxxjs.cn:8080/bdurs/user/toAddUser"
                        # u = "http://192.168.1.107:8080/BDUrs/user/toAddUser"
                        try:
                            r = requests.get(u, params=args, headers=hs, timeout=3)
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
                                    """保存到mongodb"""
                                    args = {"phone": phone, "password": password}
                                    mes = UserInfo.register(**args)
    else:
        mes['message'] = "提交错误,请刷新页面后重试"
    return json.dumps(mes)


@app.route("/logout")
def logout_func():
    """注销"""
    session.pop("_id", None)
    return redirect(url_for("index_func"))


@app.route("/login", methods=['get', 'post'])
def login_func():
    """
    接收登录信息函数
    :return:
    """
    mes = {"message": "success"}
    form = FlaskForm()
    if form.validate_on_submit():
        args = get_args(request)
        args.pop('csrf_token', None)
        try:
            mes = UserInfo.login(**args)
        except Exception as e:
            n = datetime.datetime.now()
            t = "官网登录失败.{}".format(n)
            c = "args:{}, auth:{}, error:{}".format(args, AUTH, e)
            send_mail(title=t, content=c)
            ms = "{} {}".format(t, c)
            logger.exception(msg=ms)
        finally:
            if mes['message'] == "success":
                """登录成功"""
                session['_id'] = mes.pop('_id')  # 保存会话
            else:
                pass
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
        _id = session.get("_id", None)
        if isinstance(_id, ObjectId):
            user = UserInfo.find_by_id(o_id=_id, to_dict=True)
        else:
            user = None
        return render_template(the_path, form=FlaskForm(), user=user)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)
