#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import ujson
import zerorpc
from bson.objectid import ObjectId
import datetime
from flask.globals import LocalProxy
from django.http import HttpRequest


"""token检查的RPC客户端"""


class RPC(dict):
    """
    提供验证token的服务的类
    定制的返回体
    """
    def __bool__(self):
        if self.get("message") == "success":
            return True
        else:
            return False

    @classmethod
    def before(cls, req: object):
        """记录用户操作的入日志,这是个快捷方式"""
        return cls.before(req)

    def after(self, response: (dict, str), to_json: bool = True) -> (str, dict):
        """记录用户操作的出日志,这是个快捷方式"""
        return self.record_response(response, to_json)

    def record_response(self, response: (dict, str), to_json: bool = True) -> (str, dict):
        """
        记录返回结果
        :param response: 函数运行的返回体.必须是字典或者json.
        :param to_json: 是否将返回值转换为json.
        :return: json
        """
        if isinstance(response, str):
            response = ujson.loads(response)
        else:
            pass
        if isinstance(response, dict):
            response = to_flat_dict(response)
            c = zerorpc.Client()
            c.connect("tcp://127.0.0.1:4242")  # 连接到rpc服务器
            event_id = self.get('event_id')
            if event_id is None:
                e2 = {
                        "error": str("12"),
                        "file": __file__,
                        "func": sys._getframe().f_code.co_name
                    }
                c.record_error(doc=e2)
                c.close()
            else:
                args = {
                    "_id": event_id,
                    "response": response
                }
                try:
                    c.after_response(args)
                except Exception as error:
                    print(error)
                    e2 = {
                        "error": str(error),
                        "file": __file__,
                        "func": sys._getframe().f_code.co_name
                    }
                    c.record_error(doc=e2)
                finally:
                    c.close()
            return ujson.dumps(response) if to_json else response
        else:
            ms = "response参数必须是字典或者json格式"
            raise TypeError(ms)

    @classmethod
    def check_request(cls, req: object):
        """记录用户操作的入日志"""
        resp = RPC(message="success")
        init = {
            "ip": "",
            "user_agent": "",
            "user_id": 0,
            "host": "",
            "path": "",
            "method": "",
            "web_framework": "",
            "get_args": dict(),
            "post_args": dict(),
            "json_args": dict(),
        }
        if isinstance(req, LocalProxy):
            """flask请求"""
            b = datetime.datetime.now()
            init['web_framework'] = "flask"
            init['ip'] = get_real_ip(req=req)
            init['user_agent'] = req.headers.get("user_agent")
            authorization = req.headers.get("authorization")
            if authorization is None:
                pass
            else:
                init['authorization'] = authorization
            init['user_id'] = 0
            init['host'] = req.host
            init['path'] = req.path
            init['method'] = req.method.lower()
            init['get_args'] = {k: v for k, v in req.args.items()}
            init['post_args'] = {k: v for k, v in req.form.items()}
            init['json_args'] = req.json
            c = zerorpc.Client()
            c.connect("tcp://127.0.0.1:4242")  # 连接到rpc服务器
            oid = None
            try:
                oid = c.before_request(init)
            except Exception as error:
                print(error)
                e2 = {
                    "error": str(error),
                    "file": __file__,
                    "func": sys._getframe().f_code.co_name
                }
                c.record_error(doc=e2)
            finally:
                c.close()
                e = datetime.datetime.now()
                print((e - b).total_seconds())
                if isinstance(oid, dict):
                    resp.update(oid)
                else:
                    resp['message'] = "保存数据失败,请联系管理员"
        elif isinstance(req, HttpRequest):
            """django的请求"""
            b = datetime.datetime.now()
            ip = req.META['HTTP_X_FORWARDED_FOR'] if req.META.get('HTTP_X_FORWARDED_FOR') else req.META['REMOTE_ADDR']
            user_agent = req.META['HTTP_USER_AGENT']
            authorization = req.META.get('HTTP_AUTHORIZATION')  # 可能是None
            path = req.path
            get_args = req.GET.dict()
            method = req.method.lower()
            post_args = req.POST.dict()
            try:
                json_args = ujson.loads(req.body)
            except Exception as e:
                print(e)
                json_args = dict()
            finally:
                pass
            init['web_framework'] = "django"
            init['ip'] = ip
            init['user_agent'] = user_agent
            if authorization is None:
                pass
            else:
                init['authorization'] = authorization
            init['user_id'] = 0
            init['host'] = req.get_host()
            init['path'] = path
            init['method'] = method
            init['get_args'] = get_args
            init['post_args'] = post_args
            init['json_args'] = json_args
            c = zerorpc.Client()
            c.connect("tcp://127.0.0.1:4242")  # 连接到rpc服务器
            oid = None
            try:
                oid = c.before_request(init)
            except Exception as error:
                print(error)
                e2 = {
                    "error": str(error),
                    "file": __file__,
                    "func": sys._getframe().f_code.co_name
                }
                c.record_error(doc=e2)
            finally:
                c.close()
                e = datetime.datetime.now()
                print((e - b).total_seconds())
                if isinstance(oid, dict):
                    resp.update(oid)
                else:
                    resp['message'] = "保存数据失败,请联系管理员"
        else:
            web_framework = req.__class__.__name__
            ms = "未意料的web框架类型: {}".format(web_framework)
            print(ms)
            resp['message'] = ms
        return resp


