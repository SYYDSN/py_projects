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
from tools_module import get_real_ip
from flask_socketio import SocketIO
from log_module import get_logger


ObjectId = mongo_db.ObjectId
logger = get_logger()
"""
        "英镑": {"platform_name": "Xinze Group Limited", "code": "GBPUSD"},
        "加元": {"platform_name": "Xinze Group Limited", "code": "USDCAD"},
        "澳元": {"platform_name": "Xinze Group Limited", "code": "AUDUSD"},
        "日元": {"platform_name": "Xinze Group Limited", "code": "USDJPY"},
        "欧元": {"platform_name": "Xinze Group Limited", "code": "EURUSD"},
        "恒指": {"platform_name": "Xinze Group Limited", "code": "HK50"},
        "原油": {"platform_name": "Xinze Group Limited", "code": "XTIUSD"},
        "白银": {"platform_name": "Xinze Group Limited", "code": "XAGUSD"},
        "黄金": {"platform_name": "Xinze Group Limited", "code": "XAUUSD"},
        "测试": {"platform_name": "Xinze Group Limited", "code": "XAGUSD"}
"""
p_map = {
    "Xinze Group Limited": {
        "GBPUSD": {"product": "英镑", "code": "GBPUSD"},
        "USDCAD": {"product": "加元", "code": "USDCAD"},
        "AUDUSD": {"product": "澳元", "code": "AUDUSD"},
        "USDJPY": {"product": "日元", "code": "USDJPY"},
        "EURUSD": {"product": "欧元", "code": "EURUSD"},
        "HK50": {"product": "恒指", "code": "HK50"},
        "XTIUSD": {"product": "原油", "code": "XTIUSD"},
        "XAGUSD": {"product": "白银", "code": "XAGUSD"},
        "XAUUSD": {"product": "黄金", "code": "XAUUSD"}
    }
}


"""行情模块"""


def transform_product(raw_dict: dict) -> (dict, None):
    """
    根据报价的代码批量将产品的商品名称，转换成自有的产品名称。
    :param raw_dict: 产品报价的dict
    :return: 转换后的list
    """
    p = raw_dict.get("platform_name")
    c = raw_dict.get("code")
    map1 = p_map.get(p)
    if map1 is None:
        pass
    else:
        temp = map1.get(c)
        if temp is None:
            pass
        else:
            raw_dict['product'] = temp['product']
            raw_dict['code'] = temp['code']
            return raw_dict


class RawRequestInfo(mongo_db.BaseDoc):
    """
    原始请求信号的记录,注意，没有记录请求中的files参数,可用来监听任意request,
    目前的用途:
    1. 监听交易平台发过来的消息  2018-6-29
    """
    _table_name = "raw_request_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['server'] = str
    type_dict['ip'] = str
    type_dict['url'] = str
    type_dict['path'] = str
    type_dict['args'] = dict
    type_dict['form'] = dict
    type_dict['json'] = dict
    type_dict['headers'] = dict
    type_dict['time'] = datetime.datetime

    def __init__(self, **kwargs):
        if "event_date" not in kwargs:
            kwargs['event_date'] = datetime.datetime.now()
        super(RawRequestInfo, self).__init__(**kwargs)

    @classmethod
    def get_init_dict(cls, req: request) -> dict:
        """
        从request中获取初始化字典.
        :param req:
        :return:
        """
        headers = {k: v for k, v in req.headers.items()}
        args = {k: v for k, v in req.args.items()}
        form = {k: v for k, v in req.form.items()}
        json_data = None if req.json is None else (req.json if isinstance(req.json, dict) else json.loads(req.json))
        ip = get_real_ip(req)
        now = datetime.datetime.now()
        args = {
            "ip": ip,
            "method": req.method.lower(),
            "url": req.url,
            "path": req.path,
            "headers": headers,
            "args": args,
            "form": form,
            "json": json_data,
            "time": now
        }
        return args

    @classmethod
    def instance(cls, req: request):
        """
        生成一个实例
        :param req: flask.request
        :return: 实例
        """
        args = cls.get_init_dict(req=req)
        instance = cls(**args)
        return instance

    @classmethod
    def record(cls, req: request) -> ObjectId:
        """
        记录原始的请求
        :param req:
        :return:
        """
        instance = cls.instance(req)
        return instance.save_plus()


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
                insert_res = ses.insert_many(documents=res2)
                print(insert_res)
            else:
                pass
        return res

    @classmethod
    def analysis(cls, data_str: str) -> list:
        """
        从一个flask的request的data中分析发送来的信息的list
        这个函数是用来检查发送来的信息格式的。不用于生产环境
        :param data_str:
        :return:
        """
        res = list()
        if isinstance(data_str, str) and len(data_str) > 10:
            prices = data_str
            t1 = [[y for y in x.split("*")] for x in prices.split("^")]
            for x in t1:
                if len(x) >= 3:
                    temp = {"code": x[0], "product": x[1], "price": float(x[2])}
                    res.append(temp)
                else:
                    print("不合格的报价字段：{}".format(x))
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
        mes = [mongo_db.to_flat_dict(transform_product(x)) for x in init_list if transform_product(x) is not None]
        data = json.dumps(mes)
        io.emit(event=event, data=data)


class ProviderStatus(mongo_db.BaseDoc):
    """
    报价提供者(提供报价的服务器/应用程序)(在线/工作)状态
    """


class KLine(mongo_db.BaseDoc):
    """
    :k线数据，从5分钟开始。
    """


if __name__ == "__main__":
    d = "USDCHF*美元兑瑞郎*0.99120^GBPUSD*英镑兑美元*1.27945^EURUSD*欧元兑美元*1.14802^USDJPY*美元兑日元*110.071" \
        "^USDCAD*美元兑加元*1.30425^AUDUSD*澳元兑美元*0.73370^EURGBP*欧元兑英镑*0.89714^EURAUD*欧元兑澳元*1.56436^" \
        "EURJPY*欧元兑日元*126.368^CADJPY*加元兑日元*84.380^GBPJPY*英镑兑日元*140.834^AUDNZD*澳元兑纽元*1.10404^AUDCAD*" \
        "澳元兑加元*0.95694^AUDCHF*澳元兑瑞郎*0.72719^AUDJPY*澳元兑日元*80.759^CHFJPY*瑞郎兑日元*111.025^" \
        "XAUUSD*黄金*1190.24^XAGUSD*白银*14.735^"
    q1 = {
    "_id" : ObjectId("5b80427e6a090e5fb296b963"),
    "platform_time" : "2018-08-25T01:38:05.000Z",
    "price" : 68.74,
    "product" : "原油",
    "platform_account" : "8300140",
    "platform_name" : "Xinze Group Limited",
    "code" : "XTIUSD",
    "receive_time" : "2018-08-25T01:38:06.381Z"
    }
    r = Quotation.send_io_message([q1], "aaa", "a")
    print(r)
    pass