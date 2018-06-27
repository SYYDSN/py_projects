#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
import json
from tools_module import *
from model.company_module import Company
from model.identity_validate import GlobalSignature
from flask import request


"""注册蓝图"""
web_blueprint = Blueprint("web_blueprint", __name__, url_prefix="/web", template_folder="templates/web")


"""用于站点部分的视图函数"""


def login_func(series: str, **kwargs) -> str:
    """
    登录函数. 加密接口.所有参数封装在payload中.
    :param series: 用于区分不同的登录用户 company/operator/driver/admin  企业/运营/司机用户/管理员  默认是company(公司)
    :param kwargs: 备用参数
    :return:
    """
    mes = {"message": "success"}
    method = request.method.lower()
    if method == "get":
        """测试接口可用"""
        mes['method'] = method
    else:
        """登录接口"""
        payload = get_arg(request, "payload", "")
        if payload == "":
            mes['message'] = "参数错误"
        else:
            """解密密文"""
            payload = GlobalSignature.decode(jwt_str=payload)
            print(payload)
            if isinstance(payload, dict) and "user_name" in payload and "user_password" in payload:
                user_name = payload['user_name']
                user_password = payload['user_password']
                """看看是什么类型登录?"""
                if series == 'company':
                    mes = Company.login(user_name=user_name, user_password=user_password)
                else:
                    mes['message'] = "功能未实现"
            else:
                mes['message'] = "解码失败"
    return json.dumps(mes)


def driver_page_func() -> str:
    """
    分页查询司机简历. 加密接口.所有参数封装在payload中.
    :return:
    """
    mes = {"message": "success"}
    method = request.method.lower()
    if method == "get":
        """测试接口可用"""
        mes['method'] = method
    else:
        """登录接口"""
        payload = get_arg(request, "payload", "")
        if payload == "":
            mes['message'] = "参数错误"
        else:
            """解密密文"""
            payload = GlobalSignature.decode(jwt_str=payload)
            print(payload)
            if isinstance(payload, dict) and "query_dict" in payload:
                """
                分页查询的条件:
                query_dict: dict 类型, 查询条件字典,必须参数,可以是空字典
                sort_dict: dict 类型, 排序字典,必须参数,可以是空字典
                projection: list 类型, 投影字段,非必须参数,建议不要由客户端传送此参数而是由函数自己定义
                page_size: int 类型, 每页多少条记录? 非必须字段.默认一页10条
                page_size: int 类型, 第几页? 非必须字段.默认1,第一页
                to_dict: bool 类型, 转字典? 非必须字段.默认转,客户端不要传送此参数.
                can_json: bool 类型, 为json序列化做转换? 非必须字段.默认False,此函数建议设置为True,客户端不要传送此参数.
                函数本身需要一直传送此参数.
                """
            else:
                mes['message'] = "解码失败"
    return json.dumps(mes)


"""集中注册函数"""


web_blueprint.add_url_rule(rule="/login_<series>", view_func=login_func, methods=['get', 'post'])  # 注册
web_blueprint.add_url_rule(rule="/driver_page", view_func=driver_page_func, methods=['get', 'post'])  # 分页查询司机信息
