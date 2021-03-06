from flask import Flask
from flask import abort
from flask import send_from_directory
from flask import render_template
from flask import make_response
from flask import request
from flask import session
from flask_session import Session
from flask import redirect
import json
import datetime
import os
import json
from module.item_module import WXUser
from views.wx_view import wx_blueprint
import requests
from module.item_module import RawWebChatMessage
from module.item_module import WebChatMessage
from module.item_module import WXUser
from module.item_module import EventHandler
from tools_module import *
from mongo_db import cache
import xmltodict


key_str = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
app.register_blueprint(wx_blueprint)
SESSION_TYPE = "redis"
Session(app)
port = 8080
app_id = "wx50cbcc5725601880"
app_secret = "1aa28cda9bbb187acb9e1f7464d2b15a"


"""扩展jinja2过滤器"""


def str_time(val: datetime.datetime, fmt: str = None) -> str:
    """
    自定义的jinja2的格式化时间的方式.
    :param val:
    :param fmt:
    :return:
    """
    if isinstance(val, datetime.datetime):
        fmt = "%F" if fmt is None else fmt
        res = '' if val is None else val.strftime(fmt)
    else:
        res = val
    return res


def is_list(val) -> bool:
    """
    自定义的jinja2的过滤器, 判断一个对象是否是数组
    :param val:
    :return:
    """
    if isinstance(val, list):
        return True
    else:
        return False


def get_birth(birth: datetime.datetime) -> str:
    """
    根据出生年月计算年龄
    :param birth:
    :return:
    """
    if isinstance(birth, datetime.datetime):
        now = datetime.datetime.now().year
        y = birth.year
        m = birth.month
        return "{} 岁({}年{}月)".format(now - y, y, m)
    else:
        return ''


def transform_education(education: (str, int)) -> int:
    """
    转换学历,忽视旧的字符串格式的学历.None转为-1
    :param education:
    :return:
    """
    if isinstance(education, str):
        try:
            education = int(education)
        except Exception as e:
            education = -1
    elif isinstance(education, int):
        pass
    else:
        education = -1
    return education


app.jinja_env.filters['str_time'] = str_time
app.jinja_env.filters['is_list'] = is_list
app.jinja_env.filters['get_birth'] = get_birth
app.jinja_env.filters['transform_education'] = transform_education


"""辅助函数"""


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


"""视图函数开始"""


@app.route('/')
def hello_world():
    mes = {"message": "success"}
    data = get_all_args(req=request)
    mes['data'] = data
    return json.dumps(mes)


@app.route("/MP_verify_DsFnF8udEBEA4gAI.txt")
def wx_validate_file_func():
    """微信服务器回调域名验证"""
    return send_from_directory(directory="static/file/", filename="MP_verify_DsFnF8udEBEA4gAI.txt")


@app.route("/welcome")
def welcome_func():
    return render_template("welcome.html")


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
        """微信服务器推送的消息"""
        """
        微信服务器推送的消息的放在xml,同时args里面也有参数
        xml的内容取出后是一个有序字典:
        OrderedDict([('xml',
          OrderedDict([('ToUserName', 'gh_134657758ddf'),
                       ('FromUserName', 'oBBcR1T5r6FCqOo2WNxMqPUqvK_I'),
                       ('CreateTime', '1532479965'),
                       ('MsgType', 'event'),
                       ('Event', 'SCAN'),
                       ('EventKey', '123'),
                       ('Ticket',
                        'gQHB8DwAAAAAAAAAAS5odHRwOi8vd2VpeGluLnFxLmNvbS9xLzAybmhTSjBKNG5jaGwxMDAwMHcwM0wAAgQYwlZbAwQAAAAA')]))])

        """
        xml_data = request.data.decode(encoding="utf-8")
        if xml_data != "":
            xml = xmltodict.parse(xml_data)
            xml = xml['xml']
            print(xml)
            event = xml.get("Event")
            if event is None:
                msg_type = xml.get("event")
                if msg_type == "text":
                    """
                    这是用户在公众号发消息
                    """
                    content = xml.get("Content")
                    print("room mes is {}".format(content))
            else:
                client_id = xml.get("FromUserName")
                if event.lower() == "scan":
                    """扫码事件"""
                    event_key = xml.get("EventKey", "")
                    if event_key.startswith("relate_"):
                        sale_id = event_key.split("_")[-1]
                        print("client_id: {}, client_id: {}".format(client_id, sale_id))
                        WXUser.relate(open_id=client_id, s_id=sale_id)
                elif event.lower() == "subscribe":
                    """
                    订阅事件,用户未关注的时候的扫带参数二维码就会生成这个事件.
                    """
                elif event.lower() == "view":
                    """浏览页面事件"""
                else:
                    pass
        else:
            pass
        """对微信服务器推送的消息进行处理"""
        info = WebChatMessage.instance_from_request(request)
        resp = EventHandler.listen(info=info)
        if resp == b'':
            return "success"  # 规定的返回字符串
        else:
            print(resp)
            resp = make_response(resp)
            resp.headers["Content-Type"] = "text/xml; charset=utf-8"
            return resp
    else:
        return abort(405)


@app.route("/temp_message", methods=['post', 'get'])
def temp_message():
    mes = {"message": "success"}
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
    try:
        xml_data = request.data.decode(encoding="utf-8")
    except Exception as e:
        logger.exception(msg=e)
        xml_data = ''
    finally:
        pass
    ip = get_real_ip(request)
    now = datetime.datetime.now()
    data = {
        "ip": ip,
        "url": request.url,
        "method": request.method.lower(),
        "headers": headers,
        "args": args,
        "form": form,
        "json": json_data,
        "xml": xml_data,
        "time": now
    }
    mes = RawWebChatMessage(**data)
    mes.save_plus()
    one = WebChatMessage.doc_from_raw(mes.get_dict())
    WebChatMessage(**one).save_plus()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
