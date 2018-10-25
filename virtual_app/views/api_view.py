#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
import json
from tools_module import *
from flask import request


"""注册蓝图"""
api_blueprint = Blueprint("api_blueprint", __name__, url_prefix="/api", template_folder="templates/api")


"""用于接口部分的视图函数，主要用于app调用"""


def hello_func() -> str:
    """
    hello world
    :return:
    """
    mes = {"message": "success"}
    return json.dumps(mes)



"""集中注册函数"""


"""hello world"""
api_blueprint.add_url_rule(rule="/hello", view_func=hello_func, methods=['get', 'post'])

