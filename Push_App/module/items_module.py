# -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
from flask import request
import datetime
import random


ObjectId = orm_module.ObjectId
start_img_dir = os.path.join(__project_dir__, "resource", "start_image")
IMAGE_DIR = os.path.join(__project_dir__, "static", "start_image")  # 上传启动图片的默认目录


def check_start_dir():
    """检查启动图片目录"""
    if not os.path.exists(start_img_dir):
        os.makedirs(path=start_img_dir)
    else:
        pass


def last_icon() -> str:
    """
    获取最后一个图标的url,目前暂停使用2019-1-3
    :return:
    """
    d = os.path.join(__project_dir__, "static", "icon")
    if os.path.exists(d):
        pass
    else:
        os.makedirs(name=d)
    names = os.listdir(d)
    allow_img = ['jpg', 'jpeg', 'png']
    resp = [
        {"ctime": os.path.getctime(os.path.join(d, name)), "name": name}
        for name in names if name.lower().split(".")[-1] in allow_img
    ]
    resp.sort(key=lambda obj: obj['ctime'], reverse=True)
    if len(resp) == 0:
        s = "/static/image/no_icon.png"
    else:
        s = "/static/icon/{}".format(resp[0]['name'])
    return s


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
    type_dict['time'] = datetime.datetime

    orm_module.collection_exists(table_name=_table_name, auto_create=True)

    @classmethod
    def find_one(cls, filter_dict: dict) -> dict:
        """
        查找一个设备信息.会附带contacts的数量
        :param filter_dict:
        :return:
        """
        col = cls.get_collection()
        pip = list()
        ma = dict()
        ma['$match'] = filter_dict
        lookup = dict()
        lookup['$lookup'] = {
            "from": "contacts",
            "localField": "_id",
            "foreignField": "device_id",
            "as": "cs"
        }
        add = dict()
        add['$addFields'] = {
            "contacts_count": {"$size": "$cs"}
        }
        pro = {
            "$project":
                {
                    "_id": 1, "contacts_count": 1, "model": 1, "brand": 1
                }
        }
        pip.append(ma)
        pip.append(lookup)
        pip.append(add)
        pip.append(pro)
        look2 = {
            "$lookup":
                {
                    "from": "location_info",
                    "let": {"the_id": "$_id"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$$the_id", "$registration_id"]}}},
                        {"$project": {
                            "x": "$latitude",
                            "y": "$longitude",
                            "city": 1,
                            "last": "$time"
                        }},
                        {"$sort": {"last": 1}}
                    ],
                    "as": "lp"
                }
        }
        pip.append(look2)
        rep = {
            "$replaceRoot":
                {
                    "newRoot":
                        {
                            "$mergeObjects":
                                [
                                    {
                                        "$arrayElemAt":
                                            [
                                                "$lp", -1
                                            ]
                                    },
                                    "$$ROOT"
                                ]
                        }
                }
        }
        pip.append(rep)
        p2 = {"$project": {"lp": 0}}
        pip.append(p2)
        r = col.aggregate(pipeline=pip)
        r = [x for x in r]
        if len(r) > 0:
            return r[0]
        else:
            return None

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
            doc['time'] = datetime.datetime.now()
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
                            print("联系人数量: {}".format(len(contacts)))
                            r2 = c2.insert_many(documents=contacts)
                            if r2 is None:
                                mes['message'] = "插入新联系人失败"
                                ses.abort_transaction()
                            else:
                                """成功,返回极光id"""
                                mes['_id'] = _id
        return mes

    @classmethod
    def insert_return(cls, item: dict, update:  dict) -> dict:
        """
        在字典中插入一个键值对然后再返回,
        这是一个为了快速迭代的辅助函数
        :param item:
        :param update:
        :return:
        """
        item.update(update)
        return item

    @classmethod
    def paging_info(cls, filter_dict: dict, page_index: int = 1, page_size: int = 10) -> dict:
        """
        分页设备信息.由于涉及的关系复杂,这里使用了cls.aggregate函数
        :param filter_dict: 过滤器,由用户的权限生成
        :param page_index: 页码(当前页码)
        :param page_size: 每页多少条记录
        :return:
        """
        pipeline = list()
        pipeline.append({"$match": filter_dict})
        pipeline.append({"$sort": {"time": -1}})
        product_cond = {
            "$lookup": {
                "from": "contacts",
                "let": {"did": "$_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$device_id", "$$did"]}}},
                    {"$project": {"_id": 0}}
                ],
                "as": "contacts"
            }
        }
        pipeline.append(product_cond)
        add = {
            "$addFields":
                {
                    "contacts_count": {"$size": "$contacts"}
                }
        }
        pipeline.append(add)
        p = {
            "$project": {"contacts":  0}
        }
        pipeline.append(p)
        look2 = {
            "$lookup":
                {
                    "from": "location_info",
                    "let": {"the_id": "$_id"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$$the_id", "$registration_id"]}}},
                        {"$project": {
                            "x": "$latitude",
                            "y": "$longitude",
                            "city": 1,
                            "last": "$time"
                        }},
                        {"$sort": {"last": 1}}
                    ],
                    "as": "lp"
                }
        }
        pipeline.append(look2)
        rep = {
            "$replaceRoot":
                {
                    "newRoot":
                        {
                            "$mergeObjects":
                                [
                                    {
                                        "$arrayElemAt":
                                            [
                                                "$lp", -1
                                            ]
                                    },
                                    "$$ROOT"
                                ]
                        }
                }
        }
        pipeline.append(rep)
        p2 = {"$project": {"lp": 0}}
        pipeline.append(p2)
        resp = cls.aggregate(pipeline=pipeline, page_size=page_size, page_index=page_index)
        return resp

    @classmethod
    def batch_delete(cls, ids: list) -> dict:
        """
        批量删除设备和联系人
        :param ids: _id的数组
        :return:
        """
        mes = {"message": "success"}
        f1 = {"_id": {"$in": ids}}
        f2 = {"device_id": {"$in": ids}}
        f3 = {"registration_id": {"$in": ids}}
        db_client = orm_module.get_client()
        col1 = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client)
        col2 = orm_module.get_conn(table_name=Contacts.get_table_name(), db_client=db_client)
        col3 = orm_module.get_conn(table_name=Location.get_table_name(), db_client=db_client)
        with db_client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=orm_module.get_write_concern()):
                r1 = col1.delete_many(filter=f1, session=ses)
                if isinstance(r1, orm_module.DeleteResult):
                    r2 = col2.delete_many(filter=f2, session=ses)
                    if isinstance(r2, orm_module.DeleteResult):
                        r3 = col3.delete_many(filter=f3, session=ses)
                        if isinstance(r3, orm_module.DeleteResult):
                            """成功"""
                            pass
                        else:
                            mes['message'] = "删除位置信息失败"
                            ses.abort_transaction()
                    else:
                        mes['message'] = "删除联系人失败"
                        ses.abort_transaction()
                else:
                    mes['message'] = "删除设备出错"
                    ses.abort_transaction()
        return mes


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
            json_data['time'] = datetime.datetime.now()
            r = cls.insert_one(doc=json_data)
            if isinstance(r, ObjectId):
                pass
            else:
                mes['message'] = "插入失败"
        return mes


