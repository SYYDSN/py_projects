# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
from bson.objectid import ObjectId
import datetime


"""
此模块用于根据老师喊单的信号，生成对应的虚拟喊单信号
"""


class Teacher(mongo_db.BaseDoc):
    """
    老师
    """
    _table_name = "teacher"
    type_dict = dict()
    """真实老师的id取自简道云"""
    type_dict['_id'] = ObjectId
    """真实老师的name可能取自简道云(也可再修改)"""
    type_dict['name'] = str   # 展示的名字，比如青云老师等
    type_dict['real_name'] = str  # 真实姓名，非必须
    type_dict['level'] = str  # 老师等级
    type_dict['motto'] = str  # 座右铭
    type_dict['feature'] = str  # 特性，风格，特点
    type_dict['resume'] = str  # 简历
    type_dict['create_date'] = datetime.datetime
    type_dict['native'] = bool  # 是否是真实的teacher？
    type_dict['from_id'] = ObjectId  # 虚拟老师专有，发源老师id，保持不连，除非修改
    type_dict['direction'] = str  # 虚拟老师专有，跟的方向，有三种 follow/reverse/random

    @classmethod
    def instance(cls, **kwargs):
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        if "name" not in kwargs:
            ms = "name必须"
            raise ValueError(ms)
        if "native" not in kwargs:
            ms = "native必须"
            raise ValueError(ms)
        return cls(**kwargs)

    @classmethod
    def rebuild(cls) -> None:
        """
        从交易信号中，初始化老师，如果你想重置所有的老师，请手动清空旧的老师列表,
        仅在初始化时候使用。
        :return:
        """
        f = dict()
        s = [("create_time", -1)]
        p = ['creator_id', 'creator_name', 'create_time']
        ses = mongo_db.get_conn(table_name="signal_info")
        args = {"filter": f, "sort": s, "projection": p}
        r = ses.find(**args)
        native = dict()
        for x in r:
            _id = ""
            try:
                _id = x['creator_id']
                name = x['creator_name']
            except KeyError as e:
                # print(e)
                # print(x)
                try:
                    name = x['updater_name']
                except KeyError as e:
                    print(e)
                    print(x)
            if isinstance(_id, str) and len(_id) == 24:
                _id = ObjectId(_id)
                if _id not in native:
                    native[_id] = name
                else:
                    prev_name = native[_id]
                    if prev_name == name:
                        pass
                    else:
                        ms = "新旧老师名字不一致：prev={}, now={}".format(prev_name, name)
                        raise ValueError(ms)
            else:
                ms = "异常的_id：{}".format(_id)
                print(ms)
        print(native)
        for k, v in native.items():
            t = {"_id": k, "name": v, "native": True}
            t1 = {"name": "{}_正向".format(v), "native": False, "from_id": k, "direction": "follow"}
            t2 = {"name": "{}_反向".format(v), "native": False, "from_id": k, "direction": "reverse"}
            t3 = {"name": "{}_随机".format(v), "native": False, "from_id": k, "direction": "random"}
            cls(**t).save_plus()
            cls(**t1).save_plus()
            cls(**t2).save_plus()
            cls(**t3).save_plus()


if __name__ == "__main__":
    """重建老师列表"""
    Teacher.rebuild()
    pass