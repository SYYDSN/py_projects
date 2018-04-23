#  -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import make_response
from flask import render_template
from flask import render_template_string
from flask import send_file
from flask import request
from mongo_db import get_datetime_from_str
from flask_session import Session
from log_module import get_logger
import sms_module
from mongo_db import get_obj_id
from flask_tokenauth import TokenAuth, TokenManager
import json
from werkzeug.contrib.cache import RedisCache
from flask_debugtoolbar import DebugToolbarExtension
from tools_module import *
import item_module
from module.spread_module import AllowOrigin
from uuid import uuid4
from module import user_module
import os
from mail_module import send_mail
from browser.crawler_module import CustomerManagerRelation
from pdb import set_trace


secret_key = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
SESSION_TYPE = "redis"
app.config.from_object(__name__)
Session(app)

"""作为Draw_Server项目,JDY_server.py为历史问题,暂未有任何作用."""
cache = RedisCache()
logger = get_logger()
port = 9000


class MyTokenAuth(TokenAuth):
    """自定义验证类"""
    def token_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.method.lower() == 'post':
                token = request.headers.get('X-Auth-Token')
                if not token:
                    return self.auth_error_callback()
                if not self.authenticate(token):
                    return self.auth_error_callback()
            return f(*args, **kwargs)
        return decorated


token_auth = MyTokenAuth(secret_key=secret_key)
token_manager = TokenManager(secret_key=secret_key)


def get_token() -> str:
    """生成防csrf的token"""
    uuid_str = uuid4().hex
    token = token_manager.generate(name=uuid_str).decode()
    cache.set(token, uuid_str, 3600)
    return token


@token_auth.verify_token
def verify_token(token):
    """csrf的token验证器"""
    if request.method.lower() == 'post':
        str1 = token_manager.verify(token)
        str2 = cache.get(token)
        if str2 is not None and str1 == str2:
            return True
        else:
            return False
    else:
        return True


def get_signature(nonce, payload, secret, timestamp):
    """生成简道云的签名验证"""
    content = ':'.join([nonce, payload, secret, timestamp]).encode('utf-8')
    m = hashlib.sha1()
    m.update(content)
    return m.hexdigest()


def validate_signature(req, secret, signature) -> bool:
    """验证简道云发来的消息的签名是否正确？"""
    payload = req.data.decode('utf-8')
    nonce = req.args.get('nonce')
    timestamp = req.args.get('timestamp')
    if nonce is None or timestamp is None:
        return False
    else:
        if signature != get_signature(nonce, payload, secret, timestamp):
            return False
        else:
            return True


