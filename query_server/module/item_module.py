# -*- coding: utf-8 -*-
import os
import sys
__root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __root_path not in sys.path:
    sys.path.append(__root_path)
import orm_module
from pymongo import WriteConcern
from uuid import uuid4
import datetime


ObjectId = orm_module.ObjectId


class TempRecord(orm_module.BaseDoc):
    """测试类"""
    _table_name = "temp_record"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['sn'] = str

    def __init__(self, **kwargs):
        kw = dict()
        sn = kwargs.get('sn')
        kw['sn'] = uuid4().hex if sn is None else sn
        orm_module.BaseDoc.__init__(self, **kw)

    @classmethod
    def insert_mongodb(cls):
        """插入mongodb"""
        ses = cls.get_collection({"w": 0, "j": False})
        begin = datetime.datetime.now()
        for i in range(20):
            t = [cls().get_dict() for x in range(1000)]
            ses.insert(t)
        end = datetime.datetime.now()
        delta = (end - begin).total_seconds()
        print("mongodb (w0)分组插入2万条记录耗时 {}秒".format(delta))
        ses = cls.get_collection({"w": 1, "j": False})
        begin = datetime.datetime.now()
        for i in range(20):
            t = [cls().get_dict() for x in range(1000)]
            ses.insert(t)
        end = datetime.datetime.now()
        delta = (end - begin).total_seconds()
        print("mongodb (w1)分组插入2万条记录耗时 {}秒".format(delta))
        ses = cls.get_collection({"w": 'majority', "j": False})
        begin = datetime.datetime.now()
        for i in range(20):
            t = [cls().get_dict() for x in range(1000)]
            ses.insert(t)
        end = datetime.datetime.now()
        delta = (end - begin).total_seconds()
        print("mongodb (w:majority)分组插入2万条记录耗时 {}秒".format(delta))
        ses = cls.get_collection({"w": 1, "j": True})
        begin = datetime.datetime.now()
        for i in range(20):
            t = [cls().get_dict() for x in range(1000)]
            ses.insert(t)
        end = datetime.datetime.now()
        delta = (end - begin).total_seconds()
        print("mongodb (w1, j1)分组插入2万条记录耗时 {}秒".format(delta))
        ses = cls.get_collection({"w": 'majority', "j": True})
        begin = datetime.datetime.now()
        for i in range(20):
            t = [cls().get_dict() for x in range(1000)]
            ses.insert(t)
        end = datetime.datetime.now()
        delta = (end - begin).total_seconds()
        print("mongodb (w:majority, j1)分组插入2万条记录耗时 {}秒".format(delta))

    @classmethod
    def query_mongodb(cls):
        """mongodb查询测试"""
        f = {"sn": uuid4().hex}
        ses = cls.get_collection()
        begin = datetime.datetime.now()
        [ses.find_one(filter=f) for i in range(10000)]
        end = datetime.datetime.now()
        delta = (end - begin).total_seconds()
        print("mongodb 1万次查询记录耗时 {}秒".format(delta))

    @classmethod
    def mongodb_transaction(cls):
        """mongodb事务测试"""
        db = orm_module.get_client()
        begin = datetime.datetime.now()
        for i in range(1000):
            t1 = orm_module.get_conn(table_name='temp_record', db_client=db)
            t2 = orm_module.get_conn(table_name='t2', db_client=db)
            with db.start_session(causal_consistency=True) as ses:
                with ses.start_transaction():
                    t1.insert_one(document={"sn": uuid4().hex}, session=ses)
                    t2.insert_one(document={"sn": uuid4().hex}, session=ses)
        end = datetime.datetime.now()
        delta = (end - begin).total_seconds()
        print("mongodb 1000次事物操作耗时 {}秒".format(delta))





if __name__ == "__main__":
    pass