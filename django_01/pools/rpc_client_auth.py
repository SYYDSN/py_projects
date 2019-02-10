#  -*- coding: utf-8 -*-
import zerorpc
from flask.globals import LocalProxy
from django.http import HttpRequest
import ujson
import datetime
from functools import wraps


"""RPC客户端模块"""


class Resp(dict):
    """
    定制的返回体
    """
    def __bool__(self):
        if self.get("message") == "success":
            return True
        else:
            return False


def check_request(req: object):
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
        init['web_framework'] = "flask"
    elif isinstance(req, HttpRequest):
        """django的请求"""
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
        init['authorization'] = authorization
        init['user_id'] = 0
        init['host'] = req.get_host()
        init['path'] = path
        init['method'] = method
        init['get_args'] = get_args
        init['post_args'] = post_args
        init['json_args'] = json_args
    else:
        web_framework = req.__class__.__name__
        ms = "未意料的请求体类型: {}".format(web_framework)
        raise ValueError(ms)