@app.route("/listen_<key>", methods=['get', 'post'])
def listen_func(key):
    """
    监听简道云发送过来的消息,绑定在39.108.67.178上运行。
    尽量让47.106.68.161上的JDY工作保持单一，只负责爬虫部分。
    因为爬虫服务器还在评估中，一旦资源消耗严重，就很可能重写。
    """
    mes = {"message": "success"}
    headers = request.headers
    event_id = headers.get("X-JDY-DeliverId")
    signature = headers.get("X-JDY-Signature")
    data = request.json
    print(event_id)
    print(signature)
    print(data)
    if key == "customermanagerrelation":
        """更新客户和管理者之间的关系"""
        secret_str = 'n63tPGK9e7TvrAqPXnUTwiGG'  # 不同的消息定义的secret不同，用来验证消息的合法性
        check = validate_signature(request, secret_str, signature)
        print("signal_test check is {}".format(check))
        if not check:
            return abort(404)
        else:
            """
            字段名称	字段ID	字段类型	说明
            表单名称	formName	string	
            数据ID	_id	string	数据的唯一ID
            提交人	creator	json	
            修改人	updater	json	
            删除人	deleter	json	
            提交时间	createTime	string	
            更新时间	updateTime	string	
            删除时间	deleteTime	string	
            日期时间	_widget_1515400344910	string	
            EC命名	_widget_1516598763647	string	
            客户姓名	_widget_1515400344920	string	
            首次接触时间	_widget_1516598763627	string	
            客户MT账号	_widget_1515400344933	number	
            所属平台	_widget_1517984569439	string	
            所属员工	_widget_1520476984707	string	
            所属经理	_widget_1520476984720	string	
            所属总监	_widget_1520476984733	string	
            客户状态	_widget_1516347713330	string	
            激活金额/美金	_widget_1515400345101	number	
            备注	_widget_1522391716801	number	
            example:
            {
              "op": "data_create",
              "data": {
                "formName": "开户激活",
                "_id": "5acd21b714c0ae71e9271630",
                "creator": {
                  "_id": "5acd21b714c0ae71e9271633",
                  "name": "张秀兰"
                },
                "updater": {
                  "_id": "5acd21b714c0ae71e9271634",
                  "name": "唐伟"
                },
                "deleter": {
                  "_id": "5acd21b714c0ae71e9271635",
                  "name": "任涛"
                },
                "createTime": "2018-04-10T14:16:38.10Z",
                "updateTime": "2018-04-10T01:07:48.739Z",
                "deleteTime": "2018-04-10T02:53:08.761Z",
                "_widget_1515400344910": "2018-04-10T06:25:13.146Z",
                "_widget_1516598763647": "受问须史",
                "_widget_1515400344920": "这着向几",
                "_widget_1516598763627": "2018-04-10T14:54:51.174Z",
                "_widget_1515400344933": -930.3609,
                "_widget_1517984569439": "响才之转",
                "_widget_1520476984707": "即第界转",
                "_widget_1520476984720": "少说民断",
                "_widget_1520476984733": "将只素精",
                "_widget_1516347713330": "党权划",
                "_widget_1515400345101": -289.5047,
                "_widget_1522391716801": 647.2173
              }
            }
            """
            op = data['op']
            data = data['data']
            record_id = data['_id']
            create_date_str = data.get('createTime')
            print("create_date_str is {}".format(create_date_str))
            create_date = get_datetime_from_str(create_date_str)
            if isinstance(create_date, datetime.datetime):
                create_date = create_date + datetime.timedelta(hours=8)
            update_date_str = data.get('updateTime')
            print("update_date_str is {}".format(update_date_str))
            update_date = get_datetime_from_str(update_date_str)
            if isinstance(update_date, datetime.datetime):
                update_date = update_date + datetime.timedelta(hours=8)
            delete_date_str = data.get('deleteTime')
            print("delete_date_str is {}".format(delete_date_str))
            delete_date = get_datetime_from_str(delete_date_str)
            if isinstance(delete_date, datetime.datetime):
                delete_date = delete_date + datetime.timedelta(hours=8)
            mt4_account = str(data.get("_widget_1515400344933"))
            customer_name = data.get("_widget_1515400344920")
            platform = data.get("_widget_1517984569439")
            if platform == '盛汇中国':
                platform = 'shengfxchina'
            elif platform == 'fx888':
                platform = 'shengfx888'
            elif platform == 'fx china':
                platform = 'shengfxchina'
            else:
                pass
            sales_name = data.get("_widget_1520476984707")
            manager_name = data.get("_widget_1520476984720")
            director_name = data.get("_widget_1520476984733")
            args = {
                "record_id": record_id,
                "create_date": create_date,
                "update_date": update_date,
                "delete_date": delete_date,
                "mt4_account": mt4_account,
                "customer_name": customer_name,
                "platform": platform,
                "sales_name": sales_name,
                "manager_name": manager_name,
                "director_name": director_name
            }
            args = {k: v for k, v in args.items() if v is not None}
            print("op is {}".format(op))
            print(args)
            if op == 'data_create':
                f = {"mt4_account": args.pop("mt4_account")}
                """如果是创建用户？那就先检查是否重复？"""
                r = CustomerManagerRelation.find_one_plus(filter_dict=f, instance=False)
                if r is not None:
                    """有重复客户，发送警告消息，仍然添加"""
                    title = "重复的添加客户！mt4账户：{}".format(mt4_account)
                    mes['message'] = title
                    content = ''
                    send_mail(title=title, content=content)
                else:
                    pass
                args = {"$set": args}
                r = CustomerManagerRelation.find_one_and_update_plus(filter_dict=f, update_dict=args, upsert=True)
                print(r)
            elif op == 'data_update':
                """修改用户关系，有记录就修改，没记录就插入"""
                f = {"mt4_account": args.pop("mt4_account")}
                r = CustomerManagerRelation.find_one_plus(filter_dict=f, instance=False)
                if r is None:
                    """没有对应客户，发送警告消息，修改变添加"""
                    title = "修改客户时没有发现对应客户！mt4账户：{}".format(mt4_account)
                    mes['message'] = title
                    content = '{}'.format(args)
                    send_mail(title=title, content=content)
                else:
                    pass
                args = {"$set": args}
                r = CustomerManagerRelation.find_one_and_update_plus(filter_dict=f, update_dict=args, upsert=True)
                print(r)
            elif op == "data_remove":
                """删除用户关系"""
                f = {"record_id": record_id}
                r = CustomerManagerRelation.find_one_plus(filter_dict=f, instance=False)
                if r is None:
                    title = "无法删除，因为没有对应的客户！_id：{}".format(record_id)
                    mes['message'] = title
                    content = '{}'.format(args)
                    send_mail(title=title, content=content)
                else:
                    """有客户，可以删除"""
                    args = {"$set": {"delete_date": delete_date}}
                    r = CustomerManagerRelation.find_one_and_update_plus(filter_dict=f, update_dict=args, upsert=False)
                    print(r)
            else:
                pass
    else:
        mes['message'] = '错误的path'
    return json.dumps(mes)


@app.route("/")
def hello():
    return "hello world"


@app.route('/page1.html')
def hello_world():
    return render_template("page1.html")


@app.route("/register_demo.html")
def register_demo_page():
    return render_template("register_demo.html")


