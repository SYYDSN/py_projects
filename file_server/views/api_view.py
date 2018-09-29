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
from module.captcha_module import MyImageCaptcha


"""通用蓝图"""
api_blueprint = Blueprint("api_blueprint", __name__, url_prefix="/api", template_folder="templates")


def get_version():
    """
    返回一个随机的版本号
    :return:
    """
    return uuid4().hex


def hello_func():
    return "hello i am api view!"


def get_captcha_url():
    """
    获取验证码图片的链接
    :return:
    """
    host_name = request.host_url
    _id = str(MyImageCaptcha.get_image_id())
    url = "{}images/captcha/{}".format(host_name, _id)
    mes = {"message": "success", "url": url}
    return json.dumps(mes)


def captcha_func(c_id):
    """
    返回验证码图片的数据
    :return:
    """
    if isinstance(c_id, str) and len(c_id) == 24:
        mime_type = "image/png"
        file_name = "captcha.png"
        """把文件名的中文从utf-8转成latin-1,这是防止中文的文件名造成的混乱"""
        file_name = file_name.encode().decode('latin-1')
        data = MyImageCaptcha.get_image_data(_id=c_id)
        if isinstance(data, BytesIO):
            img = Image.open(data)
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
            return abort(404, "not found captcha image!")
    else:
        return abort(404, "invalid captcha id!")


def captcha_demo():
    """
    图形验证码示范页面, 未完成, 2018-9-29
    :return:
    """
    method = request.method.lower()
    if method == "get":
        return render_template("captcha_demo.html")





"""集中注册函数"""


"""hello"""
api_blueprint.add_url_rule(rule="/hello", view_func=hello_func, methods=['get', 'post'])
"""返回验证码图片的数据"""
api_blueprint.add_url_rule(rule="/captcha/<c_id>", view_func=captcha_func, methods=['get'])
"""返回验证码图片的url"""
api_blueprint.add_url_rule(rule="/get_captcha_url", view_func=get_captcha_url, methods=['get', 'post'])
"""图片验证码示范页"""
api_blueprint.add_url_rule(rule="/captcha_demo", view_func=captcha_demo, methods=['post', 'get'])