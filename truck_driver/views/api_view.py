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
from model.driver_module import DriverResume
from flask import request
from mongo_db import db_name
from mongo_db import DBRef


"""注册蓝图"""
api_blueprint = Blueprint("api_blueprint", __name__, url_prefix="/api", template_folder="templates/web")


"""用于接口部分的视图函数，主要被分离式前端站点调用"""


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
                    mes = Company.login(user_name=user_name, user_password=user_password, can_json=True)
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
            if isinstance(payload, dict) and "filter" in payload:
                """
                分页查询的条件:
                filter_dict: dict 类型, 查询条件字典,必须参数,可以是空字典
                sort_dict: dict 类型, 排序字典,必须参数,可以是空字典
                projection: list 类型, 投影字段,非必须参数,建议不要由客户端传送此参数而是由函数自己定义
                page_size: int 类型, 每页多少条记录? 非必须字段.默认一页10条
                page_index: int 类型, 第几页? 非必须字段.默认1,第一页
                to_dict: bool 类型, 转字典? 非必须字段.默认转,客户端不要传送此参数.
                can_json: bool 类型, 为json序列化做转换? 非必须字段.默认False,客户端不要传送此参数.
                函数本身需要一直传送此参数.
                """
                filter_dict = payload.pop("filter", dict())
                sort_dict = payload.pop("sort", dict())
                sort_dict = None if len(sort_dict) == 0 else sort_dict
                projection = [
                    '_id',                   # id ObjectId
                    'gender',                # 性别 str zh-cn
                    'age',                   # 年龄 int
                    'status',                # 是否在职? int -1 个体经营/0 离职/ 1 在职
                    'living_place',          # 现居住地 str
                    'want_job',              # 是否有求职意愿? bool
                    "expected_salary",       # 期望待遇,int元素的二元数组,详见类说明
                    "dl_license_class",      # 准驾车型, str
                    "rtqc_license_class",    # 从业资格证, str
                    "last_company",          # 最后工作的公司, str
                    "driving_experience",    # 驾龄 int
                    "industry_experience"    # 从业年限 int
                ]
                page_size = payload.pop("page_size", 10)
                if isinstance(page_size, int):
                    pass
                elif isinstance(page_size, str) and page_size.isdigit():
                    page_size = int(page_size)
                elif isinstance(page_size, float):
                    page_size = int(page_size)
                else:
                    page_size = 10
                page_index = payload.pop("page_index", 1)
                if isinstance(page_index, int):
                    pass
                elif isinstance(page_index, str) and page_index.isdigit():
                    page_index = int(page_index)
                elif isinstance(page_index, float):
                    page_index = int(page_index)
                else:
                    page_index = 1
                args = dict()
                args['filter_dict'] = filter_dict
                args['sort_dict'] = sort_dict
                args['projection'] = projection
                args['page_size'] = page_size
                args['page_index'] = page_index
                args['to_dict'] = True
                args['can_json'] = True
                drivers = DriverResume.query_by_page(**args)
                data = {"drivers": drivers}
                data = GlobalSignature.encode(payload=data)
                mes['data'] = data
            else:
                mes['message'] = "解码失败"
    return json.dumps(mes)


"""集中注册函数"""


api_blueprint.add_url_rule(rule="/login_<series>", view_func=login_func, methods=['get', 'post'])  # 注册
api_blueprint.add_url_rule(rule="/driver_page", view_func=driver_page_func, methods=['get', 'post'])  # 分页查询司机信息
