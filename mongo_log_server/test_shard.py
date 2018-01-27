# -*- coding: utf-8 -*-
import mongo_db
from uuid import uuid4


"""测试分片效果"""


class TestA(mongo_db.BaseDoc):
    _table_name = "testa_info"
    type_dict = dict()
    type_dict["_id"] = mongo_db.ObjectId
    type_dict['count'] = int
    type_dict['uuid'] = str


class TestB(mongo_db.BaseDoc):
    _table_name = "testb_info"
    type_dict = dict()
    type_dict["_id"] = mongo_db.ObjectId
    type_dict['count'] = int
    type_dict['uuid'] = str


if __name__ == "__main__":
    """大量的顺序写测试"""
    # ran = 10 * 10
    # temp_a = list()
    # for x in range(ran):
    #     u = uuid4().hex
    #     t_1 = {"_id": mongo_db.ObjectId(), "count": x, "uuid": u}
    #     temp_a.append(t_1)
    #     if x % 1 == 0 and x != 0:
    #         TestA.insert_many(temp_a)
    #         TestB.insert_many(temp_a)
    #         temp_a = list()
    #         print(x)
    """多线程写测试"""
    from threading import Thread
    import datetime
    from bson.objectid import ObjectId
    count = 0
    def counter(begin_datetime: datetime.datetime, max_count: int):
        global count
        count += 1
        if count == max_count:
            """全部多线程运行完毕"""
            now = datetime.datetime.now()
            seconds = (now - begin_datetime).total_seconds()
            print(seconds)

    def save_x(i, begin, max_count):
        t = {"_id": mongo_db.ObjectId(), "count": i, "uuid": uuid4().hex}
        t = TestA(**t)
        t.save()
        print("{} is ok".format(i))
        counter(begin, max_count)
    b = datetime.datetime.now()
    num = 10
    for x in range(num):
        th = Thread(target=save_x, args=(x, b, num), daemon=False)
        th.start()
