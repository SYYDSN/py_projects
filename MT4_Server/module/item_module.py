#  -*- coding: utf-8 -*-
from log_module import get_logger
from send_moudle import *
import mongo_db
import datetime
from flask import request
from tools_module import get_real_ip


logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


class RawRequestInfo(mongo_db.BaseDoc):
    """
    原始请求信号的记录,注意，没有记录请求中的files参数
    """
    _table_name = "raw_request_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['ip'] = str
    type_dict['path'] = str
    type_dict['args'] = dict
    type_dict['form'] = dict
    type_dict['json'] = dict
    type_dict['headers'] = dict
    type_dict['event_date'] = datetime.datetime

    def __init__(self, **kwargs):
        if "event_date" not in kwargs:
            kwargs['event_date'] = datetime.datetime.now()
        super(RawRequestInfo, self).__init__(**kwargs)

    @classmethod
    def instance(cls, req: request) -> object:
        """
        生成一个实例
        :param req: flask.request
        :return: cls()
        """
        args = dict()
        args['ip'] = get_real_ip(req)
        args['path'] = req.path
        args['args'] = {k: v for k, v in req.args.items()}
        args['form'] = {k: v for k, v in req.form.items()}
        args['json'] = request.json
        args['headers'] = {k: v for k, v in req.headers.items()}
        instance = cls(**args)
        return instance

    @classmethod
    def record(cls, req: request) -> None:
        """
        记录原始的请求
        :param req:
        :return:
        """
        instance = cls.instance(req)
        instance.save_plus()


if __name__ == "__main__":

    pass
