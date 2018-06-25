#  -*- coding: utf-8 -*-
from flask import Flask
from flask import abort
from flask import make_response
from flask import render_template
from mongo_db import get_datetime_from_str
from flask_session import Session
import sms_module
from mongo_db import get_obj_id
from flask_tokenauth import TokenAuth, TokenManager
from tools_module import *
from module.spread_module import AllowOrigin
from uuid import uuid4
from module import user_module, item_module
from module.item_module import *
import os
from mail_module import send_mail
from browser.crawler_module import CustomerManagerRelation

secret_key = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
# app.config['SERVER_NAME'] = "127.0.0.1:8001"  此域名下的所有子域名的session都会接受
app.config.from_object(__name__)
Session(app)


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
    raw = RawSignal(**data)
    raw.save_plus()  # 保存原始数据
    if key == "customermanagerrelation":
        """更新客户和管理者之间的关系"""
        secret_str = 'n63tPGK9e7TvrAqPXnUTwiGG'  # 不同的消息定义的secret不同，用来验证消息的合法性
        check = validate_signature(request, secret_str, signature)
        print("signal_test check is {}".format(check))
        if not check:
            return abort(404)
        else:
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
            customer_sn = int(data.get("_widget_1526780188629"))
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
                "customer_sn": customer_sn,
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
                    content = '{}'.format(args)
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
                    content = ''
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
    elif key == "distribution_scheme":
        """资源分配方案"""
        secret_str = 'lYLaLKgFX9Mi6ij19tpZELlt'  # 不同的消息定义的secret不同，用来验证消息的合法性
        check = validate_signature(request, secret_str, signature)
        print("signal_test check is {}".format(check))
        if not check:
            return abort(404)
        else:
            """
            {
                "_id" : ObjectId("5af626224513533cc34ea6e3"),
                "data" : {
                    "updateTime" : "2018-05-11T23:24:18.813Z",
                    "_widget_1525903100391" : [ 
                        "1", 
                        "3", 
                        "4", 
                        "6"
                    ],
                    "_id" : "5af62604c281e01263b74981",
                    "formName" : "今日分配方案",
                    "entryId" : "5af36ea9a618d61e69243ad7",
                    "deleteTime" : null,
                    "appId" : "5a658ca3b2596932dab31f0c",
                    "updater" : {
                        "name" : "徐立杰",
                        "_id" : "5a684c9b42f8c1bffc68f4b4"
                    },
                    "deleter" : null,
                    "submitPrompt" : {
                        "content" : ""
                    },
                    "createTime" : "2018-05-11T23:23:48.445Z",
                    "label" : "",
                    "creator" : {
                        "name" : "徐立杰",
                        "_id" : "5a684c9b42f8c1bffc68f4b4"
                    }
                },
                "op" : "data_update"
            }
            """
            op = data["op"]
            data = data['data']
            args = dict()
            _id = data['_id']
            _id = _id if isinstance(_id, ObjectId) else ObjectId(_id)
            args['groups'] = data['_widget_1525903100391']
            if op == "data_update":
                op = "update"
            elif op == "data_create":
                op = "insert"
            else:
                op = "other"
            if op == "insert":
                """添加分配方案"""
                create_date = mongo_db.get_datetime_from_str(data['createTime'])
                create_date = transform_time_zone(create_date)
                args["_id"] = _id
                args['create_date'] = create_date
                scheme = DistributionScheme(**args)
                r = scheme.save_plus()
                ms = "插入结果:{}".format((str(r)))
                logger.info(ms)
            if op == "update":
                """修改分配方案"""
                create_date = mongo_db.get_datetime_from_str(data['updateTime'])
                create_date = transform_time_zone(create_date)
                f = {"_id": _id}
                args['create_date'] = create_date
                u = {"$set": args}
                r = DistributionScheme.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)
                ms = "插入结果:{}".format((str(r)))
                logger.info(ms)
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
