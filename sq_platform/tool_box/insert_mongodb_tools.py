# -*- coding:utf8 -*-
from mongo_db import get_conn
from mongo_db import ObjectId
from mongo_db import DBRef
from api.user.violation_module import ViolationQueryResult
from api.user.item_module import CarLicense


def insert_error_code(**kwargs):
    """插入错误代码"""
    ses = get_conn("error_code_info")
    inserted_id = ses.insert_one(kwargs).inserted_id
    return inserted_id


args = {"code": 5001,
        "description": "文件写入磁盘失败"}


print(insert_error_code(**args))


