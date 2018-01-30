from flask import Flask
from flask import make_response
from flask import render_template
from flask import render_template_string
from flask import send_file
from flask import request
from flask_wtf import FlaskForm
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from log_module import get_logger
import sms_module
import json
from werkzeug.contrib.cache import RedisCache
from tools_module import *
import item_module
from celery_module import to_jiandao_cloud_and_send_mail
import os

keystr = os.urandom(24)  # 生成密钥，为session服务。
app = Flask(__name__)
app.config['SECRET_KEY'] = keystr  # 配置会话密钥
SESSION_TYPE = "redis"
app.config.from_object(__name__)
Session(app)
csrf = CSRFProtect(app)       # 开启全局CSRF保护
cache = RedisCache()
logger = get_logger()
port = 9000


@app.route("/")
def hello():
    return "hello world"


@app.errorhandler
def csrf_error(reason):
    """记录csrf错误并跳转"""
    host_url = request.host_url
    base_url = request.base_url
    user_agent = request.user_agent
    args = get_args(request)
    referrer = request.referrer
    ip = get_real_ip(request)
    error_dict = {
        "time": datetime.datetime.now(),
        "host_url": host_url,
        "base_url": base_url,
        "referrer": referrer,
        "user_agent": user_agent.string,
        "args": args,
        "reason": reason,
        "client_ip": ip
    }
    error = item_module.CsrfError(**error_dict)
    error.save()
    return render_template('welcome.html')


@app.route('/page1.html')
def hello_world():
    return render_template("page1.html")


@app.route("/register_demo.html")
@csrf.exempt
def register_demo_page():
    return render_template("register_demo.html")


@app.route("/register.js", methods=['get'])
def return_register_js_func():
    """返回带csrf保护的注册脚本"""
    form = FlaskForm()
    csrf_token = form.csrf_token.current_token
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


@app.route("/send_sms", methods=['POST'])
def send_sms_func():
    """短信接口"""
    phone = request.args.get("user_phone") if request.form.get("user_phone") is None else \
        request.form.get("user_phone")
    result = sms_module.send_sms(phone)
    resp = make_response(json.dumps(result))
    resp.headers.set("Access-Control-Allow-Origin", "*")  # 跨域
    return resp


@app.route("/register", methods=['POST'])
def my_register():
    """注册接口"""
    sms_code = get_arg(request, "sms_code")
    user_name = get_arg(request, "user_name", "")
    phone = get_arg(request, "user_phone")
    search_keyword = get_arg(request, "search_keyword")
    customer_description = get_arg(request, "customer_description", '')
    referrer = request.referrer
    user_agent = request.user_agent
    host_url = request.host_url
    base_url = request.base_url
    args = {
        "user_name": user_name, "phone": phone, "referrer": referrer,
        "description": customer_description, "search_keyword": search_keyword,
        "user_agent": user_agent.string, "host_url": host_url, "base_url": base_url,
        "time": datetime.datetime.now()
    }
    print(args)
    to_jiandao_cloud_and_send_mail.delay(**args)
    result = sms_module.check_sms_code(phone=phone, sms_code=sms_code)
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
