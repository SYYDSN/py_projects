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
import json


"""注册蓝图"""
flash_blueprint = Blueprint("web_blueprint", __name__, url_prefix="/flash", template_folder="templates/web")


"""用于闪卡训练的视图函数"""


def hello() -> str:
    """hello world"""
    return "hello baby"


"""集中注册函数"""


"""hello"""
flash_blueprint.add_url_rule(rule="/hello", view_func=hello, methods=['get', 'post'])