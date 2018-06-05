# -*- coding: utf-8 -*-
import sys
import os
"""直接运行此脚本，避免import失败的方法"""
__dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if __dir_path not in sys.path:
    sys.path.append(__dir_path)
import mongo_db
from api.data.item_module import User
import datetime
import re


"""事故模块"""


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
get_datetime_from_str = mongo_db.get_datetime_from_str
cache = mongo_db.cache


class AccidentData(mongo_db.BaseFile):
    """
    事故相关资料,可以是图片,文件,视频等.
    """
    _table_name = "accident_data"


class Accident(mongo_db.BaseDoc):
    """事故类
    """
    _table_name = "accident_info"
    type_dict = dict()
    type_dict["_id"] = ObjectId  # id 唯一
    type_dict["writer"] = DBRef  # dbref 记录者id,
    type_dict['code'] = str  # 事故编号
    type_dict['title'] = str  # 事故标题,非必须
    type_dict['content'] = str  # 事故正文,必须,指向
    type_dict['comment'] = str  # 事故备注,非必须
    type_dict['type'] = str  # 事故类型 追尾碰撞, 双车刮蹭, 部件失效, 车辆倾覆
    type_dict['level'] = str  # 事故结果类别, 轻微事故, 一般事故, 重大事故, 特大事故
    type_dict['loss'] = float  # 事故造成的损失.浮点.
    type_dict['plate_number'] = str  # 肇事车牌
    type_dict['driver_name'] = str  # 肇事司机真实姓名
    type_dict['time'] = datetime.datetime  # 事发时间
    type_dict['address'] = str  # 事发地址
    type_dict['city'] = str  # 事发城市
    type_dict['files'] = list  # 相关视频,文件资料.内部都是DBRef
    type_dict['status'] = int   # 事故状态, 1已处理0未处理
    type_dict['create_date'] = datetime.datetime
    type_dict['last_update'] = datetime.datetime

    def __init__(self, **kwargs):
        files = kwargs.pop("files", list())
        new_files = list()
        for file in files:
            if isinstance(file, DBRef) and DBRef.collection == AccidentData.get_table_name():
                new_files.append(file)
            elif isinstance(file, ObjectId):
                f = DBRef(database=mongo_db.db_name, collection=AccidentData.get_table_name(), id=file)
                new_files.append(f)
            elif isinstance(file, str) and len(file) == 24:
                f = DBRef(database=mongo_db.db_name, collection=AccidentData.get_table_name(), id=ObjectId(file))
                new_files.append(f)
            else:
                pass
        kwargs['files'] = new_files
        now = datetime.datetime.now()
        if "create_date" not in kwargs:
            kwargs['create_date'] = now
        if "last_update" not in kwargs:
            kwargs['last_update'] = now
        super(Accident, self).__init__(**kwargs)

    @classmethod
    def transform_file_path(cls, raw: object, include_data: bool = False) -> dict:
        """
        把一个实例或者doc对象的转化为适合前端呈现的格式,包括:
        1. 全部是都是字符串和数字
        2. files部分转化为合适的路径.
        这个函数一般在返回数据给前端的时候调用.
        :param raw: 实例/doc
        :param include_data: 是否在返回对象中包含数据? 默认不包含数据只包含url_path
        :return:  符合1.2要求的字典
        """
        if isinstance(raw, cls):
            raw = raw.get_dict()
        files = raw.pop("files", list())
        if len(files) == 0:
            r = list()
        else:
            r = list()
            for file in files:
                f = {"_id": file.id}
                d = AccidentData.find_one_cls(filter_dict=f)
                temp = AccidentData.transform(d, include_data=include_data)
                r.append(temp)
        raw = mongo_db.to_flat_dict(raw)
        raw['files'] = r
        return raw

    @classmethod
    def page(cls, driver_name: str = None, writer: (str, ObjectId, DBRef) = None, status: int = None,
             plate_number: str = None, city: str = None, begin_date: datetime.datetime = None,
             end_date: datetime.datetime = None, index: int = 1, num: int = 20, can_json: bool = True,
             reverse: bool = True) -> dict:
        """
        分页查询行车记录
        :param driver_name: 司机真实姓名,为空表示所有司机
        :param writer: 录入者id,默认指向user_info的_id
        :param status: int 处理状态 0未处理,1已处理, -1和None表示不做筛选
        :param plate_number: 车牌
        :param city: 城市
        :param begin_date:   开始时间
        :param end_date:   截至时间
        :param index:  页码
        :param can_json:   是否进行can json转换
        :param num:   每页多少条记录
        :param reverse:   是否倒序排列?
        :return: 事件记录的列表和统计组成的dict
        """
        filter_dict = dict()
        if isinstance(driver_name, str) and len(driver_name) > 1:
            """司机名存在"""
            filter_dict['driver_name'] = driver_name
        if writer is not None:
            if isinstance(writer, DBRef):
                filter_dict['writer'] = writer
            elif isinstance(writer, ObjectId):
                writer = DBRef(database=mongo_db.db_name, collection=User.get_table_name(), id=writer)
                filter_dict['writer'] = writer
            elif isinstance(writer, str) and len(writer) == 24:
                writer = DBRef(database=mongo_db.db_name, collection=User.get_table_name(), id=ObjectId(writer))
                filter_dict['writer'] = writer
            else:
                ms = "身份验证失败"
                raise ValueError(ms)
        if status is not None and status != -1:
            filter_dict['status'] = status
        if plate_number is not None:
            filter_dict['plate_number'] = plate_number
        if city is not None:
            filter_dict['city'] = city
        if isinstance(begin_date, datetime.datetime) and isinstance(end_date, datetime.datetime):
            filter_dict['time'] = {"$lte": end_date, "$gte": begin_date}
        elif isinstance(begin_date, datetime.datetime):
            filter_dict['time'] = {"$gte": begin_date}
        elif isinstance(end_date, datetime.datetime):
            filter_dict['time'] = {"$lte": end_date}
        else:
            pass
        skip = (index - 1) * num
        sort_dict = {"time": -1 if reverse else 1}
        count = cls.count(filter_dict=filter_dict)
        res = cls.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, skip=skip, limit=num, to_dict=True)
        if can_json:
            res = [mongo_db.to_flat_dict(x) for x in res]
        data = {"count": count, "data": res}
        return data