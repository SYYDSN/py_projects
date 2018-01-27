# -*- coding: utf-8 -*-
import os
import sys
from bson.objectid import ObjectId
from flask import Flask, request, abort, send_from_directory
from flask import render_template
from flask_session import Session
import json
from log_module import get_logger
import user_module
from uuid import uuid4
from flask_wtf.csrf import CSRFProtect
from mongo_db import cache
from tools_module import *


keystr = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
SESSION_TYPE = "redis"
app.config.from_object(__name__)
Session(app)
csrf = CSRFProtect(app)
port = 9090


logger = get_logger()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/login", methods=['post', 'get'])
def login_func():
    if request.method.lower() == "get":
        login_title = "登录"
        return render_template("login.html", login_title=login_title)
    elif request.method.lower() == "post":
        user_name = get_arg(request, "user_name", "")
        user_password = get_arg(request, "user_password", "")
        res = user_module.User.validate_identity_cls(user_name=user_name, user_password=user_password)
        if res['message'] == "success":
            """登录成功"""
            user_id = res['data']['_id']
            save_session(user_id=user_id, user_name=user_name, user_password=user_password)
            return json.dumps({"message": "success"})
    else:
        return abort(405)


@app.route("/upload_<key>", methods=['post', 'get'])
@check_session
def upload(key):
    """用户上传图片/文件"""
    user_id = session.get('user_id')
    if key.lower() == "image":
        """上传图片"""
        if request.method.lower() == "get":
            image_list = user_module.User.get_file_space(user_id)
            images = {image.split("/")[-1]: request.url_root.rstrip("/") + image for image in image_list}
            return render_template("upload_page.html", images=images)
        else:
            message = {"message": "success"}
            upload_files = request.files
            """sys._getframe().f_code.co_name 当前运行函数的名称"""
            ms = "{} 上传文件，key={},files={}".format(sys._getframe().f_code.co_name, key, upload_files)
            logger.info(ms)
            file = upload_files[key]
            # file_name = file.filename
            file_type = file.content_type
            file_type = file_type.split("/")[-1]
            file_name = "".join([uuid4().hex, ".", file_type])
            dir_path = user_module.User.get_upload_dir_path(key, user_id=user_id)
            try:
                file.save(os.path.join(dir_path, file_name))
            except Exception as e:
                logger.exception(e)
                message['message'] = "上传失败"
            finally:
                return json.dumps(message)
    else:
        return abort(405)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static/image"), 'favicon.ico',
                               mimetype="image/vnd.microsoft.icon")


@app.after_request
def allow_cross_domain(response):
    """跨域资源访问管理"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    allow_headers = "Referer,Accept,Origin,User-Agent"
    response.headers['Access-Control-Allow-Headers'] = allow_headers
    # 也可以在此设置cookie
    # resp.set_cookie('username', 'the username')
    return response


csrf.exempt(login_func)             # 此视图不做csrf保护
csrf.exempt(upload)             # 此视图不做csrf保护


if __name__ == '__main__':
    print(app.url_map)
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
