from flask import Flask
from flask import render_template
from flask import abort
from flask import request
from flask_session import Session
from views.manage_view import manage_blueprint
import functools
from my_filter import mount_plugin
from module.items_module import *
import json


app = Flask(__name__)
key_str = os.urandom(24)  # 生成密钥，为session服务。
app.config['SECRET_KEY'] = key_str  # 配置会话密钥
app.config['SESSION_TYPE'] = "redis"  # session类型为redis
app.config['SESSION_PERMANENT'] = True  # 如果设置为True，则关闭浏览器session就失效
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)  # 持久化的会话的生存时间
app.register_blueprint(manage_blueprint)           # 注册平台操作视图
SESSION_TYPE = "redis"
Session(app)
port = 8900


"""扩展jinja2过滤器"""
mount_plugin(app)  # 注册jinja2的自定义过滤器


def check_auth(f):
    """
    装饰器.
    检查请求的身份,请求头信息不合法的不予相应
    :param f:
    :return:
    """
    @functools.wraps(f)
    def decorated_func(*args,  **kwargs):
        """
        装饰器函数
        :param args:
        :param kwargs:
        :return:
        """
        flag = False
        headers = request.headers
        key = "app-key"
        if key in headers:
            v = headers.get(key)
            if v == "affa687b-faed-45b8-b69b-17fdddea40fb":
                flag = True
            else:
                flag = False
        else:
            flag = False
        if flag:
            return f(*args, **kwargs)
        else:
            print("请求头验证失败")
            return abort(404)
    return decorated_func


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route("/contacts", methods=['post', 'get'])
@check_auth
def contacts_func():
    """
    接收app上传的联系人
    :return:
    """
    mes = {"message": "success"}
    json_data = request.json
    if json_data is None or len(json_data) == 0:
        print("没有发现json数据")
    else:
        """处理数据"""
        try:
            mes = Device.save_data(json_data=json_data)
        except Exception as e:
            print(e)
            mes['message'] = "db error"
        finally:
            if mes['message'] == "success":
                """拼接跳转地址"""
                host_url = request.host_url
                _id = mes.pop('_id')
                host_url = "{}tongxunlu/tongxunlu.asp?rid={}".format(host_url, _id)
                mes['redirect'] = host_url
            else:
                pass
    return json.dumps(mes)


@app.route("/location", methods=['post', 'get'])
@check_auth
def location_func():
    """
    收集位置信息
    :return:
    """
    mes = {"message": "success"}
    json_data = request.json
    if json_data is None or len(json_data) == 0:
        ms = "没有发现json参数"
        print(ms)
        mes['message'] = ms
    else:
        """处理数据"""
        try:
            mes = Location.save_data(json_data=json_data)
        except Exception as e:
            print(e)
            mes['message'] = "db error"
        finally:
            pass
    return json.dumps(mes)


@app.route("/start_args", methods=['post', 'get'])
@check_auth
def start_args_func():
    """
    查询启动参数
    :return:
    """
    mes = {"message": "success"}
    json_data = request.json
    if json_data is None or len(json_data) == 0:
        ms = "没有发现json参数"
        print(ms)
        mes['message'] = ms
    else:
        """处理数据"""
        try:
            registration_id = json_data.get("registration_id")
            mes = StartArgs.get_last()  # 获取最新的启动参数
        except Exception as e:
            print(e)
            mes['message'] = "db error"
        finally:
            pass
    return json.dumps(mes)


@app.route("/tongxunlu/<file_name>", methods=['post', 'get'])
# @check_auth
def html_func(file_name):
    """
    通用页面渲染之一
    :return:
    """
    names = os.listdir(os.path.join(os.path.dirname(__file__), "templates"))
    names = [x for x in names if x.lower().endswith(".html")]
    file_name = file_name.split(".")[0]
    file_name = "{}.html".format(file_name)
    if file_name in names:
        kw = dict()
        if file_name == "tongxunlu.html":
            """提交联系人页面"""
            rid = request.args.get("rid", "")
            if rid == "":
                pass
            else:
                device = Device.find_one(filter_dict={"_id": rid})
                if isinstance(device, dict):
                    kw['device'] = device
                else:
                    pass
        return render_template(file_name, **kw)
    else:
        return abort(404)




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
