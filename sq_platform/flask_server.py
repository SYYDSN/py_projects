# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, send_from_directory
from flask import session
from flask_session import Session
from flask import redirect
from api.user.user_view import api_user_blueprint
from api.data.data_view import api_data_blueprint
from manage.manage_module import manage_blueprint
import manage.manage_module as m_module
from flask_wtf.csrf import CSRFProtect
from flask_debugtoolbar import DebugToolbarExtension
import json
import os
from mongo_db import cache


keystr = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = keystr  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
# app.config['SERVER_NAME'] = "127.0.0.1:8001"  此域名下的所有子域名的session都会接受
app.register_blueprint(api_user_blueprint)
app.register_blueprint(api_data_blueprint)
app.register_blueprint(manage_blueprint)
SESSION_TYPE = "redis"
app.config.from_object(__name__)
Session(app)
# csrf = CSRFProtect(app)                                       # 开启全局CSRF保护
# csrf.exempt(api_user_blueprint)                               # 此蓝图不做csrf保护


port = 5000


@app.route('/', methods=['get'])
def index_func():
    return redirect("/manage/")


@app.route("/hello", methods=['get', 'post'])
def hello_world_2():
    return "ok"


@app.route("/token", methods=['post', 'get'])
def test_token():
    token = request.headers.get("auth-token")
    result = {"token": token}
    return json.dumps(result)


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static/image"), 'favicon.ico',
                               mimetype="image/vnd.microsoft.icon")


@app.before_request
def show_request_before():
    # print(request)
    pass


@app.after_request
def allow_cross_domain(response):
    """允许跨域资源访问管理"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    allow_headers = "Referer,Accept,Origin,User-Agent"
    response.headers['Access-Control-Allow-Headers'] = allow_headers
    # 也可以在此设置cookie
    # resp.set_cookie('username', 'the username')
    return response


if __name__ == '__main__':
    # print(app.url_map)  # 打印视图路由
    cache.set("flask_server_port", port)
    # app.debug = True  # 这一行必须在toolbar = DebugToolbarExtension(app)前面,否则不生效
    toolbar = DebugToolbarExtension(app)  # 开启html调试toolbar
    # app.run(host="0.0.0.0", port=port, threaded=True)  # 开启DebugToolbar的调试模式. 对应app.debug = True
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)  # 一般调试模式
