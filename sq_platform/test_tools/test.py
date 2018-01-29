#  -*- coding: utf-8 -*-
import mongo_db
from uuid import uuid4
import datetime


class X(mongo_db.BaseDoc):
    _table_name = "test2"
    type_dict = dict()
    type_dict["_id"] = mongo_db.ObjectId
    type_dict['uuid'] = uuid4()
    type_dict['create_date'] = datetime.datetime

    def __init__(self, **kwargs):
        if "create_date"not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(X, self).__init__(**kwargs)


# for i in range(10):
#     xs = [X().to_flat_dict() for x in range(10000)]
#     X.insert_many(xs)
#     print(i)

x = X.find_one()
print(x)