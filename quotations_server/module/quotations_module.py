# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
from flask import request
import json
import datetime
from flask_socketio import SocketIO
from log_module import get_logger


ObjectId = mongo_db.ObjectId
logger = get_logger()


"""行情模块"""


class Quotation(mongo_db.BaseDoc):
    """
    行情报价信息
    """
    _table_name = "quotation"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['platform_name '] = str # 平台名称
    type_dict['platform_account'] = str
    type_dict['platform_time'] = datetime.datetime  # 报价时间
    type_dict['code'] = str  # 产品代码
    type_dict['product'] = str  # 产品名称
    type_dict['price'] = float  # 报价
    type_dict['receive_time'] = datetime.datetime  # 报价收到时间,用于和platform_time比对评估延时

    @classmethod
    def analysis_request(cls, req: request, auto_save: bool = False) -> (list, None):
        """
        从一个flask的request中分析发送来的信息,符合标准的化,就返回一个本类初始化字典(多条报价)组成的.
        否则返回None
        :param req:
        :param auto_save:  auto_save 是否需要保存实例?
        :return:
        """
        now = datetime.datetime.now()
        form = req.form
        form = {k: v for k, v in form.items()}
        platform_name = form.get("platform_name", "")
        if platform_name == "":
            platform_name = form.get("platform_name ", "")
        platform_account = form.get("platform_account", "")
        platform_time = form.get("platform_time", now)
        platform_time = platform_time.replace(".", "-") if isinstance(platform_time, str) else platform_time
        platform_time = mongo_db.get_datetime_from_str(platform_time) if isinstance(platform_time, str) \
            else platform_time
        r = {
            "platform_name": platform_name,
            "platform_account": platform_account,
            "platform_time": platform_time,
            "receive_time": now
        }
        prices = form.pop('data', '')
        if prices == '':
            res = None
        else:
            t1 = [[y for y in x.split("*")] for x in prices.split("^")]
            res = list()
            res2 = list()
            for x in t1:
                if len(x) >= 3:
                    temp = {"code": x[0], "product": x[1], "price": float(x[2])}
                    temp2 = {"code": x[0], "product": x[1], "price": float(x[2]), "_id": ObjectId()}
                    temp.update(r)
                    temp2.update(r)
                    res.append(temp)
                    res2.append(temp2)
            if auto_save:
                ses = cls.get_collection()
                ses.insert_many(documents=res2)
            else:
                pass
        return res

    @classmethod
    def send_io_message(cls, init_list: list, event: str, io: SocketIO) -> None:
        """
        使用socketio,向所有的客户端发送报价.
        :param init_list:  类初始化字典的数组(报价是一批一批来的)
        :param event:      事件名
        :param io:         socketio实例

        :return:
        """
        mes = [mongo_db.to_flat_dict(x) for x in init_list]
        data = json.dumps(mes)
        io.emit(event=event, data=data)