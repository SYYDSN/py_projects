# -*- coding: utf-8 -*-
import orm_module
import datetime


ObjectId = orm_module.ObjectId


class User(orm_module.BaseDoc):
    _table_name = "user_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_name'] = str
    type_dict['age'] = int
    type_dict['time'] = datetime.datetime


if __name__ == "__main__":
    kw = {
        "user_name": "李四",
        'age': 12,
        "dict": {"name": "sds", "l":[1,2,3,4,5]},
        "time": datetime.datetime.now()
    }
    User.insert_one(doc=kw)
    pass