# -*- coding:utf8 -*-
from mongo_db import get_conn
from mongo_db import ObjectId
from mongo_db import DBRef
from api.data.violation_module import ViolationQueryResult
from api.data.item_module import CarLicense


def insert_error_code(**kwargs):
    """插入错误代码"""
    ses = get_conn("error_code_info")
    inserted_id = ses.insert_one(kwargs).inserted_id
    return inserted_id


args = {"code": 3018,
        "description": "约定的图片名未在本次请求或图片名与约定不一致"}


print(insert_error_code(**args))


