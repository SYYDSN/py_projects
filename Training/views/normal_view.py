#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import render_template


"""注册蓝图"""
normal_blueprint = Blueprint("normal_blueprint", __name__, url_prefix="/normal", template_folder="templates/normal")


"""用于暂时无法归类的视图函数"""


def hello() -> str:
    """hello world"""
    return "hello baby"


def clock_func():
    """时钟"""
    return render_template("normal/clock.html")


"""集中注册函数"""


"""hello"""
normal_blueprint.add_url_rule(rule="/hello", view_func=hello, methods=['get', 'post'])
"""clock"""
normal_blueprint.add_url_rule(rule="/clock", view_func=clock_func, methods=['get', 'post'])
