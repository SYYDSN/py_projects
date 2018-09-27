#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from flask.blueprints import Blueprint
from flask import abort
from flask import make_response
from flask import render_template
from flask import send_file
import json
from bson.objectid import ObjectId
from tools_module import *
from mail_module import send_mail
from PIL import Image
from io import BytesIO
from module.image_module import Praise


"""一般视图函数"""


normal_blueprint = Blueprint("normal_blueprint", __name__, url_prefix="/normal", template_folder="templates")


def view_praise_img():
    """查看战绩图片"""
    fid = get_arg(request, "fid", "")
    if isinstance(fid, str) and len(fid) == 24:
        img = Praise.get_image(_id=fid)
        if img is None:
            return abort(404)
        else:
            mime_type = "image/jpeg"
            file_name = "1.jpeg"
            """把文件名的中文从utf-8转成latin-1,这是防止中文的文件名造成的混乱"""
            file_name = file_name.encode().decode('latin-1')
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
        return abort(404)


"""注册视图函数"""
normal_blueprint.add_url_rule(rule="/praise_image/view", view_func=view_praise_img, methods=['get', 'post'])