def get_real_ip(req):
    """
    获取当前请求的真实ip。参数只有一个：
    1.req  当前的请求。一般都是传入当前上下文的request
    return ip地址(字符串格式)
    注意，如果前端的反向代理服务器是nginx的话，需要在配置文件中加上几句。
    在location / 配置下面的proxy_pass   http://127.0.0.1:5666; 后面加上
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    然后才可以用headers["X-Forwarded-For"]取真实ip
    虽然只加proxy_set_header X-Real-IP $remote_addr;这一句的话。
    也可以用request.headers["X-Real-IP"]获取。
    但为了和IIS的兼容性。还是需要再加一句
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    参数
    :parm req: flask 是request对象，
    tornado是 tornado.web.RequestHandler.request或者tornado.websocket.WebSocketHandler.reuest
    """
    try:
        ip = req.headers["X-Forwarded-For"].split(":")[0]
    except KeyError as e:
        ip = req.remote_addr  # 注意：tornado是 request.remote_ip   flask是 req.remote_addr
    if ip.find(",") != -1:
        """处理微信登录时转发的双ip"""
        ip = ip.split(",")[0]
    return ip


def other_can_json(obj):
    """
    把其他对象转换成可json,是to_flat_dict的内部函数
    v = v.strftime("%F %H:%M:%S.%f")是v = v.strftime("%Y-%m-%d %H:%M:%S")的
    简化写法，其中%f是指毫秒， %F等价于%Y-%m-%d.
    注意，这个%F只可以用在strftime方法中，而不能用在strptime方法中
    """
    if isinstance(obj, datetime.datetime):
        if obj.hour == 0 and obj.minute == 0 and obj.second == 0 and obj.microsecond == 0:
            return obj.strftime("%F")
        else:
            return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, datetime.date):
        return obj.strftime("%F")
    elif isinstance(obj, list):
        return [other_can_json(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: other_can_json(v) for k, v in obj.items()}
    else:
        return obj


def to_flat_dict(a_dict, ignore_columns: list = list()) -> dict:
    """
    转换成可以json的字典,这是一个独立的方法
    :param a_dict: 待处理的doc.
    :param ignore_columns: 不需要返回的列
    :return:
    """
    return {other_can_json(k): other_can_json(v) for k, v in a_dict.items() if k not in ignore_columns}


if __name__ == "__main__":
    pass
