#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import render_template
from flask import send_file
from flask import make_response
from flask import abort
from tools_module import *
from mongo_db import BaseFile
from io import BytesIO
import json


"""注册蓝图"""
user_blueprint = Blueprint("user_blueprint", __name__, url_prefix="/user", template_folder="templates/web")


"""用于闪卡训练的视图函数"""


def hello() -> str:
    """hello world"""
    return "hello user"


def syllabus_view_func() -> str:
    """
    课程表
    :return:
    """


def page_flash_images():
    """
    分页显示闪卡
    :return:
    """


"""集中注册函数"""


"""hello"""
user_blueprint.add_url_rule(rule="/hello", view_func=hello, methods=['get', 'post'])
"""课程表"""
user_blueprint.add_url_rule(rule="/syllabus", view_func=syllabus_view_func, methods=['post', 'get'])