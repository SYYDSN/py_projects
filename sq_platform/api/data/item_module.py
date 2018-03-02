# -*- coding:utf-8 -*-
import sys
import os
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if project_dir not in sys.path:
    sys.path.append(project_dir)
import mongo_db
from bson.objectid import ObjectId
import datetime
from log_module import get_logger
from bson.son import SON
import time
import re
import math
import json
import random
from uuid import uuid4
import amap_module
from error_module import RepeatError, pack_message
from amap_module import *
import mail_module
import threading


"""为防止循环引用,不要引用tools_module模块"""
"""定义gps和传感器数据模型及相关方法"""
"""定义用户的模型及相关方法"""

logger = get_logger()
MyDBRef = mongo_db.MyDBRef
DBRef = mongo_db.DBRef
cache = mongo_db.cache
GeoJSON = mongo_db.GeoJSON
insert_queue_lock = threading.Lock()

"""定义用户的模型及相关方法"""

image_patch = "static/image/head_img/"



class Log(mongo_db.BaseDoc):
    """记录日志信息"""
    _table_name = "log_record_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # 记录，是一个ObjectId对象，唯一
    type_dict['log_type'] = str  # 日志类型
    type_dict['create_date'] = datetime.datetime  # 记录时间
    type_dict['info_dict'] = dict  # 日志内容

    @classmethod
    def record(cls, log_type: str, info_dict: dict) -> None:
        """
        记录单个日志,所有添加日志都推荐用此方法
        :param log_type: 日志类型,字符串
        :param info_dict:  日志的内容字典.
        :return:
        """
        kw = {
            "log_type": log_type, "info_dict": info_dict,
            "create_date": datetime.datetime.now()
        }
        log = cls(**kw)
        log.save()


class LoginRecord(mongo_db.BaseDoc):
    """用户登录的记录"""
    _table_name = "login_record_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # 记录，是一个ObjectId对象，唯一
    type_dict['user_id'] = DBRef  # 用户idDBRef对象  
    type_dict['login_type'] = str  # 登录类型,可以是 web / app 默认 web
    type_dict['ip'] = str  # 用户登陆时的ip
    type_dict['user_agent'] = str  # 用户登录时的浏览器信息如果是app登录,就没有这一项信息
    type_dict['login_date'] = datetime.datetime  # 登录时间

    def __init__(self, **kwargs):
        if "login_type" not in kwargs:
            kwargs['login_type'] = "web"
        if "user_agent" not in kwargs:
            kwargs['user_agent'] = ""
        if "app_version" not in kwargs:
            kwargs['app_version'] = ""
        super(LoginRecord, self).__init__(**kwargs)


