# -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
import datetime
import random


ObjectId = orm_module.ObjectId


"""对象类"""


class Contacts(orm_module.BaseDoc):
    """通讯录中的单条记录"""
    _table_name = "contacts"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name'] = str  # 人名
    type_dict['phone'] = str  # 手机号码
    type_dict['remark'] = str  # 备注
    type_dict['device_id'] = str  # 极光id,也是device._id
    """
    以上2条是基本信息,手机通讯录中有很多附加的信息.但不保证都有
    """

    orm_module.collection_exists(table_name=_table_name, auto_create=True)


class Device(orm_module.BaseDoc):
    """
    移动设备(手机/平板)信息
    """
    _table_name = "device"
    type_dict = dict()
    type_dict['_id'] = str            # 极光的id
    type_dict['brand'] = str       # 设备品牌
    type_dict['imei'] = str         # imei号码
    type_dict['model'] = str         # 型号
    type_dict['version'] = str         # 系统版本

    orm_module.collection_exists(table_name=_table_name, auto_create=True)

    @classmethod
    def save_data(cls, json_data: dict) -> dict:
        """
        上传手机联系人和设备信息.
        重复上传会覆盖上一次的.
        :param json_data:
        :return:
        """
        mes = {"message": "success"}
        contacts = json_data.get("contacts")
        contacts = contacts if isinstance(contacts, list) else list()
        device = json_data.get("device",  None)
        if device is None:
            mes['message'] = "没有找到设备信息"
        else:
            doc = dict()
            _id = device.get("registration_id", "")
            doc['brand'] = device.get("Brand", "")
            doc['imei'] = device.get("Imei", "")
            doc['model'] = device.get("ProductModel", "")
            doc['version'] = device.get("SystemVersion", "")
            db_client = orm_module.get_client()
            c1 = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client)  # device表
            c2 = orm_module.get_conn(table_name=Contacts.get_table_name(), db_client=db_client)  # contacts表
            with db_client.start_session(causal_consistency=True) as ses:
                with ses.start_transaction(write_concern=orm_module.get_write_concern()):
                    f1 = {"_id": _id}
                    u = {"$set": doc}
                    after = orm_module.ReturnDocument.AFTER
                    r = c1.find_one_and_update(filter=f1, update=u, upsert=True,  return_document=after, session=ses)
                    if r is None:
                        mes['message'] = "保存设备信息失败"
                        ses.abort_transaction()
                    else:
                        f2 = {"device_id": _id}
                        r1 = c2.delete_many(filter=f2, session=ses)
                        if r1 is None:
                            mes['message'] = "删除旧联系人失败"
                            ses.abort_transaction()
                        else:
                            contacts = [cls.insert_return(x, {"device_id": _id}) for x in contacts]
                            r2 = c2.insert_many(documents=contacts)
                            if r2 is None:
                                mes['message'] = "插入新联系人失败"
                                ses.abort_transaction()
                            else:
                                pass
        return mes

    @classmethod
    def insert_return(cls, item: dict, update:  dict) -> dict:
        """
        在字典中插入一个键值对然后再返回,
        :param item:
        :param update:
        :return:
        """
        item.update(update)
        return item


class Location(orm_module.BaseDoc):
    """
    位置信息
    """
    _table_name = "location_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId  #
    type_dict['registration_id'] = str  # 极光的id
    type_dict['longitude'] = str  # 经度
    type_dict['latitude'] = str  # 纬度
    type_dict['time'] = datetime.datetime.now()

    @classmethod
    def save_data(cls, json_data: dict) -> dict:
        """
        保存位置信息
        :param json_data:
        :return:
        """
        mes = {"message": "success"}
        if json_data is None or len(json_data) == 0:
            mes['message'] = "没有找到位置信息"
        else:
            r = cls.insert_one(doc=json_data)
            if isinstance(r, ObjectId):
                pass
            else:
                mes['message'] = "插入失败"
        return mes


class User(orm_module.BaseDoc):
    """用户表"""
    _table_name = "user_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_name'] = str
    type_dict['password'] = str
    type_dict['nick_name'] = str
    type_dict['last'] = datetime.datetime
    type_dict['time'] = datetime.datetime

    @classmethod
    def add_user(cls, **kwargs) -> dict:
        """
        添加用户
        :param kwargs:
        :return:
        """
        mes = {"message": "success"}
        user_name = kwargs.get("user_name", '')
        pwd = kwargs.get("password", '')
        args = {"user_name": user_name, "password": pwd}
        db = orm_module.get_client()
        conn = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db)
        write_concern = orm_module.WriteConcern(w=1, j=True)
        with db.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=write_concern):
                r = conn.find_one(filter={'user_name': user_name})
                if r is not None:
                    ms = "账户 {} 已存在!".format(user_name)
                    mes['message'] = ms
                else:
                    """提取其他信息"""
                    role_id_str = kwargs.get("role_id", '')
                    if isinstance(role_id_str, str) and len(role_id_str) == 24:
                        role_id = ObjectId(role_id_str)
                    elif isinstance(role_id_str, ObjectId):
                        role_id = role_id_str
                    else:
                        role_id = None
                    args['role_id'] = role_id
                    args['dept_id'] = None
                    now = datetime.datetime.now()  # 创建时间
                    args['time'] = now
                    args['last'] = now
                    args['status'] = 1
                    nick_name = kwargs.get("nick_name", "")
                    if isinstance(nick_name, str) and len(nick_name) > 0:
                        args['nick_name'] = nick_name
                    else:
                        nick_name = "guest_{}".format(str(random.randint(1, 99)).zfill(2))
                        args['nick_name'] = nick_name
                    r = conn.insert_one(args)
                    if r is None:
                        ms = "保存用户账户失败"
                        mes['message'] = ms
                    else:
                        pass
        return mes

    @classmethod
    def login(cls, user_name: str, password: str) -> dict:
        """
        管理员登录检查
        当前管理员: root/Phone@3436
        :param user_name:
        :param password:
        :return:
        """
        mes = {"message": "success"}
        f = {"user_name": user_name}
        conn = cls.get_collection()
        r = conn.find_one(filter=f)
        if r is None:
            mes['message'] = "用户名不存在"
        else:
            if user_name != "root" and r['status'] == 0:
                mes['message'] = "账户已被禁用"
            else:
                if password.lower() == r['password'].lower():
                    mes['_id'] = r['_id']
                else:
                    mes['message'] = '密码错误'
        return mes

    @classmethod
    def change_pw(cls, u_id: ObjectId, pwd_old: str, pw_n1: str, pw_n2: str) -> dict:
        """
        修改密码
        :param u_id:
        :param pwd_old:
        :param pw_n1:
        :param pw_n2:
        :return:
        """
        mes = {"message": 'unknow error!'}
        db_client = orm_module.get_client()
        w = orm_module.get_write_concern()
        col = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client, write_concern=w)
        with db_client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=w):
                f = {"_id": u_id}
                p = ["_id", "password"]
                r = col.find_one(filter=f, projection=p)
                if r is None:
                    mes['message'] = "错误的用户id:{}".format(u_id)
                else:
                    if r.get("password", "").lower() == pwd_old.lower():
                        if pw_n1 == pw_n2:
                            pw = pw_n1.lower()
                            u = {"$set": {"password": pw}}
                            r = col.find_one_and_update(filter=f, update=u, return_document=orm_module.ReturnDocument.AFTER)
                            if r['password'] == pw:
                                mes['message'] = "success"
                            else:
                                mes['message'] = "保存失败"
                    else:
                        mes['message'] = "原始密码错误"
        return mes


if __name__ == "__main__":
    pass

