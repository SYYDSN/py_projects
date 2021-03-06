#  -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import render_template
from flask_session import Session
from user_module import User
from module.data.pickle_data import query_chart_data
from tools_module import *
from module.item_module import *
from views.mt4_view import mt4_blueprint
from views.quotations_view import quotations_blueprint
from views.normal_view import normal_blueprint
from module.jdy_module import listen_jdy
import os


secret_key = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
# app.config['SERVER_NAME'] = "127.0.0.1:8001"  此域名下的所有子域名的session都会接受
app.config.from_object(__name__)
app.register_blueprint(mt4_blueprint)  # 注册监听mt4后台发送过来的消息的蓝图
app.register_blueprint(quotations_blueprint)  # 注册监听报价行情推送的消息的蓝图
app.register_blueprint(normal_blueprint)  # 注册一般视图的蓝图
Session(app)


cache = RedisCache()
logger = get_logger()
port = 8000


def get_signature(nonce, payload, secret, timestamp):
    """生成简道云的签名验证"""
    content = ':'.join([nonce, payload, secret, timestamp]).encode('utf-8')
    m = hashlib.sha1()
    m.update(content)
    return m.hexdigest()


def validate_signature(req, secret, signature) -> bool:
    """验证简道云发来的消息的签名是否正确？"""
    payload = req.data.decode('utf-8')
    nonce = req.args.get('nonce', '')
    timestamp = req.args.get('timestamp', '')
    if signature != get_signature(nonce, payload, secret, timestamp):
        return False
    else:
        return True


@app.route('/', methods=['post', 'get'])
def hello_world():
    return 'Hello World!'


@app.route("/listen_<key>", methods=['post'])
def listen_func(key):
    """监听   新增的监听请使用 listen_func2
    1. 简道云
    2. 虚拟喊单延迟信号
    发送过来的消息"""
    mes = {"message": "success"}
    headers = request.headers
    event_id = headers.get("X-JDY-DeliverId")
    signature = headers.get("X-JDY-Signature")
    data = request.json
    data = data if isinstance(data, dict) else get_args(request)
    print(event_id)
    print(signature)
    print(data)
    raw = RawSignal(**data)
    raw.save_plus()  # 保存原始喊单数据格式
    if key == "test":
        """测试消息"""
        secret_str = "ckFqpdtIr45aXwPkSITuW2iY"  # 不同的消息定义的secret不同，用来验证消息的合法性
        print(validate_signature(request, secret_str, signature))
    elif key == "signal_test":
        """分析师发信号测试"""
        secret_str = 'P5lxNPYgF6cylkMBUenhkOE7'
        check = validate_signature(request, secret_str, signature)
        ms = "signal_test check secret is {}".format(check)
        logger.info(ms)
        print(ms)
        signal = Signal.instance(**data)
        signal.send()
    elif key == "virtual_teacher":
        """虚拟老师的增删改,这个操作是简道云发来的，将来不一定使用这种方式"""
        secret_str = 'xRJKhty0IxbP5uBKotyDOS7r'
        check = validate_signature(request, secret_str, signature)
        ms = "signal_test check secret is {}".format(check)
        logger.info(ms)
        print(ms)
        """虚拟老师管理方式暂时未定"""
        pass
    elif key == "virtual_trade":
        """虚拟喊单延迟信号"""
        trade = get_args(req=request)
        print("原始trade: {}".format(trade))
        native = False
        if "native" in trade:
            native = True if trade['native'] == "True" else False
        trade['native'] = native
        trade = Trade(**trade)
        trade = trade.get_dict()
        # res = delay_virtual_trade(trade)
        res = process_case(trade, native)
        print(res)
    else:
        mes['message'] = '错误的path'
    return json.dumps(mes)


@app.route("/listen2_<key>", methods=['post'])
def listen_func2(key):
    """
    http://47.106.68.161:8000/listen_<key>
    监听简道云发送过来的消息,2018-10-8之后新建的简道云应用都用此接口.
    每次更新服务器应用后,需要检查简道云对应的接口状态
    1. 企划部.入金宣传表
    """
    mes = {"message": "success"}
    headers = request.headers
    event_id = headers.get("X-JDY-DeliverId")
    signature = headers.get("X-JDY-Signature")
    data = request.json
    data = data if isinstance(data, dict) else get_args(request)
    print(event_id)
    print(signature)
    print(data)
    raw = RawSignal(**data)
    raw.save_plus()  # 保存原始喊单数据格式
    if key in ["deposit", "material"]:
        """
        deposit:       企划部.入金宣传表
        material:      上传图片素材
        """
        secret_str = "tYfHgynb10QJkoPTPFoEJaI8"  # 消息定义的secret
        validate_result = validate_signature(request, secret_str, signature)
        print("deposit request validate result is {}".format(validate_result))
        if validate_result:
            kw = data['data']
            kw['req_type'] = key
            mes = listen_jdy(**kw)
        else:
            mes['message'] = "validate error"
    else:
        mes['message'] = '错误的path'
    # print(mes)
    return json.dumps(mes)


@app.route("/teacher_charts/<key>", methods=['get', 'post'])
@check_platform_session
def teacher_charts_func(key):
    """
    查看老师喊单成功率的页面
    key: 用于区分图标分组的标准.比如是以老师未分组依据还是以产品为分组依据?
    """
    begin = get_arg(request, "begin", None)
    end = get_arg(request, "end", None)
    if request.method.lower() == "get":
        url_args = {"begin": begin, "end": end}
        url_args = {k: v for k, v in url_args.items() if v is not None}
        url_path = ""
        for k, v in url_args.items():
            if url_path.find("?") == -1:
                url_path += "?"
            else:
                url_path += "&"
            url_path += "{}={}".format(k, v)
        return render_template("teacher_charts.html", key=key, url_args=url_args, url_path=url_path)
    elif request.method.lower() == "post":
        """查询老师的喊单数据"""
        data = query_chart_data(chart_type=key, begin=begin, end=end)
        mes = {"message": "success", "data": data}
        return json.dumps(mes)
    else:
        return abort(405)


@app.route("/teacher_login", methods=['post', 'get'])
def teacher_login_func():
    """管理登录页，登录后可查看老师喊单的有关统计图表"""
    if request.method.lower() == "get":
        login_title = "Login"
        return render_template("teacher_login.html", login_title=login_title)
    elif request.method.lower() == "post":
        user_name = get_arg(request, "user_name")
        user_password = get_arg(request, "user_password")
        """teacher_admin/2018@0429"""
        mes = {"message": "success"}
        if User.login(user_name, user_password):
            """登录成功"""
            save_platform_session(user_name=user_name, user_password=user_password)
        else:
            mes['message'] = "用户名或密码错误"
            clear_platform_session()
        return json.dumps(mes)
    else:
        return abort(405)


@app.before_request
def logger_request_info():
    """
    监控所有的请求信息
    :return:
    """
    data = None
    try:
        data = RawRequestInfo.get_init_dict(req=request)
        mes = RawRequestInfo(**data)
        mes.save_plus()
    except Exception as e:
        ms = "Error: {}, data: {}".format(e, data)
        logger.exception(msg=ms)
        send_mail(title="{}Message_Server监听请求出错".format(datetime.datetime.now()), content=ms)
    finally:
        if request.url.startswith("http://www.baidu.com"):
            return abort(404)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
