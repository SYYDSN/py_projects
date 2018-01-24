# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, send_from_directory
from flask import session
from flask_session import Session
from api.user.user_view import api_user_blueprint
from api.data.data_view import api_data_blueprint
from manage.manage_module import manage_blueprint
import manage.manage_module as m_module
from flask_wtf.csrf import CSRFProtect
import os
from mongo_db import cache


keystr = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = keystr  # 配置会话密钥
app.register_blueprint(api_user_blueprint)
app.register_blueprint(api_data_blueprint)
app.register_blueprint(manage_blueprint)
SESSION_TYPE = "redis"
app.config.from_object(__name__)
Session(app)
csrf = CSRFProtect(app)                                       # 开启全局CSRF保护
csrf.exempt(api_user_blueprint)                               # 此蓝图不做csrf保护
csrf.exempt(api_data_blueprint)                               # 此蓝图不做csrf保护
csrf.exempt(m_module.track_info)                              # 此视图不做csrf保护
csrf.exempt(m_module.login_func)                              # 此视图不做csrf保护
csrf.exempt(m_module.register_func)                           # 此视图不做csrf保护
csrf.exempt(m_module.track_info)                              # 此视图不做csrf保护
csrf.exempt(m_module.index_func)                              # 此视图不做csrf保护
csrf.exempt(m_module.get_driver_list_func)                    # 此视图不做csrf保护
csrf.exempt(m_module.get_employee_archives_func)              # 此视图不做csrf保护
csrf.exempt(m_module.driver_detail_func)                      # 此视图不做csrf保护
csrf.exempt(m_module.report_page_func)                        # 此视图不做csrf保护
csrf.exempt(m_module.app_version_table_func)                  # 此视图不做csrf保护
csrf.exempt(m_module.block_employee_list_func)                # 此视图不做csrf保护
csrf.exempt(m_module.user_info_func)                          # 此视图不做csrf保护
csrf.exempt(m_module.last_positions_func)                     # 此视图不做csrf保护
csrf.exempt(m_module.subordinates_base_info_func)             # 此视图不做csrf保护
port = 5000


@app.route('/index', methods=['get', 'post'])
def hello_world():
    if request.method.lower() == "get":
        return "{} pid:{}".format(request.method, os.getppid())
    else:
        return "{} pid:{}".format(request.method, os.getppid())


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static/image"), 'favicon.ico',
                               mimetype="image/vnd.microsoft.icon")


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
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
    # app.run(host="0.0.0.0", port=port, debug=True, threaded=True, ssl_context="adhoc")
