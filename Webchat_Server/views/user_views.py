#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import render_template
from flask import send_file
from flask import make_response
from flask import abort
from tools_module import *
from mongo_db import BaseFile
from io import BytesIO
import json
from module.server_api import app_id
from module.server_api import host_name
from module.server_api import PageAuthorization


"""注册蓝图"""
user_blueprint = Blueprint("user_blueprint", __name__, url_prefix="/user", template_folder="templates/")


"""用户信息的视图函数"""


def hello() -> str:
    """hello world"""
    return "hello user <a href='/user/auth/info'>去授权</a>"


def auth_func(key: str = None) -> str:
    """
    用户授权页面，仅仅为了获取用户信息
    :param key: 参数，默认是base/snsapi_base,也可以是info/snsapi_userinfo
    :return:
    """
    if key is None or key == "" or key == "base":
        key = "snsapi_base"
    else:
        key = "snsapi_userinfo"  # 授权类型
    url = request.referrer
    url = request.args.get("url", "{}/hello".format(host_name)) if url is None or url == "" else url
    redirect_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}" \
                       "&response_type=code&scope={}&state=STATE#wechat_redirect".format(app_id, url, key)
    return redirect(redirect_url)


def page_auth_demo():
    """
    页面授权示范页
    :return:
    """
    code = request.args.get("code", "")
    if code == "":
        data = dict()
    else:
        data = PageAuthorization.get_user_info(code=code)
    return render_template("page_auth_demo.html", data=data)


"""集中注册函数"""


"""hello"""
user_blueprint.add_url_rule(rule="/hello", view_func=hello, methods=['get', 'post'])
"""获取用户授权页面"""
user_blueprint.add_url_rule(rule="/auth/<key>", view_func=auth_func, methods=['post', 'get'])
"""页面授权示范页"""
user_blueprint.add_url_rule(rule="/page_auth_demo", view_func=page_auth_demo, methods=['post', 'get'])
