# -*- coding:utf-8 -*-
import sys
import os

"""直接运行此脚本，避免import失败的方法"""
__dir_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if __dir_path not in sys.path:
    sys.path.append(__dir_path)
import mongo_db
import datetime


"""
item_module.py的扩展模块.
主要是对item_module模块的补充
"""


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


class MonthCounter(dict):
    """
    月统计器,非持久化类
    """
    def __init__(self, arg_dict: dict = None):
        arg_dict = dict() if arg_dict is None else arg_dict
        day_count = dict() if arg_dict.get("day_count") is None else arg_dict['day_count']  # 日统计
        day_count = day_count
        month_count = sum([len(v) for k, v in day_count.items() if isinstance(v, list)])  # 月统计
        super(MonthCounter, self).__init__(zip(("month_count", "day_count"), (month_count, day_count)))

    def add_one(self):
        """
        计数+1
        :return:
        """
        day_count = self['day_count']
        now = datetime.datetime.now()
        day = str(now.day)   # mongodb的限制,key必须是str
        day_list = day_count.get(day)
        if day_list is None:
            day_list = list()
        day_list.append(now)
        day_count[day] = day_list
        month_count = sum([len(v) for k, v in day_count.items() if isinstance(v, list)])  # 月统计
        self['month_count'] = month_count
        self['day_count'] = day_count

    def get_dict(self):
        return {"day_count": self['day_count'], "month_count": self['month_count']}


class UseHandlerRecord(mongo_db.BaseDoc):
    """
    一个计数器,用于记录用户操作过哪些函数,以及操作的结果的统计.
    计数器以月为单个记录的最大统计区间.
    """
    _table_name = "user_handle_record"
    type_dict = dict()
    type_dict['_id'] = ObjectId  # 记录id,
    type_dict['user_id'] = DBRef  # user_id,
    type_dict['year'] = int
    type_dict['month'] = int
    type_dict['func_name'] = str  # 函数名
    type_dict['counter'] = MonthCounter
    type_dict['create_date'] = datetime.datetime
    type_dict['update_date'] = datetime.datetime

    def __init__(self, **kwargs):
        user_id = kwargs.get("user_id")
        if user_id is None:
            ms = "user_id不能为空"
            raise ValueError(ms)
        else:
            if isinstance(user_id, str) and len(user_id) == 24:
                user_id = ObjectId(user_id)
                kwargs['user_id'] = DBRef(database=mongo_db.db_name, collection="user_info", id=user_id)
            elif isinstance(user_id, ObjectId):
                kwargs['user_id'] = DBRef(database=mongo_db.db_name, collection="user_info", id=user_id)
            elif isinstance(user_id, DBRef):
                pass
            else:
                ms = "错误的user_id类型:{}".format(type(user_id))
                raise ValueError(ms)
        today = datetime.datetime.today()
        year = today.year
        month = today.month
        if "func_name" not in kwargs:
            ms = "func_name 不能为空"
            raise ValueError(ms)
        if "year" not in kwargs:
            kwargs['year'] = year
        if "month" not in kwargs:
            kwargs['month'] = month
        if "counter" not in kwargs:
            kwargs['counter'] = dict()
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(UseHandlerRecord, self).__init__(**kwargs)

    @classmethod
    def record(cls, user_id: ObjectId, func_name: str) -> None:
        """
        对用户的操作行为进行计数
        :param user_id: 用户id
        :param func_name: 函数名
        :return:
        """
        user_dbref = None
        if user_id is None:
            ms = "user_id不能为空"
            raise ValueError(ms)
        else:
            if isinstance(user_id, str) and len(user_id) == 24:
                user_id = ObjectId(user_id)
                user_dbref = DBRef(database=mongo_db.db_name, collection="user_info", id=user_id)
            elif isinstance(user_id, ObjectId):
                user_dbref = DBRef(database=mongo_db.db_name, collection="user_info", id=user_id)
            elif isinstance(user_id, DBRef):
                user_dbref = user_id
            else:
                ms = "错误的user_id类型:{}".format(type(user_id))
                raise ValueError(ms)
        f = {"user_id": user_dbref, "func_name": func_name}
        instance = cls.find_one_plus(filter_dict=f, instance=True)
        if instance is None:
            instance = cls(user_id=user_dbref, func_name=func_name)
        counter = instance.get_attr("counter", None)
        if counter is None:
            counter = MonthCounter()

        counter.add_one()
        doc = instance.get_dict()
        f = {"_id": doc.pop("_id")}
        doc['counter'] = counter.get_dict()
        doc['update_date'] = datetime.datetime.now()
        u = {"$set": doc}
        r = cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)
        print(r)

    @classmethod
    def get_count(cls, user_id: ObjectId, func_name: str) -> int:
        """
        获取用户对某一操作的统计信息
        :param user_id:
        :param func_name:
        :return:
        """
        user_dbref = None
        if user_id is None:
            ms = "user_id不能为空"
            raise ValueError(ms)
        else:
            if isinstance(user_id, str) and len(user_id) == 24:
                user_id = ObjectId(user_id)
                user_dbref = DBRef(database=mongo_db.db_name, collection="user_info", id=user_id)
            elif isinstance(user_id, ObjectId):
                user_dbref = DBRef(database=mongo_db.db_name, collection="user_info", id=user_id)
            elif isinstance(user_id, DBRef):
                user_dbref = user_id
            else:
                ms = "错误的user_id类型:{}".format(type(user_id))
                raise ValueError(ms)
        f = {"user_id": user_dbref, "func_name": func_name}
        res = cls.find_plus(filter_dict=f, to_dict=True)
        if len(res) == 0:
            return 0
        else:
            return sum([x['counter']['month_count'] for x in res])


if __name__ == "__main__":
    UseHandlerRecord.record(user_id=ObjectId("5982eb1fde713e428829d3d8"), func_name="xxx")
    print(UseHandlerRecord.get_count(user_id=ObjectId("5982eb1fde713e428829d3d8"), func_name="xxx"))
    pass