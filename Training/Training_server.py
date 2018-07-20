# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import send_from_directory
from flask import session
from flask_session import Session
from flask import abort
import os
import requests
import datetime
from tools_module import *
from modules.item_module import RawWebChatMessage
from views.flash_view import flash_blueprint


"""训练服务器"""


port = 5678
key_str = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
SESSION_TYPE = "redis"
app.config.from_object(__name__)
app.register_blueprint(flash_blueprint)  # 注册闪卡训练蓝图
Session(app)
app_id = "wxd89f1f72776053ad"                       # app_id
app_secret = "66a4200979bf09dd565180f1bd9c38d4"     # app_secret


"""工具函数"""


def get_all_args(req) -> dict:
    """
    获取一次请求的所有参数.
    :param req:
    :return:
    """
    args = {k: v for k, v in request.args.items()}
    form = {k: v for k, v in request.form.items()}
    json_data = req.json
    jsons = dict() if json_data is None else {k: v for k, v in json_data.items()}
    data = {"args": args, 'form': form, "json": jsons}
    return data


def get_code(req) -> dict:
    """
    从微信服务器获取code和state的方法.
    code作为换取access_token的票据，每次用户授权带上的code将不一样，code只能使用一次，5分钟未被使用自动过期。
    :param req:
    :return:
    """
    code = get_arg(req, "code", "")
    state = get_arg(req, "state", "")
    t = datetime.datetime.now()
    res = {"time": t, "code": code, "state": state}
    return res


def refresh_access_token(refresh_token: str) -> dict:
    """
    当access_token过期时,调用此方法刷新access_token
    :param refresh_token: 用于刷新的凭证
    :return:
    返回的例子:
    {
    "access_token":"ACCESS_TOKEN",
    "expires_in":7200,
    "refresh_token":"REFRESH_TOKEN",
    "openid":"OPENID",
    "scope":"SCOPE"
    }
    返回的字段说明:
    access_token	网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
    expires_in	access_token接口调用凭证超时时间，单位（秒）
    refresh_token	用户刷新access_token
    openid	用户唯一标识
    scope	用户授权的作用域，使用逗号（,）分隔
    """
    res = {"message": "未知错误"}
    u = "https://api.weixin.qq.com/sns/oauth2/refresh_token?appid={}&grant_type=refresh_token&refresh_token={}".\
        format(app_id, refresh_token)
    resp = requests.get(u)
    status = resp.status_code
    if status != 200:
        res['message'] = "服务器返回了异常的状态码:{}".format(status)
    else:
        data = resp.json()
        res['message'] = "success"
        res['data'] = data
    return json.dumps(res)


def get_access_token(code_str: str) -> dict:
    """
    获取微信服务器的页面授权access_token
    :param code_str:
    :return:
    返回的值说明:
    access_token:	网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
    expires_in:   	access_token接口调用凭证超时时间，单位（秒）
    refresh_token:	用户刷新access_token
    openid:         用户唯一标识，请注意，在未关注公众号时，用户访问公众号的网页，也会产生一个用户和公众号唯一的OpenID
    scope:      	用户授权的作用域，使用逗号（,）分隔
    """
    res = {"message": "未知错误"}
    u = "https://api.weixin.qq.com/sns/oauth2/access_token?appid={}&secret={}&code={}&grant_type=authorization_code".\
        format(app_id, app_secret, code_str)
    resp = requests.get(u)
    status = resp.status_code
    if status != 200:
        res['message'] = "服务器返回了异常的状态码:{}".format(status)
    else:
        data = resp.json()
        res['message'] = "success"
        res['data'] = data
    return res


def validate_token(timestamp: str, nonce: str, signature: str) -> bool:
    """
    验证微信服务器的的配置

    1. 将token、timestamp、nonce三个参数进行字典序排序
    2. 将三个参数字符串拼接成一个字符串进行sha1加密
    3. 开发者获得加密后的字符串可与signature对比

    若确认此次GET请求来自微信服务器，请原样返回echostr参数内容，
    则接入生效，成为开发者成功，否则接入失败.
    :param timestamp:时间戳
    :param nonce: 随机数
    :param signature:微信加密签名
    :return: bool
    """
    res = False
    token = "0cceb6c6157747dcab9791569418799a"
    if isinstance(timestamp, str) and isinstance(nonce, str) and isinstance(signature, str):
        l = [token, timestamp, nonce]
        l.sort()
        s = "".join(l)
        sha = hashlib.sha1(s.encode(encoding="utf-8"))
        sha = sha.hexdigest()
        if sha == signature:
            res = True
        else:
            pass
    else:
        pass
    return res


"""开始视图函数"""


@app.route('/')
def hello_world():
    return 'Hello Baby!'


@app.route("/MP_verify_Y2yMSCJbTbMwSml6.txt")
def wx_validate_file_func():
    """
    微信服务器回调域名验证
    验证JS接口安全域名时使用.
    微信公众平台->设置->公众号设置->功能设置->JS接口安全域名(点击设置按钮)
    """
    return send_from_directory(directory="static/file/", filename="MP_verify_Y2yMSCJbTbMwSml6.txt")


@app.route("/message", methods=['post', 'get'])
def message_func():
    """接收微信发来的消息"""
    if request.method.lower() == "get":
        """验证微信服务器的配置"""
        signature = get_arg(request, "signature")
        t_stamp = get_arg(request, "timestamp")
        nonce = get_arg(request, "nonce")
        echostr = get_arg(request, "echostr")
        if validate_token(timestamp=t_stamp, nonce=nonce, signature=signature):
            return echostr
        else:
            return abort(403)
    elif request.method.lower() == "post":
        mes = {"message": "success"}
        return json.dumps(mes)
    else:
        return abort(405)


@app.before_request
def logger_request_info():
    """
    监控所有的请求信息
    :return:
    """
    headers = {k: v for k, v in request.headers.items()}
    args = {k: v for k, v in request.args.items()}
    form = {k: v for k, v in request.form.items()}
    json_data = None if request.json is None else {k: v for k, v in request.headers.items()}
    xml_data = request.data.decode(encoding="utf-8")
    ip = get_real_ip(request)
    now = datetime.datetime.now()
    data = {
        "ip": ip,
        "headers": headers,
        "args": args,
        "form": form,
        "json": json_data,
        "xml": xml_data,
        "time": now
    }
    mes = RawWebChatMessage(**data)
    mes.save_plus()


if __name__ == '__main__':
    if __name__ == '__main__':
        app.run(host="0.0.0.0", port=port, debug=True, threaded=True)  # 一般调试模式
