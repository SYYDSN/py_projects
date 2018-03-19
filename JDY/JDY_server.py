from flask import Flask
from flask import abort
from flask import make_response
from flask import render_template
from flask import render_template_string
from flask import send_file
from flask import request
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

secret_key = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key  # 配置会话密钥
SESSION_TYPE = "redis"
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
    """获取token"""
    uuid_str = uuid4().hex
    token = token_manager.generate(name=uuid_str).decode()
    cache.set(token, uuid_str, 3600)
    return token


@token_auth.verify_token
def verify_token(token):
    """token验证器"""
    if request.method.lower() == 'post':
        str1 = token_manager.verify(token)
        str2 = cache.get(token)
        if str2 is not None and str1 == str2:
            return True
        else:
            return False
    else:
        return True


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
    app.debug = True  # 这一行必须在toolbar = DebugToolbarExtension(app)前面,否则不生效
    toolbar = DebugToolbarExtension(app)
    app.run(host="0.0.0.0", port=port, threaded=True)