class User(mongo_db.BaseDoc):
    """用户类"""
    _table_name = "user_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # 用户id，是一个ObjectId对象，唯一
    type_dict['user_name'] = str  # 登录名，唯一
    type_dict['user_password'] = str
    type_dict['head_img_url'] = str  # 头像路径
    type_dict['real_name'] = str  # 真实姓名
    type_dict['nick_name'] = str  # 昵称
    type_dict['gender'] = str  # 性别 男性，女性
    type_dict['age'] = int  # 年龄
    type_dict['driving_experience'] = int  # 驾龄 单位 年
    type_dict['country'] = str  # 国家
    type_dict['province'] = str  # 省份
    type_dict['city'] = str  # 城市
    type_dict['address'] = str  # 地址
    type_dict['zip_code'] = str  # 邮编
    type_dict['email'] = str  # 电子邮件，可用来登录，唯一 暂时未实现
    type_dict['phone_num'] = str  # 手机号码，可用来登录，唯一
    type_dict['birth_date'] = datetime.date  # 出生日期
    type_dict['description'] = str  #
    type_dict['emergency_contact'] = str  # 紧急联系人(姓名)
    type_dict['emergency_phone'] = str  # 紧急联系号码
    """
    驾驶证信息部分,驾驶证和用户有一一对应的关系.所以需要直接存储在对象中.
    """
    type_dict['license_id'] = str                          # 驾驶证id
    type_dict['license_image_url'] = str                   # 驾驶证照片
    type_dict['license_class'] = str                       # 驾驶证类型,准驾车型
    type_dict['first_issued_date'] = datetime.datetime     # 首次领证日期
    type_dict['valid_date'] = datetime.datetime            # 驾驶证有效期
    """
    有关行车证信息部分,由于行车证和用户没有意义对应关系.
    由于业务逻辑上个人可能创建和自己不相干的车牌的查询器，所以这个cars失去了业务逻辑上的意义。
    在车牌信息用，有一个user_id参数。用于确认车牌信息的使用者。
    车牌号码和使用者id构成了联合唯一主键。  
    """
    type_dict['phones'] = list      # 名下手机的的id，是一个DBRef的List对象，默认为空  对应phone_device_info表
    type_dict['user_status'] = int  # 用户状态，1表示可以登录，0表示禁止登录
    type_dict['wx_id'] = str        # 微信id
    type_dict['weibo_id'] = str     # 微博id
    type_dict['create_date'] = datetime.datetime  # 用户的注册/创建日期
    type_dict['app_version'] = str  # 用户当前的app信息
    type_dict['last_update'] = datetime.datetime  # 用户当前的app信息

    def __init__(self, **kwargs):
        if "user_name" not in kwargs:
            kwargs['user_name'] = kwargs['phone_num']
        if "country" not in kwargs:
            kwargs['country'] = "中国"
        if "user_password" not in kwargs:
            phone_num = kwargs['phone_num']
            user_password = mongo_db.generator_password(phone_num[(len(phone_num) - 6):])
            kwargs['user_password'] = user_password
        if "head_img_url" not in kwargs:
            kwargs['head_img_url'] = "static/image/head_img/default_01.png"
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(User, self).__init__(**kwargs)

    def my_cars(self) -> list:
        """
        获取车辆信息对应car_license_info表
        :return: 车辆信息的DBRef的List对象
        """
        cars = self.get_attr("cars")
        return cars

    def get_archives(self) -> dict:
        """
        获取个人档案,可以看作是超详细版的个人资料,主要是辅助显示个人详细信息
        :return:
        """
        if "phones" in self.__dict__:
            phones = self.__dict__.pop("phones")
            phones = [phone.id for phone in phones]
            filter_dict = {"_id": {"$in": phones}}
            phones = PhoneDevice.find_plus(filter_dict=filter_dict)
            phones.sort(key=lambda obj: obj.get_id().generation_time, reverse=True)  # 按照_id保存的时间排序,倒序
            phones = [phone.to_flat_dict() for phone in phones]
        else:
            phones = list()
        user_id = self.get_id()
        filter_dict = {"user_id": user_id}
        """查相关的行驶证信息"""
        car_licenses = CarLicense.find_plus(filter_dict=filter_dict)
        car_licenses.sort(key=lambda obj: obj.get_id().generation_time, reverse=True)  # 按照_id保存的时间排序,倒序
        car_licenses = [x.to_flat_dict() for x in car_licenses]
        archives = self.to_flat_dict()
        archives['phones'] = phones
        archives['car_licenses'] = car_licenses
        return archives

    def get_driving_license(self) -> dict:
        """
        获取驾照相关信息.返回的字段格式是参考App端的要求决定的.
        :return: 数据字典,没有经过json转换.
        """
        data = {
            "_id": self.get_id(),                                      # 和用户信息共享一个id
            "license_id": self.get_attr("license_id"),                 # 驾驶证id
            "license_class": self.get_attr("license_class"),           # 驾驶证类型/准驾车型
            "address": self.get_attr("address"),                       # 地址
            "image_url": "static/image/license_image/example.png" if
            self.get_attr("license_image_url") is None else
            self.get_attr("license_image_url"),                        # 驾驶证图片地址
            "official_name": self.get_attr("real_name"),               # 名字
            "gender": self.get_attr("gender"),                         # 性别
            "nationality": self.get_attr("country"),                   # 国家
            "birth_date": self.get_attr("birth_date"),                 # 出生日期
            "first_issued_date": self.get_attr("first_issued_date"),   # 首次领证日期
            "valid_date": self.get_attr("valid_date")                  # 驾照有效期
        }
        return data

    def update_driving_license(self, **kwargs) -> dict:
        """
        更新驾照相关信息.参数的日期可以是时间
        :return: 消息字典,比如{'message':'success'}
        """
        message = {"message": "success"}
        if "_id" in kwargs:
            kwargs.pop("_id")

        # 合法的属性名
        attr_names = [
            "license_id",              # 驾驶证id
            "license_class",           # 驾驶证类型/准驾车型
            "address",                 # 地址
            "image_url",               # 驾驶证图片地址
            "license_image_url",       # 驾驶证图片地址
            "official_name",           # 名字
            "real_name",               # 名字
            "gender",                  # 性别
            "nationality",             # 国家
            "country",                 # 国家
            "birth_date",              # 出生日期
            "first_issued_date",       # 首次领证日期
            "valid_date"               # 驾照有效期

        ]
        # 转换字典
        transform_dict = {"image_url": "license_image_url", "official_name": "real_name", "nationality": "country"}
        for k, v in kwargs.items():
            if k in attr_names:
                k = k if transform_dict.get(k) is None else transform_dict.get(k)
                if k in ['valid_date', 'first_issued_date', 'birth_date']:
                    val = None
                    try:
                        the_datetime = mongo_db.get_datetime_from_str(v)
                        if isinstance(the_datetime, datetime.datetime):
                            val = mongo_db.round_datetime(the_datetime)
                        else:
                            val = None
                    except TypeError as e:
                        logger.exception("User.update_driving_license TypeError")
                        print(e)
                    except Exception as e:
                        logger.exception("User.update_driving_license OtherError")
                        print(e)
                    finally:
                        if val is None:
                            ms = '参数:{}的值 {}非法.'.format(k, v)
                            logger.exception(ms)
                            print(ms)
                            message['message'] = ms
                            pass
                        else:
                            self.set_attr(k, val)
                else:
                    self.set_attr(k, v)
            else:
                pass
        try:
            self.save()
        except Exception as e:
            message['message'] = "实例保存失败"
            ms = "User.update_driving_license Error, args={}".format(kwargs)
            logger.exception(ms)
            print(e)
        finally:
            return message

    @classmethod
    def find_driving_license(cls, user_id: (str, ObjectId)) -> dict:
        """
        根据id查找相关人员的驾驶证信息.
        :param user_id: 用户id
        :return: 经过json化的数据字典.
        """
        res = cls.find_by_id(user_id)
        if res is None:
            data = None
        else:
            data = {
                "_id": str(res.get_id()),  # 和用户信息共享一个id
                "license_id": res.get_attr("license_id"),                 # 驾驶证id
                "license_class": res.get_attr("license_class"),           # 驾驶证类型/准驾车型
                "address": res.get_attr("address"),                       # 地址
                "image_url": "static/image/license_image/example.png" if
                res.get_attr("license_image_url") is None else
                res.get_attr("license_image_url"),                        # 驾驶证图片地址
                "official_name": res.get_attr("real_name"),               # 名字
                "gender": res.get_attr("gender"),                         # 性别
                "nationality": res.get_attr("country"),                   # 国家
                "birth_date": res.get_attr("birth_date"),                 # 出生日期
                "first_issued_date": res.get_attr("first_issued_date"),   # 首次领证日期
                "valid_date": res.get_attr("valid_date")                  # 驾照有效期
            }
            data = {k: (v.strftime("%F") if isinstance(v, datetime.datetime) else v) for k, v in data.items() if v is not None}
        return data

    @classmethod
    def set_driving_license(cls, **kwargs) -> dict:
        """
        根据用户id,设置一个用户的驾驶证信息
        :param kwargs: 必须包含用户id
        :return: 消息字典,比如{'message':'success'}
        """
        message = {"message": "success"}
        if isinstance(kwargs, dict):
            user_id = None
            try:
                user_id = kwargs.pop("user_id")
            except KeyError as e:
                pass
            finally:
                if user_id is None:
                    message['message'] = "用户id不能为None"
                else:
                    user = cls.find_by_id(user_id)
                    if isinstance(user, cls):
                        message = user.update_driving_license(**kwargs)
                    else:
                        message['message'] = "user_id错误"
        else:
            message['message'] = "参数集必须是dict"
        return message


    @classmethod
    def get_all_user_id(cls) -> list:
        """
        获取全部的user_id,返回OjectId的数组。
        :return: OjectId的数组。
        """
        all_user = User.find_plus(filter_dict={})
        all_user_id = [user.get_id() for user in all_user if len(user.get_attr("phone_num")) >= 11]
        return all_user_id

    @classmethod
    def get_all_user_dbref(cls) -> list:
        """
        获取全部的user_id,返回DBRef的数组。
        :return: DBRef的数组。
        """
        all_user = User.find_plus(filter_dict={})
        all_user_dbref = [user.get_dbref() for user in all_user if len(user.get_attr("phone_num")) >= 11]
        return all_user_dbref

    @classmethod
    def sync_app_version(cls, user_id: ObjectId = None) -> None:
        """
        同步版本信息，此方法很少使用。
        :return:
        """
        if not user_id:
            filter_dict = {}
        else:
            filter_dict = {"_id": user_id}
        all_user = User.find_plus(filter_dict=filter_dict, to_dict=False)
        for user in all_user:
            if len(user.get_attr("phone_num")) < 11:
                pass
            else:
                user_id = user.get_dbref()
                filter_dict = {"user_id": user_id}
                sort_dict = {"time": -1}
                b = datetime.datetime.now()
                result = GPS.find_one_plus(filter_dict=filter_dict, sort_dict=sort_dict)
                e = datetime.datetime.now()
                print((e - b).total_seconds())
                if result is not None:
                    key = "app_version"
                    user_app_version = user.get_attr(key)
                    last_update = user.get_attr("time")
                    app_version = 'too old' if result.get(key) is None else result.get(key)
                    if user_app_version is None or user_app_version != app_version:
                        user.set_attr(key, app_version)
                        user.set_attr("last_update", last_update)
                    else:
                        pass
                    user.save()

    @classmethod
    def app_version_list(cls) -> list:
        """
        获取所有用户的app版本信息
        :return:
        """
        all_user = User.find_plus(filter_dict={}, to_dict=False)
        result_list = [user.to_flat_dict() for user in all_user if len(user.get_attr("phone_num")) >= 11]
        return result_list

    @classmethod
    def get_archives_cls(cls, user_id: (str, ObjectId, list)) -> (dict, list):
        """
        获取用户档案,get_archives函数的类方法实现.
        :param user_id:一个用户id或者一组用户id
        :return: 一个用户的字典或者一组用户的字典的list
        """
        if isinstance(user_id, list):
            """一组用户id"""
            result = list()
            if len(user_id) == 0:
                ms = "{} Error:用户id组不能为空".format(sys._getframe().f_code.co_name)
                logger.info(ms)
                raise ValueError(ms)
            else:
                users = [cls.find_by_id(x) for x in user_id if x is not None]
                result = [user.get_archives() for user in users if isinstance(user, cls)]
        else:
            """单个用户"""
            result = dict()
            if user_id is None:
                ms = "{} Error:用户id不能为None".format(sys._getframe().f_code.co_name)
                raise ValueError(ms)
            else:
                user = cls.find_by_id(user_id)
                if isinstance(user, cls):
                    result = user.get_archives()
                else:
                    ms = "{} Error: 错误的用户id:{}".format(sys._getframe().f_code.co_name, user_id)
                    logger.info(ms)
                    raise ValueError(ms)
        return result

    @classmethod
    def repair_last_update(cls) -> None:
        """
        修正用户的最后一次上传时间,耗时，不常用
        :return:
        """
        all_user = User.find_plus(filter_dict={})
        all_user = [user for user in all_user if len(user.get_attr("phone_num")) >= 11]
        for user in all_user:
            user_id = user.get_dbref()
            filter_dict = {"user_id": user_id}
            sort_dict = {"time": -1}
            recode = GPS.find_one_plus(filter_dict=filter_dict, sort_dict=sort_dict)
            if recode is not None:
                user.set_attr("last_update", mongo_db.get_datetime_from_str(recode['time']))
                user.save()
                print(user.get_attr("phone_num"), user.get_attr("last_update"))

    @classmethod
    def add_phone_device(cls, user_id: (str, ObjectId, DBRef, MyDBRef), dbref_obj: mongo_db.DBRef) -> bool:
        """
        插入一个移动设备(手机)的dbref信息。如果存在，那就pass，不存在就插入
        :param user_id: 用户id
        :param dbref_obj: 移动设备的dbref
        :return: True/False
        """
        obj = None
        if isinstance(user_id, (DBRef, MyDBRef)):
            obj = User.get_instance_from_dbref(user_id)
        elif isinstance(user_id, (str, ObjectId)):
            obj = cls.find_by_id(user_id)
        else:
            raise TypeError("错误的user_id类型， {}".format(user_id))
        result = True
        if obj is None:
            result = False
        else:
            if hasattr(obj, 'phones'):
                phones = obj.phones
                if isinstance(phones, list):
                    pass
                else:
                    print(phones)
                    warning_str = "phones类型错误，期待一个list，得到一个{}".format(type(phones))
                    raise TypeError(warning_str)
            else:
                phones = list()
            dbref_ids = [x.id for x in phones]
            if dbref_obj.id in dbref_ids:
                pass
            else:
                phones.append(dbref_obj)
                obj.__dict__['phones'] = phones
                try:
                    obj.save()
                except Exception as e:
                    result = False
                    raise e
        return result

    @classmethod
    def register(cls, **kwargs):
        """用户注册"""
        if "head_img_url" not in kwargs:
            head_img_file_name = "default_0{}.png".format(random.randint(1, 3))
            kwargs['head_img_url'] = image_patch + head_img_file_name
        obj = User(**kwargs)
        func_name = sys._getframe().f_code.co_name
        event_desc = "用户注册，参数：{} 注册结果：".format(str(kwargs))
        event_date = datetime.datetime.now()

        args = {"event_type": func_name, "event_description": event_desc,
                "event_date": event_date}
        try:
            _id = obj.insert()
            obj._id = _id
            args['user_id'] = _id
            event_desc = event_desc + "成功"
            args['event_description'] = event_desc
        except ValueError as e:
            event_desc = event_desc + str(e)
            args['event_description'] = event_desc
            obj = None
            raise e
        finally:
            EventRecord.save(**args)
            return obj

    @classmethod
    def user_login(cls, **kwargs):
        """用户登录"""
        result = None
        user = User.find_one(**kwargs)
        """记录事件"""
        func_name = sys._getframe().f_code.co_name
        event_desc = "用户登录，登录参数：{}".format(str(kwargs))
        event_date = datetime.datetime.now()
        args = {"event_type": func_name, "event_description": event_desc,
                "event_date": event_date}

        if isinstance(user, User):
            user_id = user._id
            token = AppLoginToken.create_token(user_id)
            result = token
            args = {"event_type": func_name, "event_description": event_desc,
                    "event_date": event_date, "user_id": user_id}
        else:
            pass
        EventRecord.save(**args)
        return result

    @classmethod
    def iot_user_login(cls, **kwargs):
        """物联网用户登录，会检查是否注册，然后自动注册"""
        result = None
        user = User.find_one(**kwargs)
        """记录事件"""
        func_name = sys._getframe().f_code.co_name
        event_desc = "物联网用户登录，登录参数：{}".format(str(kwargs))
        event_date = datetime.datetime.now()
        args = {"event_type": func_name, "event_description": event_desc,
                "event_date": event_date}
        if user is None:
            """说明没注册"""
            kwargs['description'] = "物联网卡用户"
            user = User.insert_and_return_instance(**kwargs)
        if isinstance(user, User):
            user_id = user._id
            token = AppLoginToken.create_token(user_id)
            result = {"data": user.to_flat_dict(), "token": token}
            args = {"event_type": func_name, "event_description": event_desc,
                    "event_date": event_date, "user_id": user_id}
        else:
            pass
        EventRecord.save(**args)
        return result

    @classmethod
    def user_logout(cls, user_id):
        """用户登出"""
        ses = mongo_db.get_conn(AppLoginToken.get_table_name())
        result = ses.find_one({"user_id": user_id})
        """记录事件"""
        func_name = sys._getframe().f_code.co_name
        event_desc = "{}注销".format(user_id)
        event_date = datetime.datetime.now()
        args = {"event_type": func_name, "event_description": event_desc,
                "event_date": event_date}
        if result is not None:
            args = {"event_type": func_name, "event_description": event_desc,
                    "event_date": event_date, "user_id": result['user_id']}
        EventRecord.save(**args)
        """删除token"""
        if result is not None:
            ses.delete_one({"_id": result.get("_id")})
            mongo_db.cache.delete(result['token'])
        else:
            raise ValueError("{} 没有对应的登录记录".format(user_id))

    @classmethod
    def get_info_dict_by_token(cls, token):
        """
        通过token获取用户信息，
        :param token: 用户token
        :return: 字典
        """
        message = {"message": "success"}
        result = AppLoginToken.get_id_by_token(token)
        if result['message'] != "success":
            message = result
        else:
            obj = cls.find_one(_id=result['user_id'])
            if obj is None:
                message = pack_message(message, 3004, token=token)
            else:
                message['data'] = obj.to_flat_dict()
        return message

    @classmethod
    def get_info_dict_by_id(cls, user_id):
        """
        通过user_id获取用户信息，
        :param user_id: user_id
        :return: 字典
        """
        id = mongo_db.get_obj_id(user_id)
        message = {"message": "success"}
        obj = cls.find_by_id(id)
        if obj is None:
            message = pack_message(message, 3004, user_id=user_id)
        else:
            message['data'] = obj.to_flat_dict()
        return message


