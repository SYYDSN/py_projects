#  -*- coding: utf-8 -*-
from log_module import get_logger
import mongo_db

logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


class Signal(mongo_db.BaseDoc):
    """交易信号"""
    """


    """
    data = {'op': 'data_create',
            'data': {'_widget_1514518782557': '买入', '_widget_1514887799459': 1, '_widget_1514887799231': 121.19,
                     'deleteTime': None, '_widget_1516245169208': '非农', '_widget_1522117404041': 1090,
                     '_widget_1520843763126': 1190, 'formName': '发信号测试',
                     '_widget_1514518782504': '2018-03-29T21:40:19.000Z', 'label': '', '_widget_1514518782592': 120,
                     'createTime': '2018-03-29T21:41:21.491Z', 'appId': '5a45b8436203d26b528c7881',
                     '_widget_1522134222811': 100, '_widget_1514887799261': '保护利润，提前离场',
                     'updater': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'}, '_widget_1520843228626': 1000,
                     '_id': '5abd5d81493acc231b27af1c', 'creator': {'name': '徐立杰', '_id': '5a684c9b42f8c1bffc68f4b4'},
                     '_widget_1514518782603': [{'_widget_1514518782614': 121.21, '_widget_1514518782632': 119.11}],
                     'updateTime': '2018-03-29T21:41:21.491Z', '_widget_1514518782514': '原油',
                     'entryId': '5abc4febed763c754248e1cb', '_widget_1514518782842': 1190, 'deleter': None
                     }
            }
