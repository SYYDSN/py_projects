# -*- coding: utf-8 -*-
import os
import sys
__root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __root_path not in sys.path:
    sys.path.append(__root_path)
import orm_module
from pymongo import WriteConcern
from uuid import uuid4
from module.my_sql import sql_session as sql_con
from module.my_sql import structure_sql
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
    def test_query(cls, num: int = 1000, desc: str = None, write_concern: (dict, WriteConcern) = None) ->dict:
        """
        测试查询的速度.
        :param num: 查询次数
        :param desc: 备注
        :param write_concern: 写关注
        :return:
        {
        "num": 1000,
        }
        """
        max = 0
        min = 99999999
        col = cls.get_collection(write_concern=write_concern)
        for i in range(num):
            sn = uuid4().hex
            f = {"sn": sn}

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

    @classmethod
    def insert_mysql(cls):
        """插入mysql"""
        ses = sql_con()
        begin = datetime.datetime.now()
        for i in range(20):
            for x in range(1000):
                ses.execute(structure_sql(the_type='add', table_name='temp_record', sn=uuid4().hex))
            ses.commit()
        end = datetime.datetime.now()
        delta = (end - begin).total_seconds()
        print("mysql 分组插入2万条记录耗时 {}秒".format(delta))
        ses.close()
        # begin = datetime.datetime.now()
        # for i in range(20):
        #     for x in range(100):
        #         ses.execute(structure_sql(the_type='add', table_name='temp_record', sn=uuid4().hex))
        #         ses.commit()
        # end = datetime.datetime.now()
        # delta = (end - begin).total_seconds()
        # print("mysql 逐条插入10万条记录耗时 {}秒".format(delta))

    @classmethod
    def query_mysql(cls):
        """mysql查询测试"""
        sql = "select * from temp_record where sn='{}'".format(uuid4().hex)
        handler = sql_con()
        begin = datetime.datetime.now()
        [handler.execute(sql) for i in range(10000)]
        end = datetime.datetime.now()
        delta = (end - begin).total_seconds()
        print("mysql 1万次查询记录耗时 {}秒".format(delta))
        handler.close()

    @classmethod
    def mysql_transaction(cls):
        """mysql事物测试"""

        begin = datetime.datetime.now()
        for i in range(1000):
            handler = sql_con()
            sql1 = structure_sql(the_type='add', table_name='temp_record', sn=uuid4().hex)
            sql2 = structure_sql(the_type='add', table_name='t2', sn=uuid4().hex)
            handler.execute(sql1)
            handler.execute(sql2)
            handler.commit()
            handler.close()
        end = datetime.datetime.now()
        delta = (end - begin).total_seconds()
        print("mysql 1000次事物操作耗时 {}秒".format(delta))




if __name__ == "__main__":
    TempRecord.mongodb_transaction()
    TempRecord.mysql_transaction()
    pass