class EventRecord(mongo_db.BaseDoc):
    """事件记录,用于记录用户的各种重要事件，比如登录，注册，注销"""
    _table_name = "event_record"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # 用户id，是一个ObjectId对象，唯一
    type_dict['event_type'] = str  # 用户事件类型，一般是函数名
    type_dict['user_id'] = ObjectId  # 事件关联的用户id
    type_dict['truck_id'] = ObjectId  # 事件关联的卡车id
    type_dict['event_description'] = str  # 事件描述
    type_dict['event_date'] = datetime.datetime  # 事件描述

    @classmethod
    def save(cls, **kwargs):
        """保存对象"""
        obj = cls(**kwargs)
        return obj.insert()


class AppLoginToken(mongo_db.BaseDoc):
    """记录用户的登录，生成一个token，给app使用"""
    _table_name = "app_login_token"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['user_id'] = ObjectId  # 用户id，是一个ObjectId对象，唯一
    type_dict['token'] = str  # 用户登录标示，登录过的app用户
    type_dict['create_date'] = datetime.datetime  # token有效的开始/创建日期
    type_dict['end_date'] = datetime.datetime  # token有效的截止日期

    @classmethod
    def delete(cls, user_id):
        """
        删除一个token。注意，此方法并不清空cache里token
        :param user_id: 用户id。
        :return: int 一个删除的计数器
        """
        if isinstance(user_id, ObjectId):
            pass
        else:
            try:
                user_id = ObjectId(user_id)
            except Exception as e:
                print(e)
                raise ValueError("{} 不能被转换为ObjectId".format(user_id))
        ses = mongo_db.get_conn(cls._table_name)
        result = ses.delete_many({"user_id": user_id})
        return result.deleted_count

    @classmethod
    def check_token(cls, token):
        """
        比较token
        :param token: 登录标示
        :return: 返回一个User对象实例或者None
        """
        result = None
        token_obj = cls.find_one(token=token)
        if token_obj is None:
            return result
        else:
            try:
                user_id = token_obj.user_id
                user_obj = User.find_by_id(user_id)
                if user_obj is None:
                    warning_str = "id {} 没有对应的用户".format((str(user_id)))
                    print(warning_str)
                return user_obj
            except AttributeError as e:
                print(e)
                raise AttributeError("token对象：{} 没有user_id属性".format(token_obj.to_flat_dict()))
            finally:
                return result

    @classmethod
    def create_token(cls, user_id):
        """获取一个token"""
        if isinstance(user_id, ObjectId):
            pass
        else:
            try:
                user_id = ObjectId(user_id)
            except Exception as e:
                print(e)
                raise ValueError("{} 不能被转换为ObjectId".format(user_id))
        token = uuid4().hex
        end_date = mongo_db.get_datetime(182, False)
        args = {"user_id": user_id, "create_date": mongo_db.get_datetime(0, False),
                "end_date": end_date, "token": token}
        old = AppLoginToken.find_one(user_id=user_id)  # 以前的token
        token_obj = cls(**args)
        """删除以前的"""
        AppLoginToken.delete(user_id)
        """插入新的"""
        insert_id = token_obj.insert()
        if insert_id:
            cache = mongo_db.cache
            cache.set(token, end_date, timeout=60 * 24)
            if old is not None:
                cache.delete(old.token)
            return token
        else:
            return None

    @classmethod
    def get_id_by_token(cls, token, force=False):
        """通过token获取用户id，返回包含ObjectId的字典对象
        参数force的意思是指是否过期也返回user_id
        """
        message = {"message": "success"}
        result = cls.find_one(token=token)
        if result is None:
            message = pack_message(message, 3006, token=token)
        else:
            if result.end_date < datetime.datetime.now() and not force:
                message = pack_message(message, 3005, token=token)
            else:
                message['user_id'] = result.user_id
        return message

