#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import datetime
from log_module import get_logger
from captcha.image import ImageCaptcha
import random
from io import BytesIO
from urllib.request import quote
import requests


"""验证码模块"""


logger = get_logger()


ObjectId = mongo_db.ObjectId


class ImageFile(mongo_db.BaseFile):
    """
    图片存储类
    """
    _table_name = "image_file"


class MyImageCaptcha(mongo_db.BaseDoc):
    """
    图片验证码的验证信息
    """
    _table_name = "image_captcha"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['code'] = str
    type_dict['create_time'] = datetime.datetime

    @classmethod
    def save_info(cls) -> ObjectId:
        """
        保存校验信息并返回一个id
        :return:
        """
        args = dict()
        args['_id'] = ObjectId()
        args['code'] = str(random.randint(1000, 9999))
        args['create_time'] = datetime.datetime.now()
        ses = cls.get_collection()
        r = ses.insert_one(document=args)
        if r is None:
            ms = "保存图片验证码的校验信息失败"
            logger.exception(msg=ms)
        else:
            return r.inserted_id

    @classmethod
    def get_code(cls, _id: (str, ObjectId)) -> str:
        """
        查询图形验证码的code
        :param _id:
        :return:
        """
        now = datetime.datetime.now()
        t = now - datetime.timedelta(minutes=15)
        _id = ObjectId(_id) if isinstance(_id, str) and len(_id) == 24 else _id
        f = {"_id": _id, "create_time": {"$gte": t}}
        ses = cls.get_collection()
        r = ses.find_one(filter=f)
        if r is None:
            return ''
        else:
            return r.get("code", "")

    @classmethod
    def get_image_id(cls) -> ObjectId:
        """
        获取图片的id,
        :return:
        """
        return cls.save_info()

    @classmethod
    def get_image_data(cls, _id: (str, ObjectId)) -> BytesIO:
        """
        根据id获取图片的数据
        :param _id:
        :return:
        """
        _id = ObjectId(_id) if isinstance(_id, str) and len(_id) == 24 else _id
        f = {"_id": _id}
        ses = cls.get_collection()
        r = ses.find_one(filter=f)
        if r is None:
            code = None
        else:
            code = r.get("code", None)
        if code is None:
            return None
        else:
            font = os.path.join(__project_dir__, "resource/fonts/YaHei.ttf")
            img = ImageCaptcha(fonts=[font])
            # img.write('code', 'code.png')  # 写入文件
            data = img.generate(code)
            return data


class MySmsCaptcha(mongo_db.BaseDoc):
    """
    短信验证码的验证信息
    """
    _table_name = "sms_captcha"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['phone'] = str
    type_dict['code'] = str
    type_dict['delay'] = int   # 有效期,单位分钟
    type_dict['create_time'] = datetime.datetime
    type_dict['last_validate'] = datetime.datetime
    type_dict['validate_result'] = int  # 验证是否成功,0表示未验证过. 1表示成功, -1表示验证失败, 2表示超期

    @classmethod
    def send_sms(cls, phone: str, template_id: int = 104630, arg_dict: dict = None, delay: int = 15) -> dict:
        """
        发送短信
        :param phone:
        :param template_id: 模板id,默认是注册短信模板
        :param arg_dict: 参数字典,默认是注册码的参数
        :param delay:   验证码有效期,单位分钟
        :return:
        """
        mes = {"message": "success"}
        delay = delay if isinstance(delay, int) and 0 < delay < 1441 else 15
        phone = phone if isinstance(phone, str) else str(phone)
        if len(phone) == 11 and phone.isdigit() and phone.startswith("1"):
            val = ''
            code = str(random.randint(1000, 9999))
            if arg_dict is None or len(arg_dict) == 0:
                arg_dict = {"code": code}
            else:
                pass
            for k, v in arg_dict.items():
                val += "#{}#={}".format(k, v)
            val = quote(val)
            url = "http://v.juhe.cn/sms/send"
            args = {
                "mobile": phone,
                "tpl_id": template_id,
                "key": "8e61ec4c76a83f6dae679df6f4317c63",
                "tpl_value": val
            }
            r = requests.get(url=url, params=args)
            status = r.status_code
            if status != 200:
                mes['message'] = "服务器返回了错误的状态码 {}".format(status)
            else:
                data = r.json()
                if data.get('error_code') == 0:
                    """保存短信信息"""
                    init = {
                        "_id": ObjectId(),
                        "phone": phone,
                        "code": code,
                        "delay": delay,
                        "create_time": datetime.datetime.now(),
                        "validate_result": 0
                    }
                    conn = cls.get_collection()
                    r = conn.insert_one(document=init)
                    if r is None:
                        mes['message'] = "数据保存失败"
                    else:
                        pass
                else:
                    """短信发送出错了"""
                    mes['message'] = data['reason']
        else:
            mes['message'] = "错误的参数:phone: {}".format(phone)
        return mes

    @classmethod
    def validate_code(cls, phone: str, code: str) -> dict:
        """
        验证短信验证码
        :param phone:  手机号码
        :param code:   验证码
        :return:   结果字典
        """
        mes = {"message": "success"}
        f = {"phone": phone}
        s = {"create_time": -1}
        one = cls.find_one_plus(filter_dict=f, sort_dict=s, instance=False)
        if one is None:
            mes['message'] = "此号码还未申请过验证码"
        else:
            old = one['code']
            delay = one['delay']
            create_time = one['create_time']
            validate_result = one['validate_result']
            if validate_result == 1:
                mes['message'] = "验证码已使用"
            elif validate_result == 2:
                mes['message'] = "验证码已过期"
            else:
                now = datetime.datetime.now()
                if (now - create_time).total_seconds() > delay * 60:
                    mes['message'] = "验证码已过期"
                    u = {"$set": {"validate_result": 2, "last_validate": now}}
                elif old == code:
                    u = {"$set": {"validate_result": 1, "last_validate": now}}
                else:
                    u = {"$set": {"validate_result": -1, "last_validate": now}}
                r = cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
                if r is None:
                    mes['message'] = '保存数据失败'
                else:
                    pass
        return mes


if __name__ == "__main__":
    # print(MySmsCaptcha.send_sms(phone="18816931927"))
    print(MySmsCaptcha.validate_code('18816931927', '5954'))
    pass