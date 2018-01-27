# -*- coding: utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.split(os.path.split(sys.path[0])[0])[0]
if project_dir not in sys.path:
    sys.path.append(project_dir)
import mongo_db
import datetime
from mongo_db import ObjectId, GeoJSON, MyDBRef, DBRef
from log_module import get_logger


"""用户模块"""


logger = get_logger()
upload_dir_path = os.path.join(sys.path[0], "static", 'upload')
if not os.path.exists(upload_dir_path):
    os.makedirs(upload_dir_path)


def allow_file(file_name: str) -> bool:
    """
    根据文件名检测是不是合法的上传图片,合法返回True
    :param file_name: 不包含路径的文件名
    :return: bool
    """
    types = ('png', 'jpg', 'jpeg', 'gif')
    if not isinstance(file_name, str):
        ms = "文件名必须是字符串"
        logger.exception(ms)
        raise ValueError(ms)
    else:
        a_list = file_name.split(".")
        if len(a_list) < 2:
            ms = "错误的文件名:{}".format(file_name)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            end = a_list[-1]
            if end.lower() in types:
                return True
            else:
                return False


class User(mongo_db.BaseDoc):
    _table_name = "user_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['user_phone'] = str  # 手机号码, 唯一
    type_dict['real_name'] = str  # 真实名字
    type_dict['user_name'] = str  # 用户名,唯一
    type_dict['user_password'] = str  # 用户密码
    type_dict['create_date'] = datetime.datetime  # 创建日期

    def __init__(self, **kwargs):
        ms = "创建用户失败,{}"
        if "user_phone" not in kwargs:
            ms = ms.format("user_phone必须")
            logger.exception(ms)
            raise ValueError(ms)
        else:
            user_phone = kwargs['user_phone']
            if not mongo_db.check_phone(user_phone):
                ms = ms.format("{}不是合法的手机号码".format(user_phone))
                logger.exception(ms)
                raise ValueError(ms)
        if "user_name" not in kwargs:
            kwargs['user_name'] = kwargs['user_phone']
        if "real_name" not in kwargs:
            kwargs['real_name'] = ''
        if "user_password" not in kwargs:
            pwd = mongo_db.generator_password(kwargs['user_phone'][(len(kwargs['user_phone']) - 6):])
            kwargs['user_password'] = pwd
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(User, self).__init__(**kwargs)

    @classmethod
    def validate_identity_cls(cls, **kwargs) -> dict:
        """
        验证用户身份,常用于用户登录.用于验证,必须是唯一性的东西,比如_id, user_phone, user_name等.
        :param kwargs: ["_id","user_phone","user_name",.....]
        :return: {"message":"success","data":{"_Id":......}}
        """
        columns = ["_id", "user_phone", "user_name"]
        message = {"message": "success"}
        arg_length = len(kwargs)
        if arg_length != 2:
            message['message'] = "必须2个参数,获得了{}个参数".format(arg_length)
        elif "user_password" not in kwargs:
            message['message'] = "参数:user_password 必须"
        else:
            user_password = kwargs.pop("user_password")
            print(kwargs)
            key = list(kwargs.keys())[0]
            val = kwargs[key]
            if key not in columns:
                message['message'] = "验证机制必须是以下几种:{}".format(columns)
            else:
                args = {key: val, "user_password": user_password}
                instance = cls.find_one(**args)
                if instance is None:
                    message['message'] = "用户尚未注册或启用"
                else:
                    message['data'] = instance.to_flat_dict()
        return message

    @classmethod
    def get_upload_dir_path(cls, upload_type: str = "image", user_id: str = None) -> str:
        """
        获取长传文件的根目录
        :param upload_type: 文件类型,默认是图片
        :param user_id: 用户id
        :return: 文件路径
        """
        if user_id is None:
            ms = "用户id不能为None"
            logger.exception(ms)
            raise ValueError(ms)
        else:
            user_id = str(user_id)
            oid = None
            try:
                oid = ObjectId(user_id)
            except Exception as e:
                logger.exception(e)
                raise e
            finally:
                if isinstance(oid, ObjectId):
                    instance = User.find_by_id(oid)
                    if isinstance(instance, User):
                        path = os.path.join(upload_dir_path, upload_type, user_id)
                        if not os.path.exists(path):
                            os.makedirs(path)
                        return path
                    else:
                        ms = "user_id找不到对应的用户"
                        logger.exception(ms)
                        raise ValueError(ms)
                else:
                    pass

    @classmethod
    def get_file_space(cls, user_id: str) -> list:
        """
        获取用户的文件列表
        :param user_id: 用户id
        :return: list
        """
        user_path = cls.get_upload_dir_path(user_id=user_id)
        name_list = os.listdir(user_path)
        name_list = [os.path.join(user_path, x).split(sys.path[0])[-1] for x in name_list if allow_file(x)]
        return name_list


if __name__ == "__main__":
    user = User(user_phone="15618317376")
    user.save()
    pass