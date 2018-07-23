from flask import Flask
from flask import abort
from flask import send_from_directory
from flask import render_template
from views.user_views import user_blueprint
from flask import request
from flask import session
from flask_session import Session
from flask import redirect
import json
import datetime
import os
import json
import requests
from module.item_module import RawWebChatMessage
from module.item_module import WXUserInfo
from tools_module import *
from mongo_db import cache


key_str = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
SESSION_TYPE = "redis"
app.register_blueprint(user_blueprint)
Session(app)
port = 8080
app_id = "wx0caf19ad3fd15e71"                       # 盛汇app_id
app_secret = "f372a66d288958d5cc031637e8257543"     # 盛汇app_secret
app_id = "wx66711dbfd84a50c4"                       # 汇赢app_id
app_secret = "d9186b6cef15534427c02f6ee7085a9f"     # 汇赢app_secret


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


def get_user_info(access_token: str, open_id: str) -> dict:
    """
    根据用户id获取用户的信息
    :param access_token:
    :param open_id:
    :return:
    返回的字段说明:
    openid   	用户的唯一标识
    nickname	用户昵称
    sex	        用户的性别，值为1时是男性，值为2时是女性，值为0时是未知
    province	用户个人资料填写的省份
    city	    普通用户个人资料填写的城市
    country	    国家，如中国为CN
    headimgurl	用户头像，最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，0代表640*640正方形头像），
                用户没有头像时该项为空。若用户更换头像，原有头像URL将失效。
    privilege	用户特权信息，json 数组，如微信沃卡用户为（chinaunicom）
    unionid	    只有在用户将公众号绑定到微信开放平台帐号后，才会出现该字段。
    """
    res = {"message": "未知错误"}
    u = "https://api.weixin.qq.com/sns/userinfo?access_token={}&openid={}&lang=zh_CN". \
        format(access_token, open_id)
    resp = requests.get(u)
    status = resp.status_code
    if status != 200:
        res['message'] = "服务器返回了异常的状态码:{}".format(status)
    else:
        # data = resp.json()
        """json返回的内容,requests不好推断编码,所以使用了原始的返回体,自己解码"""
        content = resp.content
        data = json.loads(s=content.decode(), encoding="utf-8")
        print(data)
        res['message'] = "success"
        res['data'] = data
    return res


@app.route('/')
def hello_world():
    mes = {"message": "success"}
    data = get_all_args(req=request)
    mes['data'] = data
    return json.dumps(mes)


@app.route("/MP_verify_sMgcu97iNJMwM7WI.txt")
def wx_validate_file_func():
    """微信服务器回调域名验证"""
    return send_from_directory(directory="static/file/", filename="MP_verify_sMgcu97iNJMwM7WI.txt")


@app.route("/welcome")
def welcome_func():
    return render_template("welcome.html", app_id=app_id)


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


@app.route("/user_info_demo")
def user_info_demo_func():
    """
    一个获取用户信息的的示范页面.注意,不能直接访问此页面,而是需要从welcome页面进入
    :return:
    """
    """第一步,获取code"""
    code = get_all_args(req=request)['args']['code']
    """
    第二步, 获取access_token,
    data的值说明:
    access_token:	网页授权接口调用凭证,注意：此access_token与基础支持的access_token不同
    expires_in:   	access_token接口调用凭证超时时间，单位（秒）
    refresh_token:	用户刷新access_token
    openid:         用户唯一标识，请注意，在未关注公众号时，用户访问公众号的网页，也会产生一个用户和公众号唯一的OpenID
    scope:      	用户授权的作用域，使用逗号（,）分隔
    """
    error_reason = ""
    data = get_access_token(code_str=code)['data']
    access_token = ""  
    open_id = ""
    try:
        access_token = data['access_token']
        open_id = data['openid']
    except KeyError as e:
        error_reason = "code已过期或者使用过"
    finally:
        if error_reason != "":
            resp = {"message": error_reason}
        else:
            """第三步,获取用户信息"""
            resp = get_user_info(access_token=access_token, open_id=open_id)
        # return json.dumps(resp)
        data = resp.get("data", dict())
        user_info = WXUserInfo(**data)
        user_info.save_plus(upsert=True)
        return render_template("user_info_demo.html", data=data)


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
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
