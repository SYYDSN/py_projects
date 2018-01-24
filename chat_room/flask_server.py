# -*- encoding: utf-8 -*-
__author__ = 'Administrator'
from flask import Flask, request
import json
import os
import chat_room_manage
import db_tools
import time
import ext_tools
import win_info

app = Flask(__name__)
port = 9014
keystr = os.urandom(24)  # 生成密钥，为session服务。

# 配置会话密钥
app.config['SECRET_KEY'] = keystr


# 存储，删除，读取聊天室会话
@app.route("/talks/<input>", methods=["post", "get"])
def talks(input):
    messages = json.loads(request.form.get("messages", "{}"))
    result = db_tools.talks(the_type=input, messages=messages)
    result = {"message": "success"} if result is None else result
    return json.dumps(result)


# 检查后台管理员登录的账户密码
@app.route("/check_admin_login", methods=["post", "get"])
def check_admin_login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    print(request.args)
    print(request.form)
    step = int(request.form.get("step", 0))
    print("step is {0}".format(step))
    time.sleep(step)
    print("username is " + username)
    print("password is " + password)
    result = chat_room_manage.check_login(username, password)
    return json.dumps(result)


# 查询老师列表，管理老师用
@app.route("/query_teacher_admin", methods=["post", "get"])
def query_teacher_admin():
    username = request.form.get("username")
    password = request.form.get("password")
    result = chat_room_manage.query_teacher_admin(username, password)
    return json.dumps(result)


# 编辑老师资料
@app.route("/edit_teacher_user", methods=["post", "get"])
def edit_teacher_user():
    input = request.form.get("input")
    objname = request.form.get("objname")
    password = request.form.get("password")
    return json.dumps(chat_room_manage.edit_teacher_user(input, objname, password))


# 编辑聊天室用户资料
@app.route("/edit_chatroom_user", methods=["post", "get"])
def edit_chatroom_user():
    input = request.form.get("input")
    my_args = request.form.get("args", "{}")
    my_args = json.loads(my_args.replace("'", '"'))  # 替换单引号为双引号
    result = chat_room_manage.edit_chatroom_user(input, my_args)
    return json.dumps(result)


# 对营销直播室老师风采的各种操作。
@app.route("/teachers", methods=["post", "get"])
def teachers():
    data = json.loads(request.form.get("data").replace("'", '"'))  # 替换单引号为双引号
    # print(data)
    result = chat_room_manage.teachers(**data)
    return json.dumps(result)


# 读取/保存课程表
@app.route("/edit_class", methods=["post", "get"])
def edit_class():
    the_type = request.form.get("the_type")
    print("edit_class")
    print(request.form.get("class_data", ""))
    class_data = "" if request.form.get("class_data") == "" else json.loads(
        request.form.get("class_data").replace("'", '"'))  # 替换单引号为双引号
    result = chat_room_manage.edit_class(the_type=the_type, class_data=class_data)
    return json.dumps(result)


# 客户登录聊天室页面的请求
@app.route("/chartroom_user_login", methods=["post", "get"])
def chartroom_user_login():
    user_name = request.form.get("user_name", "")
    user_password = request.form.get("user_password", "")
    ip = request.form.get("ip", "")
    result = {"message": "执行错误"}
    try:
        result = chat_room_manage.chartroom_user_login(user_name, user_password, ip)
    except Exception as e:
        print(e)
        my_logger = db_tools.get_logger_everyday("flask_server")
        my_logger.error("error in here", exc_info=True, stack_info=True)
    finally:
        return json.dumps(result)


# 聊天室客户修改个人资料
@app.route("/edit_user_info", methods=["post", "get"])
def edit_user_info():
    user_id = request.form.get("user_id", "")
    real_name = request.form.get("real_name", "")
    nick_name = request.form.get("nick_name", "")
    new_password = request.form.get("new_password", "")
    result = chat_room_manage.edit_user_info(user_id, real_name, nick_name, new_password)
    return json.dumps(result)


# 聊天室客户修改绑定的手机号码
@app.route("/change_user_phone", methods=["post", "get"])
def change_user_phone():
    user_id = request.form.get("user_id", "")
    phone = request.form.get("phone", "")
    result = chat_room_manage.change_user_phone(user_id, phone)
    return json.dumps(result)


# 获取用户级别和图标路径的字典
@app.route("/level_and_prefix", methods=["post", "get"])
def level_and_prefix():
    result = chat_room_manage.level_and_prefix()
    return json.dumps(result)


# 提供匿名id和记录匿名用户的操作
@app.route("/guest_message", methods=["post", "get"])
def guest_message():
    id = request.form.get("id", "")
    event_type = request.form.get("event_type", "")
    referer = request.form.get("referer", "")
    page_url = request.form.get("page_url", "")
    ip = request.form.get("ip", "")
    result = ext_tools.guest_message(id, event_type, referer, page_url, ip)
    return json.dumps(result)


# 查询虚拟客户跟单 收益
@app.route("/create_info", methods=["post", "get"])
def create_info():
    result = win_info.create_info()
    return json.dumps(result)


# 用户注册
@app.route("/user_reg", methods=["post", "get"])
def user_reg():
    user_name = request.form.get("user_name", "")
    user_password = request.form.get("user_password", "")
    user_phone = request.form.get("user_phone", "")
    nick_name = request.form.get("nick_name", "")
    ip = request.form.get("ip", "")
    result = {"message": "执行错误"}
    try:
        result = chat_room_manage.user_reg(user_name=user_name, user_password=user_password, user_phone=user_phone,
                                       nick_name=nick_name, ip=ip)
    except Exception as e:
        print(e)
        my_logger = db_tools.get_logger_everyday("flask_server")
        my_logger.error("error in here", exc_info=True, stack_info=True)
    finally:
        return json.dumps(result)


# 用户在聊天室注册用户时，当用户名失焦的时候，检测用户名是否重复的方法
@app.route("/check_user_repeat", methods=["post", "get"])
def check_user_repeat():
    user_name = request.form.get("user_name", "")
    result = chat_room_manage.check_user_repeat(user_name)
    return json.dumps(result)


# 对每日策略的操作
@app.route("/tips", methods=["post", "get"])
def tips():
    the_type = request.args.get("the_type", "") if request.form.get("the_type", "") == "" else  request.form.get(
        "the_type", "")
    args_dict = {} if request.form.get("args_dict") is None else json.loads(
        request.form.get("args_dict").replace("'", '"'))  # 替换单引号为双引号
    result = chat_room_manage.tips(the_type, args_dict)
    return json.dumps(result)


####################################################
# 注册一个钩子，用于让服务器支持cors（跨域请求）
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,User-Agent')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


# 注册一个钩子，用于在每次请求前运行一个函数。
@app.before_request
def before_request():
    pass


##########################################################
if __name__ == '__main__':
    logger = ext_tools.get_logger_everyday("flask")
    logger.info("begin....")
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
