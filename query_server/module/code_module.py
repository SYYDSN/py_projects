# -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
import datetime
from log_module import get_logger


"""
条码模块
"""


logger = get_logger()
ObjectId = orm_module.ObjectId
cache = orm_module.RedisCache()


def set_code_length(length: int = 0) -> int:
    """
    设置标准条码长度. 默认35
    :param length:
    :return:
    """
    if length == 0:
        """从数据库查询"""
        col = orm_module.get_conn(table_name="company_info")
        r = col.find_one()
        if isinstance(r, dict):
            length = r.get("code_length", 35)
        else:
            length = 35
    else:
        pass
    key = "standard_code_length"
    cache.set(key=key, value=length, timeout=43200)  # 12小时缓存
    return length


def get_code_length() -> int:
    """
    获取标准条码长度
    :return:
    """
    key = "standard_code_length"
    length = cache.get(key=key)
    if length is None:
        length = set_code_length()
    else:
        pass
    return length


class SocketListener(orm_module.BaseDoc):
    """
    socket(tcp)请求监听器
    """
    _table_name = "socket_record"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['request'] = str
    type_dict['response'] = str
    type_dict['client_ip'] = str
    type_dict['client_port'] = int
    type_dict['time'] = datetime.datetime

    @classmethod
    def log(cls, req: str, resp, ip: str, port: (int, str)) -> None:
        """
        记录日志
        :param req: tcp客户端请求的字符串格式
        :param resp: 响应的字符串格式
        :param ip:  客户ip
        :param port: 客户端端口
        :return:
        """
        now = datetime.datetime.now()
        doc = {
            "request": req, "response": resp, "client_id": ip, 'client_port': port,
            "time": now
        }
        write_concern = orm_module.get_write_concern()
        col = cls.get_collection(write_concern=write_concern)
        r = None
        try:
            r = col.insert_one(document=doc)
        except Exception as e:
            logger.exception(msf=e)
        finally:
            if r is None:
                ms = "{}: SocketListener.log未能返回正确的插入结果, doc={}".format(now, doc)
                logger.exception(ms)
            else:
                pass

    @classmethod
    def listen(cls, mes: str, ip: str, port: (int, str)) -> str:
        """
        监听Tcp通讯
        :param mes: tcp客户端请求的字符串格式
        :param ip:  客户ip
        :param port: 客户端端口
        :return: 响应的字符串格式
        """
        try:
            port = int(port)
        except Exception as e:
            print(e)
        finally:
            if mes.startswith("CheckTraceCodeCanUse"):
                """
                条码合格判定
                请求检测数据是否合格: CheckTraceCodeCanUse, 10401911001201805011536541033317
                系统检测条码合格返回数据格式: 10401911001201805011536541033317,1    
                系统检测条码重复返回数据格式: 10401911001201805011536541033317,2 
                系统检测条码非当前生产数据格式: 10401911001201805011536541033317,3 
                系统检测条码格式错误: 10401911001201805011536541033317,4 
                条码加请求检测结果后的返回值，返回值为以上定义的 1-4数据。
                """
                code = mes.split(",")[-1].strip("")
                r = CodeInfo.query_code(code=code)
                resp = '{},{}'.format(code, r)
            elif mes.startswith("UploadTraceCodeToDb"):
                """
                UploadTraceCodeToDb
                请求检测数据是否合格: UploadTraceCodeToDb, 10401911001201805011536541033317, 
                10401911001201805011536541033318, 10401911001201805011536541033319, 
                10401911001201805011536541033311, 10401911001201805011536541033312,
                ……
                系统检测条码合格返回数据格式: UploadTraceCodeToDb ,10401911001201805011536541033317,1
                系统数据返回格式解释: 用请求的接口名，加第一个请求的条码内容，加结果。
                1. 代表本次请求接口处理成功，0则代表本次接口处理数据失败。
                """
                resp = "UploadTraceCodeToDb api not implemented!"
            else:
                resp = 'not implemented data={}！\n'.format(mes)

            """记录结果"""
            cls.log(req=mes, resp=resp, ip=ip, port=port)
            return resp


class CodeInfo(orm_module.BaseDoc):
    """条码信息"""
    _table_name = "code_info"
    type_dict = dict()
    type_dict['_id'] = str  # 条码的码
    type_dict['product_id'] = ObjectId  # 产品id
    type_dict['print_id'] = ObjectId   # 打印批次id
    type_dict['file_id'] = ObjectId     # 导入时的文件id
    """
    status标识状态:
    -1 标记作废
    0 未使用
    1 已使用
    """
    type_dict['status'] = int               # 默认是0
    type_dict['time'] = datetime.datetime   # 使用时间,可能为空

    @classmethod
    def get_threshold(cls) -> dict:
        """
        获取公司的空白库存最低阈值和已打印可用条码阈值
        :return:
        """
        res = {"inventory_threshold": None, "printed_threshold": None}
        col = orm_module.get_conn(table_name="company_info")
        r = col.find_one(filter=dict())
        if r is None:
            pass
        else:
            res['inventory_threshold'] = r.get("inventory_threshold")
            res['printed_threshold'] = r.get("printed_threshold")
        return res

    @classmethod
    def query_code(cls, code: str) -> int:
        """
        查询条码
        系统检测条码合格返回数据格式: 1
        系统检测条码重复返回数据格式: 2
        系统检测条码非当前生产数据格式: 3  条码没有打印过.
        系统检测条码格式错误: 4  条码长度不够.
        :param code:
        :return:
        """
        res = 4
        f = {"_id": code}
        r = cls.find_one(filter_dict=f)
        if r is None:
            pass
        else:
            r.get("used")
            if r == 0:
                res = 0
            else:
                res = 1
        return res




if __name__ == "__main__":
    pass
