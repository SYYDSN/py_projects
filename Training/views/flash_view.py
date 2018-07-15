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
flash_blueprint = Blueprint("web_blueprint", __name__, url_prefix="/flash", template_folder="templates/web")


"""用于闪卡训练的视图函数"""


def hello() -> str:
    """hello world"""
    return "hello baby"


def file_func(action, table_name):
    """
    保存/获取文件,
    :param action: 动作, save/get(保存/获取)
    :param table_name: 文件类对应的表名.
    :return:
    """
    mes = {"message": "success"}
    """
    tables表名,分别存储不同的类的实例.
    1. base_info                  文件存储基础表,对应mongo_db.BaseFile
    2. flash_image                闪卡图片类,对应model.flash_image.FlashImage
    """
    tables = ['base_file', 'flash_image']
    table_name = table_name if table_name in tables else 'base_file'
    if action == "save":
        """保存文件"""
        r = BaseFile.save_flask_file(req=request, collection=table_name)
        if isinstance(r, ObjectId):
            mes['_id'] = str(r)
        else:
            mes['message'] = "保存失败"
    elif action == "view":
        """获取文件"""
        fid = get_arg(request, "fid", "")
        if isinstance(fid, str) and len(fid) == 24:
            fid = ObjectId(fid)
            f = {"_id": fid}
            r = BaseFile.find_one_cls(filter_dict=f, collection=table_name)
            if r is None:
                return abort(404)
            else:
                mime_type = "image/jpeg" if r.get('mime_type') is None else r['mime_type']
                file_name = "1.jpeg" if r.get('file_name') is None else r['file_name']
                """把文件名的中文从utf-8转成latin-1,这是防止中文的文件名造成的混乱"""
                file_name = file_name.encode().decode('latin-1')
                data = r['data']
                data = BytesIO(initial_bytes=data)
                resp = make_response(send_file(data, attachment_filename=file_name, as_attachment=True,
                                               mimetype=mime_type))
                return resp
        else:
            mes['message'] = '无效的id'
    else:
        mes['message'] = "不支持的操作"
    return json.dumps(mes)


def page_flash_images():
    """
    分页显示闪卡
    :return:
    """


"""集中注册函数"""


"""hello"""
flash_blueprint.add_url_rule(rule="/hello", view_func=hello, methods=['get', 'post'])
"""保存或者获取文件(mongodb存储)"""
flash_blueprint.add_url_rule(rule="/file/<action>/<table_name>", view_func=file_func, methods=['post', 'get'])