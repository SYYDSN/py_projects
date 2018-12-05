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


logger = get_logger("条码查询")
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
    type_dict['task_id'] = ObjectId  # 生产任务id,ProduceTask._id 和product_id有数据冗余,可以检验是否当前生产数据
    type_dict['print_id'] = ObjectId   # 打印批次id PrintCode._id
    type_dict['file_id'] = ObjectId     # 导入时的文件id  UploadFile._id
    type_dict['level'] = int     # 条码的级别,只是在最后回传结果的时候才能确定.
    """
    status标识状态:
    -1 标记作废
    0 未使用
    1 已使用
    """
    type_dict['status'] = int               # 默认是0
    type_dict['time'] = datetime.datetime   # 使用时间,可能为空

    @classmethod
    def deposit(cls, product_id: ObjectId, printed: bool = False) -> int:
        """
        统计可用条码余量
        :param product_id:
        :param printed:  是统计已打印的条码还是统计未打印的条码?
        :return:
        """
        match = {
            "$match":
                {
                    "product_id": product_id,
                    "print_id": {"$exists": printed}
                }
        }
        projection = {"$project": {"_id": 1}}
        count = {"$count": "total"}
        pipeline = [match, projection, count]
        col = cls.get_collection()
        r = col.aggregate(pipeline=pipeline)
        r = [x for x in r]
        return 0 if len(r) == 0 else r[0]['total']

    @classmethod
    def query_code(cls, code: str) -> int:
        """
        查询条码
        系统检测条码合格返回数据格式: 1
        系统检测条码重复返回数据格式: 2
        系统检测条码非当前生产数据格式: 3  条码没有打印过或者条码关联的产品id和生产任务中的产品id不符..
        系统检测条码格式错误: 4  条码长度不够.
        :param code:
        :return:
        """
        res = 4
        threshold = get_code_length()
        if len(code) != threshold:
            pass
        else:
            debug = True   # 当前保持测试模式
            begin = datetime.datetime.now()
            f = {"_id": code}
            if debug:
                """测试模式"""
                r = cls.find_one(filter_dict=f)
                if r is None:
                    """没有查询到"""
                    res = 3
                else:
                    status = r.get("status", -1)
                    print_id = r.get("print_id", None)
                    if isinstance(print_id, ObjectId):
                        if status == 0:
                            res = 1
                        elif status == -1:
                            res = 3
                        else:
                            res = 2
                    else:
                        """条码未打印"""
                        res = 3
            else:
                """生产模式"""
            db_client = orm_module.get_client()
            write_concern = orm_module.get_write_concern()
            col = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client, write_concern=write_concern)
            with db_client.start_session(causal_consistency=True) as ses:
                with ses.start_transaction(write_concern=write_concern):
                    r = col.find_one(filter=f)
                    if r is None:
                        """没有查询到"""
                        res = 3
                    else:
                        status = r.get("status", -1)
                        print_id = r.get("print_id", None)
                        if isinstance(print_id, ObjectId):
                            if status == 0:
                                res = 1
                                """标记当前条码已被使用"""
                                u = {"$set": {"status": 1}}
                                return_document = orm_module.ReturnDocument.AFTER
                                r2 = col.find_one_and_update(filter=f, update=u, return_document=return_document)
                                if r2 is None:
                                    ms = "标记已用条码时出错,已用标记未写入, 条码: {}".format(code)
                                    logger.exception(msg=ms)
                                else:
                                    pass
                            elif status == -1:
                                res = 3
                            else:
                                res = 2
                        else:
                            """条码未打印"""
                            res = 3
            end = datetime.datetime.now()
            ms = (end - begin).total_seconds()
            print(ms)
        return res


if __name__ == "__main__":
    # CodeInfo.query_code("23132104307180149268677481490882207")
    CodeInfo.deposit(product_id=ObjectId("5c00f2659f0a5e2ed772fd97"))
    pass