@app.route("/register.js", methods=['get'])
def return_register_js_func():
    """返回带csrf保护的注册脚本"""
    csrf_token = get_token()
    key = 'register.js'
    js = "var csrf_token = '{}';\n".format(csrf_token)
    js_content = cache.get(key)
    if js_content is None:
        js_content = ''
        with open("static/js/register.js", "r", encoding="utf-8") as f:
            for line in f:
                js_content += line
        cache.set(key, js_content, timeout=60 * 1)
    js += js_content
    resp = make_response(js)
    resp.headers.set('Content-Type', "application/javascript; charset=utf-8")  # 以脚本形式返回
    resp.headers.set("Access-Control-Allow-Origin", "*")  # 跨域
    return resp


@app.route("/send_sms", methods=['POST', 'options'])
@token_auth.token_required
def send_sms_func():
    """短信接口"""
    resp = make_response()
    if request.method.lower() == 'options':
        """
        cros预检通道，需要配合allow_cross_domain(response)才能生效
        注意函数配置中的  X-Auth-Token 参数
        这个是和js脚本中 setRequestHeader("X-Auth-Token", csrf_token);  verify_token函数的验证方法都是对应的。
        """
        origin = request.headers.get("origin")
        if AllowOrigin.allow(origin):
            resp = make_response()
        else:
            abort(404)
    else:
        phone = request.args.get("user_phone") if request.form.get("user_phone") is None else \
            request.form.get("user_phone")
        result = sms_module.send_sms(phone)
        resp = make_response(json.dumps(result))
        resp.headers.set("Access-Control-Allow-Origin", "localhost:63342")  # 跨域
    return resp


@app.route("/register", methods=['post', ''])
@token_auth.token_required
def my_register():
    """注册接口"""
    resp = make_response()
    if request.method.lower() == 'options':
        """
        cros预检通道，需要配合allow_cross_domain(response)才能生效
        注意函数配置中的  X-Auth-Token 参数
        这个是和js脚本中 setRequestHeader("X-Auth-Token", csrf_token);  verify_token函数的验证方法都是对应的。
        """
        origin = request.headers.get("origin")
        if origin in ["http://localhost:63342"]:
            resp = make_response()
        else:
            abort(404)
    else:
        sms_code = get_arg(request, "sms_code")
        user_name = get_arg(request, "user_name", "")
        phone = get_arg(request, "user_phone")
        page_url = get_arg(request, "page_url")
        referrer = get_arg(request, "referrer")
        search_keyword = get_arg(request, "search_keyword")
        customer_description = get_arg(request, "customer_description", '')
        user_agent = request.user_agent
        args = {
            "user_name": user_name, "phone": phone, "referrer": referrer,
            "description": customer_description, "search_keyword": search_keyword,
            "user_agent": user_agent.string, "page_url": page_url,
            "time": datetime.datetime.now()
        }
        print(args)
        result = sms_module.check_sms_code(phone=phone, sms_code=sms_code)
        # result = 1
        if result:
            """短信验证成功,可以注册"""
            print("短信验证成功,可以注册")
            result = item_module.Customer.reg(**args)
        else:
            result = {'message': "短信验证失败"}
        resp = make_response(json.dumps(result))
        resp.headers.set("Access-Control-Allow-Origin", "*")
        logger.exception(resp.headers)
        print(resp.headers)
    return resp


@app.route("/xd_login", methods=['post', 'get'])
def login_func():
    """管理登录页"""
    ip = get_real_ip(request)
    print("ip is {}".format(ip))
    if request.method.lower() == 'get':
        return render_template("login.html")
    elif request.method.lower() == 'post':
        phone = get_arg(request, "phone", None)
        password = get_arg(request, "password", None)
        if phone and password:
            res = user_module.User.login(phone, password)
            mes = {"message": "success"}
            if isinstance(res, dict):
                if res['message'] == "success":
                    save_platform_session(**res['data'])
            else:
                mes = {"message": "登录错误"}
            return json.dumps(mes)
        else:
            return abort(404)
        pass
    else:
        return abort(404)


@app.route("/customer_list", methods=['get', 'post'])
@check_platform_session
def customer_list_func():
    """注册用户列表页"""
    if request.method.lower() == 'get':
        index = get_arg(request, "index", None)
        res = item_module.Customer.page(index=index, num=200)
        return render_template("customer_list.html", customer_list=res['data'])
    elif request.method.lower() == 'post':
        op_type = get_arg(request, "type")
        if op_type == "delete":
            """删除用户"""
            customer_id = get_arg(request, "_id")
            filter_dict = {"_id": get_obj_id(customer_id)}
            mes = {"message": "success"}
            res = item_module.Customer.find_one_and_delete(filter_dict=filter_dict)
            if res is None:
                mes['message'] = "删除失败"
            else:
                pass
            return json.dumps(mes)
    else:
        return abort(404)


@app.after_request
def allow_cross_domain(response):
    """允许跨域资源访问管理"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    allow_headers = "Referer,Accept,Origin,User-Agent,X-Auth-Token"
    response.headers['Access-Control-Allow-Headers'] = allow_headers
    # 也可以在此设置cookie
    # resp.set_cookie('username', 'the username')
    return response


if __name__ == '__main__':
    # app.debug = True  # 这一行必须在toolbar = DebugToolbarExtension(app)前面,否则不生效
    # toolbar = DebugToolbarExtension(app)
    # app.run(host="0.0.0.0", port=port, threaded=True)
    """正常模式"""
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
