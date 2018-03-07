# -*- coding:utf8 -*-
from mongo_db import get_conn
from bson import regex


def insert_error_code(**kwargs):
    """插入错误代码"""
    ses = get_conn("error_code_info")
    inserted_id = ses.insert_one(kwargs).inserted_id
    return inserted_id


args = {"code": 7001,
        "description": "接口没有正确响应"}


print(insert_error_code(**args))




