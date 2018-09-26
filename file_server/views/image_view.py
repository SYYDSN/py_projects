#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from uuid import uuid4
from flask import request
from flask import abort
from flask import render_template
from flask import make_response
from flask import send_file
from tools_module import get_arg
from tools_module import get_real_ip
from flask.blueprints import Blueprint
from mongo_db import BaseFile
from mongo_db import ObjectId
from PIL import Image
from io import BytesIO
import json


"""注册蓝图"""
image_blueprint = Blueprint("image_blueprint", __name__, url_prefix="/images", template_folder="templates")


def get_version():
    """
    返回一个随机的版本号
    :return:
    """
    return uuid4().hex


def hello_func():
    return "hello i am image view!"


def image_func(action: str = "", table_name: str = ""):
    """
    此函数仅允许上传/查看图片.
    当前使用auth参数作为验证 auth = '647a5253c1de4812baf1c64406e91396'
    :param action: 动作, save/get(保存/获取)
    :param table_name: 文件类对应的表名.
    :return:
    """
    mes = {"message": "success"}
    """
    tables表名,分别存储不同的类的实例.
    1. base_info                  文件存储基础表,对应mongo_db.BaseFile
    2. teacher_image                老师相关图片
    """
    tables = ['base_file', 'teacher_image', 'image_file']
    table_name = table_name if table_name in tables else 'base_file'
    auth = get_arg(req=request, arg="auth", default_value="")
    auth = request.headers.get("auth", "") if auth == "" else auth  # 参数和headers中，只要有一个带有词参数即可
    if action == "save":
        """保存文件"""
        if auth != "647a5253c1de4812baf1c64406e91396":
            mes['message'] = '未登录'
        else:
            from_ip = get_real_ip(request)
            agent = request.user_agent.string
            r = BaseFile.save_flask_file(req=request, collection=table_name, auth=auth, from_ip=from_ip, agent=agent)
            if isinstance(r, ObjectId):
                _id = str(r)
                mes['_id'] = _id
                if table_name == "image_file":
                    """这是站点图片"""
                    img_url = "/images/obj/view/{}?fid={}".format(table_name, _id)
                    mes['url'] = img_url
                else:
                    """后继的处理方式陆续添加"""
                    pass
            else:
                mes['message'] = "保存失败"
    elif action == "view":
        """获取文件/图片"""
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
                img = Image.open(BytesIO(initial_bytes=r['data']))
                """这2个参数暂时用不上"""
                img_width = img.width
                img_height = img.height
                """重设图片大小"""
                size = get_arg(req=request, arg="size", default_value="")  # 参数size用于重设尺寸 size=width*height
                if size != "":
                    temp = size.split("*")
                    if len(temp) > 1 and temp[0].isdigit() and temp[1].isdigit():
                        width = int(temp[0])
                        height = int(temp[1])
                    else:
                        width = 80
                        height = 60
                    img = img.resize(size=(width, height))
                else:
                    pass
                """旋转图片,虽然理论上可以进行任何角度的旋转,但是出于效果,最好只进行90度的整数倍旋转"""
                rotate = get_arg(req=request, arg="rotate", default_value="0")  # 参数rotate用于旋转图片 rotate=90
                if isinstance(rotate, str) and rotate.isdigit():
                    rotate = int(rotate)
                    img = img.rotate(rotate)
                else:
                    pass
                data = BytesIO()
                if img.mode == "RGBA":
                    """
                    png图片是4通道.而JPEG是RGB三个通道，所以PNG转BMP时候程序不知道A通道怎么办,
                    会报 cannot write mode RGBA as JPEG  的错误.
                    解决方法是检查img的mode,进行针对性的处理.
                    文件的后缀名也要做针对性的修改
                    """
                    file_format = "png"
                    file_name = "{}.{}".format(file_name.split(".")[0], file_format)
                else:
                    if img.mode != "GBA":
                        """转换图像格式"""
                        img = img.convert("RGB")
                    else:
                        pass
                    file_format = file_name.split(".")[-1]
                if file_format.lower() == "jpg":
                    file_format = 'jpeg'
                img.save(fp=data, format=file_format)
                data = BytesIO(initial_bytes=data.getvalue())  # initial_bytes的值必须是二进制本身,不能是ByteIO对象.
                resp = make_response(send_file(data, attachment_filename=file_name, as_attachment=True,
                                               mimetype=mime_type))
                return resp
        else:
            mes['message'] = '无效的id'
    else:
        mes['message'] = "不支持的操作"
    return json.dumps(mes)


def demo_func():
    """
    上传文件的示范页面
    :return:
    """
    return render_template("upload_demo.html")


"""集中注册函数"""


"""hello"""
image_blueprint.add_url_rule(rule="/hello", view_func=hello_func, methods=['get', 'post'])
"""图片存取"""
image_blueprint.add_url_rule(rule="/obj/<action>/<table_name>", view_func=image_func, methods=['get', 'post'])
"""上传图片示范页"""
image_blueprint.add_url_rule(rule="/upload_demo", view_func=demo_func, methods=['post', 'get'])