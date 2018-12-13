from flask import Flask
from flask import abort
from flask import send_from_directory
from flask import render_template
from views.user_views import user_blueprint
from views.teacher_views import teacher_blueprint
from views.manage_view import manage_blueprint
from flask import request
from flask import session
from my_filter import mount_plugin
from flask_session import Session
from flask import make_response
from flask import redirect
import json
import datetime
import os
import json
import requests
import xmltodict
from celery_module import send_template_message
from module.item_module import RawWebChatMessage
from module.item_module import WebChatMessage
from module.item_module import WXUser
from module.item_module import EventHandler
from module.trade_module import Trade
from module.trade_module import process_case
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
app.register_blueprint(teacher_blueprint)
app.register_blueprint(manage_blueprint)
Session(app)
port = 8080
app_id = "wx0caf19ad3fd15e71"                       # 盛汇app_id
app_secret = "f372a66d288958d5cc031637e8257543"     # 盛汇app_secret
app_id = "wx66711dbfd84a50c4"                       # 汇赢app_id
app_secret = "d9186b6cef15534427c02f6ee7085a9f"     # 汇赢app_secret


"""注册jinja2自定义过滤器"""

mount_plugin(app)  # 注册jinja2的自定义过滤器


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


"""视图函数"""


@app.route('/')
def hello_world():
    mes = {"message": "success"}
    data = get_all_args(req=request)
    mes['data'] = data
    return json.dumps(mes)


@app.route("/<file_name>")
def validate_func(file_name):
    """申诉"""
    return send_from_directory(directory="static/file/", filename=file_name)


@app.route("/MP_verify_sMgcu97iNJMwM7WI.txt")
def wx_validate_file_func():
    """微信服务器回调域名验证"""
    return send_from_directory(directory="static/file/", filename="MP_verify_sMgcu97iNJMwM7WI.txt")


@app.route("/welcome")
def welcome_func():
    return render_template("welcome.html", app_id=app_id)


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
        """
        微信服务器推送的消息,为新服务器推送来的都是xml消息
        同时args里面也有参数
        xml的内容取出后是一个有序字典:
        OrderedDict([('xml',
          OrderedDict([('ToUserName', 'gh_134657758ddf'),
                       ('FromUserName', 'oBBcR1T5r6FCqOo2WNxMqPUqvK_I'),
                       ('CreateTime', '1532479965'),
                       ('MsgType', 'event'),
                       ('Event', 'SCAN'),
                       ('EventKey', '123'),
                       ('Ticket',
                        'gQHB8DwAAAAAAAAAAS5odHRwOi8vd2VpeGluLnFxLmNvbS9xLzAybmhTSjBKNG5jaGwxMDAwMHc
                        wM0wAAgQYwlZbAwQAAAAA')]))])
        
        """
        """对微信服务器推送的消息进行处理"""
        info = WebChatMessage.instance_from_request(request)
        resp = EventHandler.listen(info=info)
        if resp == b'':
            return "success"  # 规定的返回字符串
        else:
            resp = make_response(resp)
            resp.headers["Content-Type"] = "text/xml; charset=utf-8"
            print(resp)
            return resp
    else:
        return abort(405)


@app.route("/listen_<key>", methods=['post'])
def listen_func(key):
    """监听
    1. 虚拟喊单延迟信号
    发送过来的消息"""
    mes = {"message": "success"}
    if key == "virtual_trade":
        """虚拟喊单延迟信号"""
        trade = get_args(req=request)
        # print("原始trade: {}".format(trade))
        native = False
        if "native" in trade:
            native = True if trade['native'] == "True" else False
        trade['native'] = native
        trade = Trade(**trade)
        trade = trade.get_dict()
        res = process_case(trade, native) # 调试注销
        # res = "listen_func bypass, 不接受虚拟老师:{}信号.".format(trade['teacher_name'])   # 调试打开
        print(res)
    else:
        mes['message'] = '错误的path'
    return json.dumps(mes)


@app.route("/template_message", methods=['post', 'get'])
def template_message_func():
    """
    向微信用户发送模板消息.
    2018-9-3 弃用,使用内部函数替代.原有的Message_Server中的模块已合并到本模块
    :return:
    """
    mes = {"message": "success"}
    args = get_args(request)
    args = dict() if args is None else args
    signature = args.pop("signature", "")
    if signature != 'template_message':
        abort(404)
    else:
        mes_type = args.pop("mes_type", "")
        send_template_message.delay(mes_type=mes_type, mes_dict=args)
        print("template_message's return is {}".format(mes))
        return json.dumps(mes)


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
        "url": request.url,
        "headers": headers,
        "args": args,
        "form": form,
        "json": json_data,
        "xml": xml_data,
        "time": now
    }
    RawWebChatMessage.insert_one(doc=data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