class UserLicenseRelation(mongo_db.BaseDoc):
    """关系表,记录用户和行车证/车辆的对应关系"""
    _table_name = "user_license_relation"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict['user_id'] = DBRef  # 用户id,是指开这辆车的司机,指向user_info表
    type_dict['license_id'] = DBRef   # 驾驶证id,指向car_license_info表
    type_dict['create_date'] = datetime.datetime  # 关系的建立时间
    type_dict['end_date'] = datetime.datetime  # 关系的终结时间

    @classmethod
    def rebuild(cls):
        """从旧的行车证/用户的关联模式转换到 行车证/关系/用户模式,仅仅在模型改变时使用,一次性转换函数"""
        cars = CarLicense.find_plus(filter_dict={"user_id": {"$ne": None}})
        relations = [{
            "user_id": User.find_by_id(car.get_attr("user_id")).get_dbref(),
            "license_id": car.get_dbref(),
            "create_date": car.get_attr("create_date")
        } for car in cars]
        cls.insert_many(relations)

class CarLicense(mongo_db.BaseDoc):
    """行车证"""
    _table_name = "car_license_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    """
    考虑到车队的车
    1.可能换人开,
    2.app在上传行车证图片的时候会先创建一个临时行车证记录,这和时候的和plate_number为空.而且这种记录可能有多个.
    所以用户id 和plate_number的联合主键因该删除
    """
    type_dict["user_id"] = ObjectId  # 注意,这里是创建者的id
    type_dict["permit_image_url"] = str  # 车辆照片url
    type_dict["plate_number"] = str  # 车辆号牌, 英文字母必须大写,允许空,不做唯一判定
    type_dict["car_type"] = str  # 车辆类型  比如 重型箱式货车
    type_dict["owner_name"] = str  # 车主姓名/不一定是驾驶员
    type_dict["address"] = str  # 地址
    type_dict["use_nature"] = str  # 使用性质
    type_dict["car_model"] = str  # 车辆型号  比如 一汽解放J6
    type_dict["vin_id"] = str  # 车辆识别码/车架号的后六位 如果大于6未，查询违章的时候就用后6位查询
    type_dict["engine_id"] = str  # 发动机号
    type_dict["register_city"] = str  # 注册城市,不必填,默认查归属地
    type_dict["register_date"] = datetime.date  # 注册日期
    type_dict["issued_date"] = datetime.date  # 发证日期
    type_dict["create_date"] = datetime.datetime  # 创建日期

    def __init__(self, **kwargs):
        """因为牵扯到和用户的关系,此方法不应该直接调用"""
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        if "plate_number" in kwargs:
            """plate_number为空是在仅仅上传了行车证照片，还没有输入车牌信息的情况。一个用户只允许一条这样的记录"""
            kwargs['plate_number'] = kwargs['plate_number'].upper()
        if "user_id" not in kwargs:
            try:
                raise ValueError("user_id不能为空")
            except ValueError as e:
                ms = "创建CarLicense实例失败，user_id缺失 kwargs={}".format(kwargs)
                logger.exception(ms)
                raise e
        print(kwargs)
        super(CarLicense, self).__init__(**kwargs)

    @classmethod
    def instance(cls, **kwargs) -> (object, None):
        """
        创建实例请用此方法而不是__init__方法,
        如果已存在
        :param kwargs:
        :return: 返回实例或者None
        """
        try:
            obj = cls(**kwargs)
            license_id = obj.save()
        except Exception as e:
            ms = "instance Error! args={}".format(kwargs)
            logger.exception(ms)
        finally:
            result = None
            if isinstance(license_id, ObjectId):
                """行车证创建成功,可以创建用户和行车证的关系了"""
                relation = {
                    "license_id": DBRef(collection="car_license_info", id=license_id, database="platform_db"),
                    "user_id": DBRef(collection="user_info", id=obj.get_attr("user_id"), database="platform_db")
                }
                """检查是否已有对象"""
                find_obj = UserLicenseRelation.find_one_plus(filter_dict=relation)
                if find_obj is None:
                    relation['create_date'] = datetime.datetime.now()
                    UserLicenseRelation.insert_one(**relation)
                else:
                    pass
                result = obj
                return result

    @classmethod
    def get_usable_license(cls, user_id: (str, ObjectId, DBRef, MyDBRef)) -> list:
        """
        获取指定用户的可用行车证,行车证的可用状态是指行车证对应的UserLicenseRelation实例存在,并且
        其end_date为null,不存在或者比现在的时间更靠后的状态.
        :param user_id: 用户id
        :return: CarLisence实例的数组
        """
        if isinstance(user_id, (MyDBRef, DBRef)):
            pass
        elif isinstance(user_id, ObjectId):
            user_id = DBRef(collection=User.get_table_name(), id=user_id, database=mongo_db.db_name)
        elif isinstance(user_id, str):
            user_id = mongo_db.get_obj_id(user_id)
            user_id = DBRef(collection=User.get_table_name(), id=user_id, database=mongo_db.db_name)
        else:
            ms = "CarLicense.get_usable_license Error,错误的user_id类型: {}".format(type(user_id))
            logger.exception(ms)
        if isinstance(user_id, (DBRef, MyDBRef)):
            result = []
            filter_dict = {
                "user_id": user_id,
                "$or": [
                    {"end_date":{"$exists": False}},
                    {"end_date":None},
                    {"end_date":{"$lte": datetime.datetime.now()}}
                ]
            }
            sort_dict = {"create_date": -1}
            projection = ['license_id']
            """查询可用的行车证的id"""
            res = UserLicenseRelation.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, projection=projection)
            license_ids = [x.get_attr("license_id").id for x in res]
            if len(license_ids) == 0:
                pass
            else:
                filter_dict = {"_id": {"$in": license_ids}}
                sort_dict = {"create_date": -1}
                result = cls.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, can_json=True)
            return result
        else:
            return None

    @classmethod
    def find_one_and_delete(cls, filter_dict: dict, sort_dict: dict = None, projection: list = None,
                            instance: bool = False):
        """
        找到并删除一个对象,这是重写了父类的方法.用于在删除的时候同步终止司机和行车证的对应关系.
        :param filter_dict:  查询的条件，
        :param sort_dict: 排序的条件  比如: {"time": -1}  # -1表示倒序
        :param projection:    投影数组,决定输出哪些字段?
        :param instance: 返回的是实例还是doc对象？默认是doc对象
        :return: None, 实例或者doc对象。
        """
        result = False
        table_name = cls._table_name
        ses = mongo_db.get_conn(table_name=table_name)
        if sort_dict is not None:
            sort_list = [(k, v) for k, v in sort_dict.items()]  # 处理排序字典.
        else:
            sort_list = None
        args = {
            "filter": filter_dict,
            "sort": sort_list,  # 可能是None,但是没问题.
            "projection": projection
        }
        args = {k: v for k, v in args.items() if v is not None}
        res = ses.find_one_and_delete(**args)
        if res is None:
            """删除失败"""
            pass
        else:
            """删除成功,接着删除对应的UserLicenseRelation实例"""
            license_id = DBRef(id=res['_id'], collection=table_name, database="platform_db")
            user_id = DBRef(id=res['user_id'], collection=User.get_table_name(), database="platform_db")
            filter_dict = {"license_id": license_id, "user_id": user_id}
            update_dict = {"$set": {"end_date": datetime.datetime.now()}}
            res = UserLicenseRelation.find_one_and_update_plus(filter_dict=filter_dict, update_dict=update_dict)
            if res is None:
                """删除关系失败"""
                pass
            else:
                result = True
        return result

    def get_vio_query_info(self):
        """获取用于违章查询的车牌,车架号等信息,返回字典"""
        data_dict = self.__dict__
        plateNumber = "" if data_dict.get("plate_number") is None else data_dict['plate_number']
        engineNo = "" if data_dict.get("engine_id") is None else data_dict['engine_id']
        vin = "" if data_dict.get("vin_id") is None else data_dict['vin_id']
        vin = vin[-6:] if len(vin) > 6 else vin
        carType = "" if data_dict.get("car_type") is None else data_dict['car_type']
        carType = "02" if carType.find("小") != -1 or carType == "" else "01"
        args = {"plateNumber": plateNumber, "engineNo": engineNo, "vin": vin,
                "carType": carType}
        return args


def rebuild_car_license() -> None:
    """重建行车证信息，去掉重复的键值，为创建plate_number和user_id的联合唯一主键提供前提条件
        db.car_license_info.ensureIndex({"user_id":1,"plate_number":1}, {"unique":1})
    """
    from api.user.violation_module import VioQueryGenerator
    vios = VioQueryGenerator.find()
    for vio in vios:
        car_license = CarLicense.find_by_id(vio.get_attr("car_license").id)
        user_id = vio.get_attr("user_id")
        car_license.user_id = user_id
        car_license.save()


class TrafficRoute(mongo_db.BaseDoc):
    """
    交通线路类,记录车辆/物流的交通线路,
    1. 往返路线算两条不同的路线,因为往返路线可能完全不同.
    2. 起终点相同的路线也可能中间不同.
    """
    _table_name = "traffic_route_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['city_code_list'] = list  # 城市的ad_code的数组,code是int格式,2者顺序意义对应
    type_dict['city_name_list'] = list  # 城市的名字的数组,唯一主键.2者顺序意义对应
    type_dict['create_date'] = datetime.datetime  # 创建时间

    def __init__(self, **kwargs):
        if 'city_code_list' not in kwargs or 'city_name_list' not in kwargs:
            ms = "city_name_list和city_code_list都是必要参数"
            raise ValueError(ms)
        if len(kwargs['city_code_list']) == 0  or len(kwargs['city_name_list']) == 0:
            ms = "city_name_list和city_code_list长度不能为0"
            raise ValueError(ms)
        if len(kwargs['city_code_list']) != len(kwargs['city_name_list']):
            ms = "city_name_list和city_code_list长度不想等"
            raise ValueError(ms)
        if 'create_date' not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(TrafficRoute, self).__init__(**kwargs)


class RouteWeather(mongo_db.BaseDoc):
    """
    沿途天气类
    """
    _table_name = "route_weather_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['route_id'] = DBRef  # 交通线路的id,唯一.
    type_dict['city_weather'] = list  # weather实际上是个字典,字典组成的数组,顺序和线路相同.
    type_dict['create_date'] = datetime.datetime  # 创建时间

    def __init__(self, **kwargs):
        if 'create_date' not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(RouteWeather, self).__init__(**kwargs)

    @classmethod
    def get_route_weather(cls, route_id: (str, ObjectId)) -> list:
        """
        查询线路天气
        :param route_id: 线路id
        :return: 天气字典的数组
        """
        if route_id is None:
            ms = "{} Error,线路id不能为空".format(sys._getframe().f_code.co_name)
            logger.exception(ms)
            raise ValueError(ms)
        else:
            result = list()
            route = TrafficRoute.find_by_id(route_id)
            if isinstance(route, TrafficRoute):
                route_dbref = route.get_dbref()
                filter_dict = {"route_id": route_dbref}
                instance = cls.find_one_plus(filter_dict=filter_dict, instance=True)
                from_amap = False
                if isinstance(instance, cls):
                    prev = instance.get_attr("create_date")
                    now = datetime.datetime.now()
                    if(now - prev).total_seconds() < 1 * 60 * 60:  # 查询间隔1个小时
                        result = instance.get_attr("city_weather")
                    else:
                        from_amap = True
                else:
                    from_amap = True
                if from_amap:
                    """从网络查"""
                    result = list()  # 清空查询结果
                    code_list = route.get_attr("city_code_list")
                    name_list = route.get_attr("city_name_list")
                    for i, code in enumerate(code_list):
                        temp = dict()
                        weather = get_weather_by_ad_code(code, forecast=False)
                        center = get_district_info(code)
                        temp['city'] = weather['city']
                        temp['temp'] = weather['temperature']
                        temp['title'] = weather['weather']
                        temp['date'] = weather['report_time']
                        temp['lat'] = center['lat']
                        temp['lng'] = center['lng']
                        result.append(temp)
                    args = {"route_id": route_dbref, "city_weather": result, "create_date": datetime.datetime.now()}
                    instance = cls(**args)
                    try:
                        instance.save()
                    except mongo_db.DuplicateKeyError as e:
                        print(e)
                        filter_dict = {"route_id": args.pop("route_id")}
                        update_dict = {"$set": args}
                        cls.find_one_and_update_plus(filter_dict=filter_dict, update_dict=update_dict)
                else:
                    pass
            return result


class Track(mongo_db.BaseDoc):
    """
    记录路径跟踪信息，这个类是用算法计算出来的，用以重现位置和轨迹，记录原始数据库的是GPS类
    user_id+time 联合唯一索引
    """
    _table_name = "track_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['user_id'] = DBRef  # 用户id
    type_dict['pos_type'] = str  # 坐标类型，默认是amap  高德坐标 必须
    type_dict['loc'] = GeoJSON  # [经度, 纬度]
    type_dict["direction"] = float  # "和正北方向的顺时针夹角",  # 必须 当前车头方向和正北的夹角。 单位是度，浮点
    type_dict['speed'] = float  # 瞬时速度，单位km/h，
    type_dict['time'] = datetime.datetime  # 时间

    def __init__(self, **kwargs):
        if "pos_type" not in kwargs:
            pos_type = "amap"
            try:
                pos_type = kwargs.pop("amap")
            except KeyError:
                pass
            except TypeError as e:
                ms = "Error e:{}, args={}".format(e, kwargs)
                logger.exception(ms)
            finally:
                kwargs['pos_type'] = pos_type
        if "speed" in kwargs:
            kwargs['speed'] = (kwargs['speed'] * 3600) / 1000  # 传感器原始数据是米/秒，转换成公里/小时
        super(Track, self).__init__(**kwargs)

    @classmethod
    def need_save(cls, prev, cur) -> bool:
        """
        根据两个点之间的位置和时间差,计算cur这个点是否需要保存?
        :param prev: 参考的点,track或者gps
        :param cur:  当前的点,gps
        :return:
        """
        """计算各个点和参考点的位置和时间差,决定是否作为track点位置保留"""
        prev_pos = prev['loc']['coordinates']  # 上一个参考点的坐标
        curr_pos = cur['loc']['coordinates']  # 当前点的坐标
        distance = position_distance(prev_pos, curr_pos)
        try:
            interval = (cur['time'] - prev['time']).total_seconds()
        except KeyError as e:
            print(item)
            print(prev_item)
            raise e
        print(interval)
        print(cur['time'])
        print(cur['loc'])
        print(distance)
        """位移大于10米或者大于5分钟，就要记录一下"""
        if distance * 1000 >= 10 or interval > 60 * 5:
            print("需要转成track数据并记录 prev={}, cur={}, distance: {}, interval: {}".format(
                prev_pos, curr_pos, distance, interval))
            return True
        else:
            print("不需要转成track数据并记录 prev={}, cur={}, distance: {}, interval: {}".format(
                prev_pos, curr_pos, distance, interval))
            return False

    @classmethod
    def batch_create_item_from_gps(cls, gps_list: list) -> (dict, None):
        """
        批量创建一个用户的track信息。
        :param gps_list: 由GPS的doc对象组成的list
        :return: 返回一个精简化的doc对象/None
        """
        length = len(gps_list)
        if length > 0:
            res = list()
            first = gps_list[0]
            """查找早于/等于第一个gps时间的track.用做地一个比较基准点"""
            user_dbref = first['user_id']
            user_id = user_dbref.id  # ObjectId
            track_time = first['time']
            filter_dict = {"user_id": user_dbref, "time": {
                "$lte": track_time
            }}
            sort_dict = {"time": -1}
            prev_item = cls.find_one_plus(filter_dict=filter_dict, sort_dict=sort_dict, instance=False)
            print("batch_create_item_from_gps, 查找参照点{}".format(prev_item))
            if prev_item is None:
                """没有历史记录,那就把数组的第一个元素作为对照点"""
                prev_item = gps_list.pop(0)
                if len(gps_list) == 0:
                    """如果找不到历史数据并且,参数数组只有一个元素的情况,直接保存"""
                    [prev_item.pop(p) for p in ["longitude", "latitude", 'altitude', '_id']]
                    cls.insert_one(**prev_item)
                else:
                    pass
            for item in gps_list:
                """计算各个点和参考点的位置和时间差,决定是否作为track点位置保留"""
                if cls.need_save(prev_item, item):
                    prev_item = item
                    [item.pop(p) for p in ["longitude", "latitude", 'altitude', '_id']]
                    res.append(item)
                else:
                    pass

            inserted_results = cls.insert_many(res)  # 批量插入位置信息
            if len(inserted_results) > 0:
                last_inserted = inserted_results[-1]  # 返回最后的位置
                last_position = last_inserted
            else:
                last_position = None
            return last_position
        else:
            return None

    @classmethod
    def estimate_total_time_and_mileage(cls, track_list: list) -> dict:
        """
        估算一个track序列的总里程和总时间.次方法误差较大，应该被放弃
        :param track_list: Track类的doc对象.
        :return: {"total_time":total_time,"total_mileage":total_mileage} 单位分别是秒和公里.
        """
        l = len(track_list)
        length = 100
        if l <= length:
            step = 1  # 步长
        else:
            if l % length == 0:
                step = int(l / length)
                track_list = track_list[::step]
            else:
                step = math.floor(l / length)
                end_item = track_list[-1]
                track_list = track_list[::step]
                track_list.append(end_item)
        total_mileage = 0
        total_time = 0 if l < 2 else abs((mongo_db.get_datetime_from_str(track_list[0]['time']) -
                                          mongo_db.get_datetime_from_str(track_list[-1]['time'])).total_seconds())

        pos_begin = None
        for index, track in enumerate(track_list):
            if index == 0:
                pos_begin = track['loc']
            else:
                if pos_begin is None:
                    pos_begin = track['loc']
                else:
                    total_mileage += position_distance(pos_begin, track['loc'])
                    pos_begin = None
        return {"total_time": total_time, "total_mileage": total_mileage}

    @staticmethod
    def simple_doc(doc_dict: dict, ignore_columns: list = None, for_app: bool = False) -> dict:
        """
        :param doc_dict: 等待被精简的doc
        :param ignore_columns: 不需要的列名
        :param for_app: 是否是为app精简数据,app的的数据格式不太一样.
        :return: 精简过的doc
        """
        ignore_columns = ["_id", "pos_type", "speed"] if ignore_columns is None else ignore_columns
        result = mongo_db.doc_to_dict(doc_dict, ignore_columns)
        if for_app:
            loc = result['loc']
            lo = loc[0]
            la = loc[1]
            time = result['time'].split(".")[0]
            result = {"pr": "", "tm": time, "lo": lo, "la": la, "al": 0.0, "sp": 0.0, "br": 0.0}
        return result

    @classmethod
    def get_tracks_list(cls, user_id: (str, ObjectId, DBRef, MyDBRef), begin: datetime.datetime = None,
                        end: datetime.datetime = None, can_json: bool = True, for_app: bool = False) -> dict:
        """
        获取指定用户的指定时间区间的轨迹信息
        :param user_id:  用户id
        :param begin: 开始时间
        :param end: 结束时间
        :param can_json: 是否进行序列化转换？也就是转换类似ObjectId/DBRef之类的对象以适应json的方法
        :param for_app: 是否是为app准备的?app的格式和web端的不太一样.
        :return: track文档组成的dict。注意，doc做不做序列化的转换以can_json参数决定。
        """
        """先计算结束时间"""
        if end is None:
            """如果结束时间为空，那就以当前时间作为结束时间"""
            end = mongo_db.get_datetime(0, False)
        elif isinstance(end, datetime.datetime):
            pass
        else:
            raise TypeError("end类型错误,end:{}".format(end))
        """再计算开始时间"""
        if begin is None:
            """如果开始时间为空，那就根据结束时间来计算开始时间"""
            hour = end.hour
            if hour < 12:
                """如果是结束时间是在凌晨到１２点之前这段时间，那么开始时间就是２４小时之前。"""
                begin = end - datetime.timedelta(days=1)
            else:
                """超过１２点，就只查看本日的数据"""
                y, m, d = end.year, end.month, end.day
                date_str = "{}-{}-{} 0:0:0".format(y, m, d)
                begin = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        elif isinstance(begin, datetime.datetime):
            pass
        else:
            raise TypeError("begin类型错误,begin:{}".format(begin))
        if (end - begin).total_seconds() < 0:
            raise ValueError("开始时间不能晚于结束时间：begin={}, end={}".format(begin, end))
        else:
            if isinstance(user_id, str) and len(user_id) == 24:
                user_id = mongo_db.get_obj_id(user_id)
            elif isinstance(user_id, (DBRef, MyDBRef)):
                user_id = user_id.id
            elif isinstance(user_id, ObjectId):
                pass
            else:
                raise TypeError("非法的user_id, user_id={}".format(user_id))
            """可以查询数据了"""
            filter_dict = {
                "user_id.$id": user_id,
                "time": {"$gte": begin, "$lte": end}
            }
            sort_dict = {"time": 1}
            docs = cls.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, to_dict=True)
            if can_json:
                track_list = [Track.simple_doc(doc, for_app=for_app) for doc in docs]
            else:
                track_list = [doc for doc in docs]
            if not for_app:
                extend_info_dict = cls.estimate_total_time_and_mileage(track_list)
                dicts = extend_info_dict
            else:
                dicts = dict()
            dicts["track_list"] = track_list

            return dicts

    @classmethod
    def __get_last_position(cls, user: User) -> dict:
        """
        从数据库查询最新的位置信息.
        :param user: 用户
        :return: 位置信息的doc对象
        """
        if isinstance(user, User):
            user_dbref = user.get_dbref()
            filter_dict = {
                "user_id": user_dbref,
                "time": {"$lte": datetime.datetime.now()}
            }
            sort_dict = {"time": -1}
            result = cls.find_one_plus(filter_dict=filter_dict, sort_dict=sort_dict, instance=False)
            if result is None:
                result['real_name'] = user.get_attr("real_name")
                result['gender'] = user.get_attr("gender")
                result['phone_num'] = user.get_attr("phone_num")
                result['user_id'] = user.get_attr("phone_num")
            return result

    @classmethod
    def get_last_position(cls, user_id: (ObjectId, list)) -> dict:
        """
        获取一个/一组用户的最后的位置信息
        :param user_id:employee的id
        :return: dict   {user_id:{position_dict},....}
        """
        now = datetime.datetime.now()
        if isinstance(user_id, ObjectId):
            user_list = [user_id]
        elif isinstance(user_id, list):
            user_list = [x for x in user_id if isinstance(x, ObjectId)]
        else:
            raise ValueError("user_id:{}".format(user_id))
        res_dict = dict()
        for o_id in user_list:
            user = User.find_by_id(o_id)
            result = Track.__get_last_position(user)
            if result is not None:  # 如果能找到最后的点
                last_time_str = result['time']
                """转换时间，求差值"""
                last_time = mongo_db.get_datetime_from_str(last_time_str)
                if not isinstance(last_time, datetime.datetime):
                    """时间转换错误"""
                    result['time_delta'] = None
                else:
                    time_delta = int((now - last_time).total_seconds())
                    result['time_delta'] = time_delta
                result['user_id'] = user.get_attr("_id")
                result = cls.simple_doc(result, ["_id"], for_app=False)
                user = user.to_flat_dict()
                user.pop("_id")
                user.update(result)
                res_dict[str(o_id)] = user
        return res_dict


class Position(mongo_db.BaseDoc):
    """地址对应的类，记录地址和经纬度的对应关系"""
    _table_name = "position_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['pos_type'] = str  # 坐标类型，默认是amap  高德坐标 必须
    type_dict['address'] = str  # 地址
    type_dict['city'] = str  # 城市名
    type_dict['real_value'] = bool  # 经纬度是否是真实的结果？
    type_dict['longitude'] = float  # 经度
    type_dict['latitude'] = float  # 纬度
    type_dict['loc'] = GeoJSON  # 经度和维度的数组组成的地理位置信息

    def __init__(self, **kwargs):
        """
                实际构造器需要的参数：
                第一种：
                address 地址
                city 城市名
                real_value  是否是真实的结果?
                longitude  经度  浮点
                latitude  维度  浮点
                第二种：
                address 地址
                city 城市名
                real_value  是否是真实的结果?
                loc    地理位置对象 dict/GeoJSON 等同于第一种的longitude和latitude
                (注意地理位置的组成方式:
                {
                 "type":"Point/Polygon/....",
                 "coordinates":[点的坐标]
                }
                具体请参考如下站点：
                https://docs.mongodb.com/manual/reference/geojson/
                )
                第三种：
                address 地址
                city 城市名
                real_value  是否是真实的结果?
                longitude  经度  浮点
                latitude  维度  浮点
                loc    地理位置对象 dict/GeoJSON 等同于longitude和latitude
                :param kwargs:
                """
        pos_type = "amap"
        if pos_type not in kwargs:
            kwargs[pos_type] = pos_type  # 缺省地图类型
        if "longitude" in kwargs and 'latitude' in kwargs and "loc" not in kwargs:
            """coordinates里存储了经度和维度"""
            geo = [kwargs.get('longitude'), kwargs.get('latitude')]
            temp = {"type": "Point",
                    "coordinates": geo}
            kwargs['loc'] = temp
        elif ("longitude" not in kwargs or 'latitude' in kwargs) and "loc" in kwargs:
            temp = kwargs['loc']['coordinates']
            longitude = temp[0]
            latitude = temp[1]
            kwargs['longitude'] = longitude
            kwargs['latitude'] = latitude
        super(Position, self).__init__(**kwargs)

    @classmethod
    def query(cls, city: str, address: str, times: int = 0) -> dict:
        """
        根据城市名和地址查询经纬度。
        :param city: 城市名
        :param address: 地址字符串
        :param times: 递归时的次数
        :return: 经纬度的字典。
        """
        query_dict = {"city": city, "address": address}
        obj = cls.find_one(**query_dict)
        if obj is None:
            """如果数据库没有对应的数据，就检查一下是否有人已经在查询了"""
            query_result = query_geo_coordinate(**query_dict)
            if query_result is None:
                """已经有人在查询了，那就等待"""
                times += 1
                time.sleep(times * 0.2)
                res_dict = cls.query(city, address, times)
            else:
                obj = cls.insert_and_return_instance(**query_result)
                res_dict = {"longitude": obj.longitude, "latitude": obj.latitude}
        else:
            res_dict = {"longitude": obj.longitude, "latitude": obj.latitude}
        return res_dict


class GPS(mongo_db.BaseDoc):
    """gps信息类
    需要一个2dsphere索引的支持
    loc  2dshere 索引
    user_id+time  联合唯一索引
    time 的一个倒序索引，用以提高查询速度
    """
    _table_name = "gps_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['pos_type'] = str  # 坐标类型，默认是amap  高德坐标 必须
    type_dict['speed'] = float  # 速度 单位 m/s
    type_dict['user_id'] = DBRef  # 用户id
    type_dict['time'] = datetime.datetime  # 时间
    type_dict['altitude'] = float  # 海拔
    type_dict['longitude'] = float  # 经度
    type_dict['latitude'] = float  # 纬度
    type_dict['loc'] = GeoJSON  # 经度和维度的数组组成的地理位置信息

    def __init__(self, **kwargs):
        """
        实际构造器需要的参数：
        第一种：
        speed 速度 浮点
        user_id 用户id str或者ObjectId
        time  时间  datetime.datetime
        altitude   海拔 浮点
        longitude  经度  浮点
        latitude  维度  浮点
        第二种：
        speed 速度 浮点
        user_id 用户id str或者ObjectId
        time  时间  datetime.datetime
        altitude   海拔 浮点
        loc    地理位置对象 dict/GeoJSON 等同于第一种的longitude和latitude
        (注意地理位置的组成方式:
        {
         "type":"Point/Polygon/....",
         "coordinates":[点的坐标]
        }
        具体请参考如下站点：
        https://docs.mongodb.com/manual/reference/geojson/
        )
        第三种：
        speed 速度 浮点
        user_id 用户id str或者ObjectId
        time  时间  datetime.datetime
        altitude   海拔 浮点
        longitude  经度  浮点
        latitude  维度  浮点
        loc    地理位置对象 dict/GeoJSON 等同于longitude和latitude
        :param kwargs:
        """
        transform_dict = {"alt": "altitude", "lon": "longitude", "lat": "latitude", "ts": "time", "sp": "speed"}
        kwargs = {(transform_dict[k] if k in transform_dict else k): v for k, v in kwargs.items()}
        pos_type = "amap"
        if pos_type not in kwargs:
            kwargs[pos_type] = pos_type  # 缺省地图类型
        if "longitude" in kwargs and 'latitude' in kwargs and "loc" not in kwargs:
            """coordinates里存储了经度和维度"""
            geo = [float(kwargs.get('longitude')), float(kwargs.get('latitude'))]
            temp = {"type": "Point",
                    "coordinates": geo}
            kwargs['loc'] = temp
        elif ("longitude" not in kwargs or 'latitude' in kwargs) and "loc" in kwargs:
            temp = kwargs['loc']['coordinates']
            longitude = temp[0]
            latitude = temp[1]
            kwargs['longitude'] = longitude
            kwargs['latitude'] = latitude
        if kwargs['time'] == "0":
            pass
        else:
            super(GPS, self).__init__(**kwargs)

    @staticmethod
    def mile_time_speed(gps_list: list) -> dict:
        """
        输入一个GPS实例的数组,计算出总历程,总时长和平均速度.
        :param gps_list: GPS实例的数组
        :return: {"mileage":mileage, "total_time": total_time, "avg_speed":avg_speed}
        """
        prev_gps = None  #
        mileage = 0  # 单位米
        total_time = 0  # 单位秒
        for gps in gps_list:
            if prev_gps is None:
                prev_gps = gps
            else:
                position_b = prev_gps.get_attr('loc')['coordinates']  # 经纬度
                time_b = prev_gps.get_attr("time")  # 时间
                position_e = gps.get_attr('loc')['coordinates']  # 经纬度
                time_e = gps.get_attr("time")  # 时间
                distance = amap_module.position_distance(position_b, position_e)  # 单位公里
                times = abs((time_e - time_b).total_seconds())
                temp_avg_speed = distance / (times / (60 * 60))  # 用来取舍低速区间的的，暂时没用
                mileage += distance
                total_time += times
                prev_gps = gps
        """根据坐标计算出来的里程有误差，需要修正一下"""
        total_mileage = mileage * (61 / 49)    # 61 / 49是一个估算的修正值
        total_hour = total_time / (60 * 60)  # 把total_time换算成小时.
        avg_speed = 0 if total_hour == 0 else total_mileage / total_hour  # 平均速度 公里/小时
        res = {
            "sum_mile": round(total_mileage, 1) if isinstance(total_mileage, float) else total_mileage,  # 单位公里
            "sum_time": round(total_hour * 60, 1),  # 时长，单位分钟
            "avg_speed": round(avg_speed, 1) if isinstance(avg_speed, float) else avg_speed  # 平均速度，单位  公里/小时
        }
        return res

    @classmethod
    def insert_queue(cls, obj: dict) -> bool:
        """
        插入gps文档(doc)数据到一个队列(等待批量插入数据库)
        :return:
        """
        cache = mongo_db.cache
        key = "gps_realtime_queue"
        global insert_queue_lock
        lock = insert_queue_lock
        lock.acquire()
        val = cache.get(key)
        if val is None:
            val = list()
        val.append(obj)
        cache.set(key=key, value=val, timeout=300)  # 最长5分钟
        lock.release()
        # cls.async_insert_many()  # 测试用,正式要注销
        return True

    @staticmethod
    def get_queue() -> list:
        """
        取出queue中文档的list
        :return:
        """
        cache = mongo_db.cache
        key = "gps_realtime_queue"
        val = cache.get(key)
        if val is None:
            val = list()
        return val

    @staticmethod
    def clear_queue() -> None:
        """
        清除队列
        :return:
        """
        cache = mongo_db.cache
        key = "gps_realtime_queue"
        cache.delete(key)

    @classmethod
    def async_insert_many(cls) -> str:
        """
        以异步/celery队列的方式.批量插入gps数据.
        :return:
        """
        res = "async_insert_many function: "
        gps_list = cls.get_queue()
        l = len(gps_list)
        mes = "队列长度:{}".format(l)
        print(mes)
        if l == 0:
            pass
        else:
            reserted_list = cls.insert_many(gps_list)
            Track.batch_create_item_from_gps(reserted_list)
            cls.clear_queue()
        return res

    @classmethod
    def get_prev_gps(cls, user_id: (str, ObjectId)) -> dict:
        """
        获取用户的上一个gps信息. 暂时不清楚此方法的应用场景
        :param user_id:
        :return:
        """
        cache = mongo_db.cache
        if user_id is None:
            raise ValueError("user_id不能为空")
        else:
            if isinstance(user_id, ObjectId):
                pass
            else:
                try:
                    user_id = mongo_db.get_obj_id(user_id)
                except Exception as e:
                    logger.exception(exc_info=True, stack_info=True)
                    raise e
                finally:
                    if isinstance(user_id, ObjectId):
                        pass
                    else:
                        ms = "错误的user_id: {}".format(user_id)
                        raise ValueError(ms)
            user_id_str = str(user_id)
            key = "prev_gps_{}".format(user_id_str)
            gps = cache.get(key)
            if gps is None:
                user_dbref = DBRef(collection="user_info", database="platform_db", id=user_id)
                filter_dict = {"user_id": user_dbref}
                sort_dict = {"time": -1}
                gps = cls.find_one_plus(filter_dict=filter_dict, sort_dict=sort_dict)
                if gps is None:
                    pass
                else:
                    cache.set(key=key, value=gps, timeout=86400) # 保存一天
            return gps

    @classmethod
    def get_track(cls, user_id: ObjectId, begin: datetime.datetime = None,
                  end: datetime.datetime = None, limit: int = 500) -> list:
        """
        此方法已被废弃，由全新的类来提供轨迹的功能
        查询用户的移动轨迹，返回的是数组对象，不设置开始时间的话，默认从最早查起。
        不设置结束时间的话，默认一直查到现在。为防止输出过大，限制最大500个数据。
        :param user_id: 用户id
        :param begin: 开始时间
        :param end: 结束时间
        :param limit: 最大限制
        :return:list 格式:[
                            {'time': datetime.datetime(2017, 8, 14, 16, 50, 1),
                            'coordinates': [121.158891, 31.290664],
                            'speed': 0.0
                            },
                            ...]
        """
        if 1:
            raise RuntimeError("此方法已被废弃")
        try:
            user_id = mongo_db.get_obj_id(user_id)
        except ValueError as e:
            logger.error("error", exc_info=True, stack_info=True)
            raise e
        pattern = re.compile(r'^2\d{3}-[01]?\d-[0-3]?\d [012]?\d:[0-6]?\d:[0-6]?\d$')  # 时间匹配
        if isinstance(begin, datetime.datetime):
            pass
        elif isinstance(begin, str) and pattern.match(begin):
            begin = datetime.datetime.strptime(begin, "%Y-%m-%d %H:%M:%S")
        else:
            begin = datetime.datetime.strptime("1970-01-01 0:0:0", "%Y-%m-%d %H:%M:%S")
        if isinstance(end, datetime.datetime):
            pass
        elif isinstance(end, str) and pattern.match(end):
            end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        else:
            end = datetime.datetime.now()
        ses = mongo_db.get_conn(cls.get_table_name())
        pipeline = [
            {"$match": {"user_id": user_id, "time": {"$gt": begin, "$lte": end}}},  # 匹配
            {"$project": {"_id": -1, "time": 1, "speed": 1, "loc.coordinates": 1}},  # 选择列
            {"$sort": {"time": -1}},  # 排序
            {"$limit": limit}  # 限制输出
        ]
        res = ses.aggregate(pipeline=pipeline)
        res = [{"coordinates": x['loc']['coordinates'], "speed": x['speed'],
                "time": x['time'].strftime("%Y-%m-%d %H:%M:%S")} for x in res]
        return res


class Sensor(mongo_db.BaseDoc):
    """传感器信息类
    user_id+sensor_type+time  联合唯一索引
    """

    _table_name = "sensor_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['user_id'] = DBRef  # 用户id
    type_dict['sensor_type'] = str  # 传感器类型
    type_dict['gravity_x'] = float  # 重力x
    type_dict['gravity_y'] = float  # 重力y
    type_dict['gravity_z'] = float  # 重力z
    type_dict['acc_x'] = float  # 加速度x
    type_dict['acc_y'] = float  # 加速度y
    type_dict['acc_z'] = float  # 加速度z
    type_dict['gyro_x'] = float  # 陀螺仪x
    type_dict['gyro_y'] = float  # 陀螺仪y
    type_dict['gyro_z'] = float  # 陀螺仪z
    type_dict['rotational_x'] = float  # 旋转x
    type_dict['rotational_y'] = float  # 旋转y
    type_dict['rotational_z'] = float  # 旋转z
    type_dict['time'] = datetime.datetime  # 记录时间


class PhoneDevice(mongo_db.BaseDoc):
    """
    手机和其所包含的各种传感器信息
    manufacturer+model 联合唯一索引
    """
    _table_name = "phone_device_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # id，是一个ObjectId对象，唯一
    type_dict['accelerometer'] = str  # 加速度计
    type_dict['gravity'] = str  # 重力感应传感器
    type_dict['gyroscope'] = str  # 陀螺仪
    type_dict['manufacturer'] = str  # 制造商名称 和model一起构成unique索引
    type_dict['model'] = str  # 设备型号  和manufacturer一起构成unique索引
    type_dict['rotation_vector'] = str  # 旋转传感器

    def __init__(self, **kwargs):
        """重载构造器"""
        kwargs = {k: str(v).lower() if k not in self.type_dict or self.type_dict[k].__name__ == "str" else v for k, v in
                  kwargs.items()}
        super(PhoneDevice, self).__init__(**kwargs)

    def save(self):
        """重载的父类方法，所有PhoneDevice的实例都应该用此方法保存，以保证唯一索引,
        save可替换的方法包括insert/update
        """
        last_id = None
        table_name = self.table_name()
        sess = mongo_db.get_conn(table_name=table_name)
        save_dict = {k: v for k, v in self.__dict__.items() if v is not None}
        try:
            last_id = sess.save(save_dict)
        except mongo_db.DuplicateKeyError as e:
            # logger.error("重复的移动设备信息", exc_info=True, stack_info=True)
            print("重复的移动设备信息")
            print(e)
            """以唯一性的联合索引查询"""
            query_dict = {"manufacturer": save_dict['manufacturer'], "model": save_dict['model']}
            last_id = self.find_one(**query_dict).get_id()
        finally:
            return last_id

    def save_self_and_return_dbref(self):
        """
        save的升级扩展版
        把参数转成obj对象插入数据库并返回dbref对象,
        return: DBRef
        """
        _id = self.save()
        if _id is None:
            pass
        else:
            self._id = _id
            return self.get_dbref()

    @classmethod
    def mark_repeated(cls) -> list:
        """
        对违反唯一性主键的记录添加repeated="被替换的唯一的记录id"的键值
        :return: 有用的设备的id的字符串格式的list
        """
        ps = cls.find(to_dict=True)
        records = list()  # 记录了所有需要被替换的记录的映射
        d = {}  # 存放有效的设备信息的，values是有用的设备的id的list，唯一。
        for p in ps:
            k1 = p['manufacturer']
            k2 = p['model']
            if k1 is None or k2 is None:
                """不符合要求的记录,会被直接drop掉"""
                p['repeated'] = "drop"
                records.append(p)
            else:
                k = json.dumps({"manufacturer": k1, "model": k2})
                if k not in d:
                    d[k] = p
                else:
                    p_0 = d[k]
                    id_0 = p_0.pop("_id")
                    id_1 = p.pop("_id")
                    p_r = mongo_db.merge_dict(p_0, p)  # 混合dict
                    p_r["_id"] = id_0
                    p["_id"] = id_1
                    d[k] = p_r
                    p['repeated'] = id_0
                    records.append(p)
        # 所有需要被替换的设备的字典
        records = {record['_id']: record['repeated'] for record in records}
        need_drop_id = list(records.keys())  # 需要被删除的移动设备ｉｄ
        d = {val["_id"]: val["_id"] for val in d.values()}
        records.update(d)
        """替换所有用的设备信息"""
        users = User.find()
        """所有用户"""
        users = {user.get_id(): user.get_attr("phones") for user in users if hasattr(user, "phones")}
        rebuild_users = dict()
        for k, v in users.items():  # k是user_id，ｖ是手机设备的DBRef的list
            """把每个用户重复的设备整理一下"""
            phones = list()
            for phone in v:
                try:
                    phone_id = records[phone.id]
                    phones.append(str(phone_id))
                except KeyError as e:
                    raise e
            phones = list(set(phones))  # 删除重复设备列表
            phones = [PhoneDevice.find_by_id(phone).get_dbref() for phone in phones]
            rebuild_users[k] = phones  # 去除重复的手机信息后的，用户ｉｄ和手机设备ｌｉｓｔ的字典
        for user_id, phones in rebuild_users.items():
            """修改用户数据，达到删除重复的目的"""
            filter_dict = {"_id": user_id}
            update_dict = {"$set": {"phones": phones}}
            User.find_alone_and_update(filter_dict=filter_dict, update=update_dict)
        return list(d.keys())


class Message(mongo_db.BaseDoc):
    """
    推送给客户的消息,目前不完善,仅仅满足app端调试
    """
    _table_name = "message_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId                      # id，是一个ObjectId对象，唯一
    type_dict['ticker'] = str                        # 收到消息的时候,通知栏的一次滚动消息
    type_dict['title'] = str                         # 标题
    type_dict['detail'] = str                        # 内容
    type_dict['url'] = str                           # 详情页面地址
    type_dict['effective_time'] = datetime.datetime  # 最后有效时间  默认15分钟. 用户收到后会重置这个变量


    def __init__(self, **kwargs):
        if "title" not in kwargs or "detail" not in kwargs:
            raise ValueError("title和detail参数必须")
        if "effective_time" not in kwargs:
            kwargs['effective_time'] = datetime.datetime.now() + datetime.timedelta(minutes=15)
        super(Message, self).__init__(**kwargs)


def clear_phone() -> None:
    """清除多余的设备"""
    # 先修正用户的手机设备列表。
    phones_01 = PhoneDevice.mark_repeated()  # mark_repeated返回的有用id
    phones = PhoneDevice.find(to_dict=False)
    drop_ids = [x.get_id() for x in phones if x.get_id() not in phones_01]
    ses = mongo_db.get_conn(table_name="phone_device_info")
    filter_dict = {"_id": {"$in": drop_ids}}
    ses.delete_many(filter=filter_dict)


if __name__ == "__main__":
    # city_list = ['上海市', '嘉善县', '嘉兴市', '杭州市', '绍兴市', '余姚市', '宁波市']
    # code_list = [310000, 330421, 330400, 330100, 330600, 330281, 330200]
    # args = {"city_code_list": code_list, "city_name_list": city_list}
    # weathers = RouteWeather.get_route_weather(ObjectId("5a052d294660d327825df124"))
    # print(weathers)
    # User.app_version_list()
    # User.app_version_list()
    # User.set_driving_license()
    # GPS.async_insert_many()
    UserLicenseRelation.rebuild()
    pass