class User(orm_module.BaseDoc):
    """
    用户表
    当前管理员: root/Phone@3436
    """
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


class StartArgs(orm_module.BaseDoc):
    """
    启动参数,
    其中的启动图片建议如下:
    像素 1080*1920
    长宽比 9:16
    """
    _table_name = "start_args"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['delay'] = int  # 启动延迟
    type_dict['img_url'] = str  # 启动图片地址(相对地址,但返回的是绝对地址)
    type_dict['redirect'] = str  # 启动完成后的跳转地址(相对地址,但返回的是绝对地址)
    type_dict['time'] = datetime.datetime

    @classmethod
    def get_last(cls) -> dict:
        """
        获取最新的启动参数
        :return:
        """
        mes = {"message": "success"}
        s = [("time", -1)]
        r = cls.find_one(filter_dict=dict(), sort=s)
        if r is None:
            mes['delay'] = 1
            mes['img_url'] = ""
            mes['redirect'] = ""
        else:
            mes['delay'] = r.get("delay", 1)
            mes['img_url'] = r.get("img_url", "")
            mes['redirect'] = r.get("redirect", "")
        """测试用参数"""
        # mes['delay'] = 5
        # mes['img_url'] = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1547110678&di=e2fd34807d585b5873fb02f7c5f07f8b&imgtype=jpg&er=1&src=http%3A%2F%2Fi0.hdslb.com%2Fbfs%2Farticle%2F448a4ec600fa415f18006be9bf0433e560928311.jpg"
        # mes['redirect'] = "http://www.middear.cn"
        return mes


class UploadImageHistory(orm_module.BaseDoc):
    """上传图片记录"""
    _table_name = "upload_image_history"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['file_name'] = str
    type_dict['storage_name'] = str
    type_dict['file_size'] = int  # 单位字节
    type_dict['file_type'] = str
    type_dict['upload_time'] = datetime.datetime

    @classmethod
    def upload(cls, req: request, dir_path: str = None) -> dict:
        """
        上传条码文件
        :param req:
        :param dir_path: 保存上传文件的目录
        :return:
        """
        dir_path = IMAGE_DIR if dir_path is None else dir_path
        if not os.path.exists(dir_path):
            os.makedirs(name=dir_path)
        mes = {"message": "success"}
        file = req.files.get("file")
        if file is None:
            mes['message'] = "没有找到上传的文件"
        else:
            file_name = file.filename.lower()
            file_type = file.content_type
            _id = ObjectId()
            suffix = file_name.split(".")[-1]
            storage_name = "{}.{}".format(str(_id), suffix)
            f_p = os.path.join(dir_path, storage_name)
            with open(f_p, "wb") as f:
                file.save(dst=f)  # 保存文件
            file_size = os.path.getsize(f_p)
            doc = {
                "_id": _id,
                "file_name": file_name,
                "file_type": file_type,
                "file_size": file_size,
                "storage_name": storage_name,
                "time": datetime.datetime.now()
            }
            r = cls.insert_one(doc=doc)
            if r == _id:
                mes['img_url'] = "manage/image/view?fid={}".format(str(_id))
            else:
                mes['message'] = "保存纪录失败"
        return mes


class MessageHistory(orm_module.BaseDoc):
    """
    推送的消息的历史.
    消息会保存在数据库中,并且会标记是否已读?
    这样一旦客户不在线,推送失败后,打开App还是可以看到未读的消息.
    """
    _table_name = "message_history"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['device_id'] = str  # Device._id
    type_dict['title'] = str
    type_dict['alert'] = str
    type_dict['url'] = str
    type_dict['viewed'] = bool  # 消息是否已查看? 默认未查看
    type_dict['time'] = datetime.datetime  # 发送时间


if __name__ == "__main__":
    Device.find_one(filter_dict={"_id": "170976fa8ad9fd6f9ad"})
    pass

