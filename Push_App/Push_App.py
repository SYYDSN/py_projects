from flask import Flask
from flask import abort
from flask import request
from flask_session import Session
from views.manage_view import manage_blueprint
import functools
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
        print("没有发现json数据")
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
