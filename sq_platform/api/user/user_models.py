# -*- coding:utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.split(os.path.split(sys.path[0])[0])[0]
if project_dir not in sys.path:
    sys.path.append(project_dir)
import mongo_db
from bson.objectid import ObjectId
from bson.errors import InvalidId
import random
import datetime
from uuid import uuid4
import sys
from log_module import get_logger
import random
from error_module import pack_message


"""定义用户的模型及相关方法,
此模块被废止,迁移到api.data.item_module模块中 2017-11-9
"""

table_name = "user_info"
image_patch = "static/image/head_img/"
DBRef = mongo_db.DBRef
MyDBRef = mongo_db.MyDBRef
cache = mongo_db.cache
logger = get_logger()


class User(mongo_db.BaseDoc):
    """用户类"""
    _table_name = table_name
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
    type_dict['email'] = str  # 电子邮件，可用来登录，唯一 暂时未实现
    type_dict['phone_num'] = str  # 手机号码，可用来登录，唯一
    type_dict['born_date'] = datetime.date  # 出生日期
    type_dict['description'] = str  #
    type_dict['emergency_contact'] = str  # 紧急联系人(姓名)
    type_dict['emergency_phone'] = str  # 紧急联系号码
    # type_dict['cars'] = list  # 名下车辆的id，是一个DBRef的List对象，默认为空  对应car_license_info表
    """
    由于业务逻辑上个人可能创建和自己不相干的车牌的查询器，所以这个cars失去了业务逻辑上的异议。
    在车牌信息用，有一个user_id参数。用于确认车牌信息的使用者。
    车牌号码和使用者id构成了联合唯一主键。   
    """
    type_dict['phones'] = list  # 名下手机的的id，是一个DBRef的List对象，默认为空  对应phone_device_info表
    type_dict['user_status'] = int  # 用户状态，1表示可以登录，0表示禁止登录
    type_dict['wx_id'] = str  # 微信id
    type_dict['weibo_id'] = str  # 微博id
    type_dict['create_date'] = datetime.datetime  # 用户的注册/创建日期

    def __init__(self, **kwargs):
        if "user_name" not in kwargs:
            kwargs['user_name'] = kwargs['phone_num']
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
            filter_dict = {"_id": {"in": [phones]}}
            """没写完"""
        else:
            phones = list()
        user_id = self.get_id()
        filter_dict = {"user_id": user_id}
        """差相关的行驶证信息"""
        car_licenses = CarLicense.find_plus(filter_dict=filter_dict)
        car_licenses = [x.to_flat_dict() for x in car_licenses]
        print(car_licenses)




    @classmethod
    def add_phone_device(cls, user_id: (str, ObjectId, DBRef, MyDBRef), dbref_obj: mongo_db.DBRef)->bool:
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
            ses.delete_one({"_id": result.get_id()})
            mongo_db.cache.delete(result.token)
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
        通过token获取用户信息，
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


class CarLicense(mongo_db.BaseDoc):
    """行驶证"""
    _table_name = "car_license_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict["user_id"] = ObjectId  # 关联用户id 和plate_number构成了联合唯一主键。
    type_dict["permit_image_url"] = str  # 车辆照片url
    type_dict["plate_number"] = str  # 车辆号牌 和user_id构成了联合唯一主键。
    type_dict["car_type"] = str  # 车辆类型  比如 重型箱式货车
    type_dict["owner_name"] = str  # 车主姓名/不一定是驾驶员
    type_dict["address"] = str  # 地址
    type_dict["use_nature"] = str  # 使用性质
    type_dict["car_model"] = str  # 车辆型号  比如 一汽解放J6
    type_dict["vin_id"] = str    # 车辆识别码/车架号的后六位 如果大于6未，查询违章的时候就用后6位查询
    type_dict["engine_id"] = str  # 发动机号
    type_dict["register_city"] = str  # 注册城市,不必填,默认查归属地
    type_dict["register_date"] = datetime.date  # 注册日期
    type_dict["issued_date"] = datetime.date  # 发证日期
    type_dict["create_date"] = datetime.datetime  # 创建日期

    def __init__(self, **kwargs):
        keys = kwargs.keys()
        if "create_date" not in keys:
            kwargs['create_date'] = datetime.datetime.now()
        if "plate_number" in keys:
            """plate_number为空是在仅仅上传了行车证照片，还没有输入车牌信息的情况。一个用户只允许一条这样的记录"""
            kwargs['plate_number'] = kwargs['plate_number'].upper()
        if "user_id" not in kwargs:
            try:
                raise ValueError("user_id不能为空")
            except ValueError as e:
                logger.exception("创建CarLicense实例失败，user_id缺失")
                raise e

        super(CarLicense, self).__init__(**kwargs)

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


def rebuild_car_license()->None:
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


if __name__ == "__main__":
    user_id = ObjectId("59895177de713e304a67d30c")
    user = User.find_by_id(user_id)
    user.get_archives()
    pass
