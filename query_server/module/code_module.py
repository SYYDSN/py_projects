# -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
import datetime
import json
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
            code = mes.split(",")[-1].strip()
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
                r = CodeInfo.query_code(code=code)
                resp = '{},{}'.format(code, r)
            elif mes.startswith("reset_code"):
                """重设条码"""
                r = CodeInfo.reset_cord(code)
                resp = '{},{}'.format(code, r)
            elif mes.startswith("apply_code"):
                """申请条码"""
                resp = CodeInfo.apply_code(old_id=code)
            elif mes.startswith("code_details"):
                """查询条码详情"""
                resp = CodeInfo.code_details(code=code)
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
    """
    条码信息
    条码信息所能执行的查询服务如下:
    1. 条码比对: 嵌入式向服务器发送一条条码信息,服务器在数据库中进行查询:
            prefix: CheckTraceCodeCanUse
            如果条码信息status为0,且print_id不为空.表示条码信息可用.置此条码的status=1.返回1.
            如果码信息status为1,返回2, 表示这个条码已被使用
            如果码信息有查询到但是print_id为空.返回3. 条码没有打印过.
            如果码信息status为-1或者没有查询到对应的条码.返回4. 表示此条码无效.
    2. 条码重置: 嵌入式向服务器发出重置一条条码信息的请求:
            prefix: reset_code
            如果此条码status=1, print_id存在. 服务器修改此条码的status=0.返回值1. 表示重置成功
            如果此条码status=0, print_id存在. 返回值0. 表示此条码无需重置.
            如果此条码如果查询不到此条码. 返回值2.  表示此条码不存在
            如果此条码如果查询到此条码.  print_id不存在,返回值3.  表示此条码尚未打印
            如果程序执行出错.返回 -1
    3. 条码替换: 嵌入式向服务器发出一条替换条码的信息,信息中顺序包含A和B两个条码. 意思是用B条码替换A条码的位置.
            <1>. 如果 .A条码的status=1, print_id存在.且 B条码status=0, print_id存在.那么服务器将执行以下操作后返回1:
                 1).设置A条码的status=0.B条码的status=1.
                 2).如果A条码有parent_id,那么设置B.patent_id=A.parent_id
                 3).搜寻数据库中,parent_id=A._id的条码,修改这些条码的parent_id=B._id
            <2>. 如果 .A条码的status=1, print_id存在.且 B条码status=1, print_id存在.返回0.表示B条码已使用.
            <3>. 如果 .A条码的status=1, print_id存在.且 B条码print_id不存在.返回2.表示B条码不可用.
            <4>. 如果 .A条码的status=0, print_id存在.返回3.表示A条码无需替换
            <5>. 如果 .A条码的print_id不存在.返回4.表示A条码未打印
            <6>. 如果 .A条码不存在.返回5.表示A条码未打印
            如果程序执行出错.返回 -1
    4. 临时申请条码: 此操作用于将一条未打印的条码标记为已打印状态并返回给嵌入式设备.
       嵌入式设备需要发送一个产品id给服务端(服务端会提供一个查询产品信息的接口)
            服务器会选择一个未打印的条码A. 标记A的print_id为None,product_id为P._id. 同时返回 A.表示申请成功.
            如果旧条码无效或者没有有效的产品信息.返回 1
            无对应产品的空白条码,返回 0
            如果程序执行出错.返回 -1
            注意,此步骤嵌入式需要考虑如何将临时申请的条码传给标签打印机
    5. 数据回传: 在一天的工作结束后,嵌入式会回传当天的工作数据:
            单个条码结构的组织形式是: {"code": 123349439122834434, "level": 2, "children": []}这样的形式.children字段可以不存在.
            多个条码的组织形式[
                             {
                              "code": 1234, "level: 3,                                   # 三级码信息
                              "children": [
                                            {
                                              "code": 1235, "level: 2,                   # 二级码信息
                                              "children":[
                                                            {"code": 1236, "level: 1},   # 一级码信息
                                                            {"code": 1237, "level: 1},
                                                            ......
                                                        ]
                                            },
                                            {
                                              "code": 1238, "level: 2,                   # 二级码信息
                                              "children":[
                                                            {"code": 1239, "level: 1},   # 一级码信息
                                                            {"code": 1240, "level: 1},
                                                            ......
                                                        ]
                                            },
                                            ......
                                        ]
                              },
                             ......
                            ]
            最如该条码是一级条码的话. level字段也可以省略.就像这样:
                    [
                             {
                              "code": 1234, "level: 3,                                   # 三级码信息
                              "children": [
                                            {
                                              "code": 1235, "level: 2,                   # 二级码信息
                                              "children":[
                                                            {"code": 1236},              # 一级码信息
                                                            {"code": 1237},
                                                            ......
                                                        ]
                                            },
                                            {
                                              "code": 1238, "level: 2,                   # 二级码信息
                                              "children":[
                                                            {"code": 1239},              # 一级码信息
                                                            {"code": 1240},
                                                            ......
                                                        ]
                                            },
                                            ......
                                        ]
                              },
                             ......
                            ]
            你还可以进一步省略.把一级条码直接简化成字符串的格式:
                            [
                             {
                              "code": 1234, "level: 3,                                   # 三级码信息
                              "children": [
                                            {
                                              "code": 1235, "level: 2,                   # 二级码信息
                                              "children":[
                                                          1236,                          # 一级码信息
                                                          1237,
                                                            ......
                                                        ]
                                            },
                                            {
                                              "code": 1238, "level: 2,                   # 二级码信息
                                              "children":[
                                                            1239,                        # 一级码信息
                                                            1240,
                                                            ......
                                                        ]
                                            },
                                            ......
                                        ]
                              },
                             ......
                            ]
            当然,这些格式需要嵌入式和服务端进行约定后,选择其中的一种结构进行数据组织.切不可在同一文件内部混用不同的组织格式.
            嵌入式按照层级关系,把当日工作的条码信息组织成json格式,保存成以.json为后缀的文件饭后使用文件上传的方式(一般是http协议,
            post方法)上传给服务器.强烈建议嵌入式对此文件压缩成zip格式后再传输.可以降低越10倍上下的文件体积.
            服务器在收到此文件后,解压(如果是zip文件的话),解析json文件.然后进行如下的操作:
                1. 在数据库中标记这些数据的status和level字段.如果有任何出入.在日志中记录.
                2. 将导入的数据使用列表显示.用户手动把导入记录和生产任务进行关联.
                3. 如果数据解析失败.会在同步任务的列表中显示.用户可以点击查看错误提示并下载此文件查看分析失败原因
    """
    _table_name = "code_info"
    type_dict = dict()
    type_dict['_id'] = str  # 条码的码
    type_dict['product_id'] = ObjectId  # 产品id
    type_dict['task_id'] = ObjectId  # 生产任务id,ProduceTask._id 和product_id有数据冗余,可以检验是否当前生产数据
    type_dict['print_id'] = ObjectId   # 打印批次id PrintCode._id
    type_dict['file_id'] = ObjectId     # 导入时的文件id  UploadFile._id
    type_dict['sync_id'] = ObjectId     # 嵌入式回传结果时的文件id  TaskSync._id
    type_dict['output_id'] = ObjectId     # 到处生产结果时的文件id  OutputCode._id
    type_dict['parent_id'] = str     # 父级条码的id,顶层箱码没有这一项或者为null. 注意这个类型是字符串
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
    def can_output(cls, product_id: ObjectId) -> int:
        """
        统计可导出的条码(已完成生产)数量
        :param product_id:
        :return:
        """
        match = {
            "$match":
                {
                    "product_id": product_id,
                    "status": 1,
                    "sync_id": {"$type": "objectId"},
                    "output_id": {"$exists": False}
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
        查询条码, 这个方法是给tcp服务端接收嵌入式请求用的
        如果条码信息status为0,且print_id不为空.表示条码信息可用.置此条码的status=1.返回1.
        如果码信息status为1,返回2, 表示这个条码已被使用
        如果码信息有查询到但是print_id为空.返回3. 条码没有打印过.
        如果码信息status为-1或者没有查询到对应的条码.返回4. 表示此条码无效.
        :param code:
        :return:
        """
        res = 4
        debug = False   # 当前保持测试模式
        begin = datetime.datetime.now()
        f = {"_id": code}
        if debug:
            """测试模式"""
            r = cls.find_one(filter_dict=f)
            if r is None:
                """没有查询到"""
                pass
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
                        """没有查询到条码信息"""
                        pass
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

    @classmethod
    def reset_cord(cls, code: str) -> int:
        """
        重置条码,这个方法是给tcp服务端接收嵌入式请求用的
        如果此条码status=1, print_id存在. 服务器修改此条码的status=0.返回值1. 表示重置成功
        如果此条码status=0, print_id存在. 返回值0. 表示此条码无需重置.
        如果此条码如果查询不到此条码. 返回值2.  表示此条码不存在
        如果此条码如果查询到此条码.  print_id不存在,返回值3.  表示此条码尚未打印
        如果程序执行出错.返回 -1
        :param code:
        :return:
        """
        f = {"_id": code}
        db_client = orm_module.get_client()
        col = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client)
        w = orm_module.get_write_concern()
        with db_client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=w):
                r1 = col.find_one(filter=f, session=ses)
                if r1 is None:
                    resp = 2
                else:
                    if r1.get("print_id") is None:
                        resp = 3
                    else:
                        if r1.get("status", 0) == 1:
                            u = {"$set": {"status": 0}}
                            r2 = col.find_one_and_update(filter=f, update=u, session=ses)
                            if isinstance(r2, dict):
                                resp = 1
                            else:
                                resp = -1
                        else:
                            resp = 0
        return resp

    @classmethod
    def replace_code(cls, code_a: str, code_b: str) -> int:
        """
        条码替换,这个方法是给tcp服务端接收嵌入式请求用的
         嵌入式向服务器发出一条替换条码的信息,信息中顺序包含A和B两个条码. 意思是用B条码替换A条码的位置.
            如果 .A条码的status=1, print_id存在.且 B条码status=0, print_id存在.那么服务器将执行以下操作后返回1:
                 1).设置A条码的status=0.B条码的status=1.
                 2).如果A条码有parent_id,那么设置B.patent_id=A.parent_id
                 3).搜寻数据库中,parent_id=A._id的条码,修改这些条码的parent_id=B._id
            如果 .A条码的status=1, print_id存在.且 B条码status=1, print_id存在.返回0.表示B条码已使用.
            如果 .A条码的status=1, print_id存在.且 B条码print_id不存在.返回2.表示B条码不可用.
            如果 .A条码的status=0, print_id存在.返回3.表示A条码无需替换
            如果 .A条码的print_id不存在.返回4.表示A条码未打印
            如果 .A条码不存在.返回5.表示A条码未打印
            如果程序执行出错.返回 -1
        :param code_a: 原来的条码
        :param code_b: 用于替换的条码
        :return:
        """
        db_client = orm_module.get_client()
        col = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client)
        w = orm_module.get_write_concern()
        with db_client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=w):
                f = {"_id": code_a}
                r1 = col.find_one(filter=f, session=ses)
                if r1 is None:
                    resp = 5
                else:
                    if r1.get("print_id") is None:
                        resp = 4
                    else:
                        if r1.get("status", 0) == 0:
                            resp = 3
                        else:
                            r2 = col.find_one(filter={"_id": code_b})
                            if r2.get("print_id") is None:
                                resp = 2
                            else:
                                if r2.get("status", 0) == 1:
                                    resp = 0
                                else:
                                    f3 = {"_id": code_a}
                                    u3 = {"$set": {"status": 0}}
                                    f4 = {"_id": code_b}
                                    parent_id = r1.get("parent_id")
                                    if parent_id is None:
                                        u4 = {"$set": {"status": 1}}
                                    else:
                                        u4 = {"$set": {"status": 1, "parent_id": parent_id}}
                                    r3 = col.update_many(filter=f3, update=u3)
                                    r4 = col.update_many(filter=f4, update=u4)
                                    if r3 is None or r4 is None:
                                        resp = -1
                                    else:
                                        """更新code_a的children的parent_id"""
                                        f5 = {"parent_id": code_a}
                                        u5 = {"$set": {"parent_id": code_b}}
                                        col.update_many(filter=f5, update=u5)
                                        resp = 1
        return resp

    @classmethod
    def apply_code(cls, old_id: str) -> (int, str):
        """
        临时申请条码.这个方法是给tcp服务端接收嵌入式请求用的
        临时申请条码: 此操作用于将一条未打印的条码标记为已打印状态并返回给嵌入式设备.
        嵌入式设备需要发送一个用过的条码给服务端
        服务器会选择一个未打印的条码A. 标记A的print_id为None,old_id.product_id. 同时返回 A.表示申请成功.
        如果旧条码无效或者没有有效的产品信息.返回 1
        无对应产品的空白条码,返回 0
        如果程序执行出错.返回 -1
        注意,此步骤嵌入式需要考虑如何将临时申请的条码传给标签打印机
        :param old_id:  旧条码,用于确认产品信息
        :return:
        """
        db_client = orm_module.get_client()
        w = orm_module.get_write_concern()
        col = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client, write_concern=w)
        t = col.find_one(filter={"_id": old_id})
        if t is None:
            return 0
        else:
            product_id = t.get("product_id", None)
            if product_id is None:
                return 0
            else:
                print_id = ObjectId()  # 临时申请一个打印文件id
                f = {"print_id": {"$exists": False}, "product_id": product_id}
                u = {"$set": {"print_id": print_id}}
                re_type = orm_module.ReturnDocument.AFTER
                r = None
                try:
                    r = col.find_one_and_update(filter=f, update=u, return_document=re_type)
                except Exception as e:
                    logger.exception(e)
                    r = e
                    print(e)
                finally:
                    if isinstance(r, dict) and product_id in r:
                        return r['_id']
                    elif isinstance(r, Exception):
                        return -1
                    else:
                        return 0

    @classmethod
    def code_details(cls, code: str) -> str:
        """
        查询条码详细信息.这个方法是给tcp服务端接收嵌入式请求用的
        :param code:
        :return: json数据
        """
        f = {"_id": code}
        r = cls.find_info(filter_dict=f, can_json=True)
        return json.dumps(r)

    @classmethod
    def preview(cls) -> dict:
        """
        条码的统计信息预览
        :return:
        """
        col = cls.get_collection()
        pipeline = []
        resp = dict()
        g = {
            "$group":
                {
                    "_id":
                        {
                            "$switch":
                                {
                                    "branches": [
                                        {
                                            "case": {"$eq": [{"$type": "$print_id"}, "objectId"]},  # 打印过的
                                            "then": "printed"
                                        }
                                    ],
                                    "default": "deposit"
                                }
                        },
                    "count": {"$sum": 1},
                    "not_used_count":
                        {
                            "$sum":
                                {
                                    "$cond":
                                        {
                                            "if": {"$in": ["$status", [0, None]]},
                                            "then": 1,
                                            "else": 0
                                        }
                                }

                        },
                    "used_count":
                        {
                            "$sum":
                                {
                                    "$cond":
                                        {
                                            "if": {"$eq": ["$status", 1]},
                                            "then": 1,
                                            "else": 0
                                        }
                                }

                        },
                    "sync_count":
                        {
                            "$sum":
                                {
                                    "$cond":
                                        {
                                            "if": {
                                                "$and":
                                                    [
                                                        {"$eq": ["$status", 1]},
                                                        {"$eq": [{"$type": "$sync_id"}, "objectId"]}
                                                    ]
                                            },
                                            "then": 1,
                                            "else": 0
                                        }
                                }

                        },
                    "not_sync_count":
                        {
                            "$sum":
                                {
                                    "$cond":
                                        {
                                            "if": {
                                                "$and":
                                                    [
                                                        {"$eq": ["$status", 1]},
                                                        {"$ne": [{"$type": "$sync_id"}, "objectId"]}
                                                    ]
                                            },
                                            "then": 1,
                                            "else": 0
                                        }
                                }

                        },
                    "related_count":  # 已关联任务
                        {
                            "$sum":
                                {
                                    "$cond":
                                        {
                                            "if": {
                                                "$and":
                                                    [
                                                        {"$eq": ["$status", 1]},
                                                        {"$ne": [{"$type": "$task_id"}, "objectId"]},
                                                        {"$ne": [{"$type": "$sync_id"}, "objectId"]}
                                                    ]
                                            },
                                            "then": 1,
                                            "else": 0
                                        }
                                }

                        },
                    "output_count":
                        {
                            "$sum":
                                {
                                    "$cond":
                                        {
                                            "if": {
                                                "$and":
                                                    [
                                                        {"$eq": ["$status", 1]},
                                                        {"$ne": [{"$type": "$task_id"}, "objectId"]},
                                                        {"$eq": [{"$type": "$sync_id"}, "objectId"]},
                                                        {"$eq": [{"$type": "$output_id"}, "objectId"]}
                                                    ]
                                            },
                                            "then": 1,
                                            "else": 0
                                        }
                                }
                        },
                    "not_output_count":
                        {
                            "$sum":
                                {
                                    "$cond":
                                        {
                                            "if": {
                                                "$and":
                                                    [
                                                        {"$eq": ["$status", 1]},
                                                        {"$ne": [{"$type": "$task_id"}, "objectId"]},
                                                        {"$eq": [{"$type": "$sync_id"}, "objectId"]},
                                                        {"$ne": [{"$type": "$output_id"}, "objectId"]}
                                                    ]
                                            },
                                            "then": 1,
                                            "else": 0
                                        }
                                }
                        }
                }
        }

        pipeline.append(g)
        r = col.aggregate(pipeline=pipeline)
        r = [x for x in r]
        total = 0
        for x in r:
            if x['_id'] == "printed":
                """已打印条码"""
                temp = x['count']
                total += temp
                resp['printed'] = temp   # 已打印
                resp['not_used'] = x['not_used_count']  # 已打印未使用
                resp['used'] = x['used_count']  # 已打印已使用
                resp['sync'] = x['sync_count']  # 已使用已同步过
                resp['not_sync'] = x['not_sync_count']  # 已使用未同步过
                resp['related'] = x['related_count']  # 已同步未关联任务
                resp['output'] = x['output_count']  # 已同步过已关联任务已导出过
                resp['not_output'] = x['not_output_count']  # 已同步过已关联任务未导出过
            else:
                """未打印条码"""
                temp = x['count']
                total += temp
                resp['deposit'] = temp  # 未打印
        resp['total'] = total
        return resp

    @classmethod
    def find_info(cls, filter_dict: dict, can_json: bool = False) -> dict:
        """
        查找单条条码信息, 给管理端使用的.
        :param filter_dict:
        :param can_json:
        :return:
        """
        pipeline = []
        m = {"$match": filter_dict}
        pipeline.append(m)

        """查询打印信息"""
        l0 = {
            "$lookup":
                {
                    "from": "print_code",
                    "let": {"prid": "$print_id"},
                    "pipeline":
                        [
                            {
                                "$match": {"$expr": {"$eq": ['$_id', "$$prid"]}}
                            },
                            {"$project": {"_id": 0, "print_time": "$time"}}
                        ]
                    ,
                    "as": "print_item"
                }
        }
        r0 = {
            '$replaceRoot':  # 从根文档替换
                {'newRoot':  # 作为新文档
                    {
                        '$mergeObjects':
                            [
                                {'$arrayElemAt': ["$print_item", 0]},
                                '$$ROOT'  # 标识根文档
                            ]
                    }
                }
        }
        rm0 = {"$project": {"print_item": 0}}
        pipeline.append(l0)
        pipeline.append(r0)
        pipeline.append(rm0)

        """查询生产任务相关信息"""
        l1 = {
            "$lookup":
                {
                    "from": "produce_task",
                    "let": {"tid": "$task_id"},
                    "pipeline":
                        [
                            {
                                "$match": {"$expr": {"$eq": ['$_id', "$$tid"]}}
                            },
                            {"$project": {"_id": 0, "batch_sn": 1}}
                        ]
                    ,
                    "as": "task_item"
                }
        }
        r1 = {
            '$replaceRoot':  # 从根文档替换
                {'newRoot':  # 作为新文档
                    {
                        '$mergeObjects':
                            [
                                {'$arrayElemAt': ["$task_item", 0]},
                                '$$ROOT'  # 标识根文档
                            ]
                    }
                }
        }
        rm1 = {"$project": {"task_item": 0}}
        pipeline.append(l1)
        pipeline.append(r1)
        pipeline.append(rm1)

        """查询产品信息"""
        l2 = {
            "$lookup":
                {
                    "from": "product_info",
                    "let": {"pid": "$product_id"},
                    "pipeline":
                        [
                            {
                                "$match": {"$expr": {"$eq": ['$_id', "$$pid"]}}
                            },
                            {
                                "$addFields":
                                    {
                                        "product_info": {""
                                                "$concat":
                                            [
                                                "$product_name", " ",
                                                "$specification", " ",
                                                "$net_contents", " ",
                                                "$package_ratio"
                                            ]
                                        }
                                    }
                            },
                            {"$project": {"_id": 0, "product_info": 1}}
                        ]
                    ,
                    "as": "product_item"
                }
        }
        r2 = {
            '$replaceRoot':  # 从根文档替换
                {'newRoot':  # 作为新文档
                    {
                        '$mergeObjects':
                            [
                                {'$arrayElemAt': ["$product_item", 0]},
                                '$$ROOT'  # 标识根文档
                            ]
                    }
                }
        }
        rm2 = {"$project": {"product_item": 0}}
        pipeline.append(l2)
        pipeline.append(r2)
        pipeline.append(rm2)
        """查询回传任务相关信息"""
        l3 = {
            "$lookup":
                {
                    "from": "task_sync",
                    "let": {"sid": "$sync_id"},
                    "pipeline":
                        [
                            {
                                "$match": {"$expr": {"$eq": ['$_id', "$$sid"]}}
                            },
                            {"$project": {"_id": 0, "sync_time": "$time"}}
                        ]
                    ,
                    "as": "sync_item"
                }
        }
        r3 = {
            '$replaceRoot':  # 从根文档替换
                {'newRoot':  # 作为新文档
                    {
                        '$mergeObjects':
                            [
                                {'$arrayElemAt': ["$sync_item", 0]},
                                '$$ROOT'  # 标识根文档
                            ]
                    }
                }
        }
        rm3 = {"$project": {"sync_item": 0}}
        pipeline.append(l3)
        pipeline.append(r3)
        pipeline.append(rm3)

        """查询导出相关信息"""
        l4 = {
            "$lookup":
                {
                    "from": "output_code",
                    "let": {"oid": "$output_id"},
                    "pipeline":
                        [
                            {
                                "$match": {"$expr": {"$eq": ['$_id', "$$oid"]}}
                            },
                            {"$project": {"_id": 0, "output_time": "$time"}}
                        ]
                    ,
                    "as": "output_item"
                }
        }
        r4 = {
            '$replaceRoot':  # 从根文档替换
                {'newRoot':  # 作为新文档
                    {
                        '$mergeObjects':
                            [
                                {'$arrayElemAt': ["$output_item", 0]},
                                '$$ROOT'  # 标识根文档
                            ]
                    }
                }
        }
        rm4 = {"$project": {"output_item": 0}}
        pipeline.append(l4)
        pipeline.append(r4)
        pipeline.append(rm4)

        col = cls.get_collection()
        r = col.aggregate(pipeline=pipeline)

        r = [x for x in r]
        resp = dict() if len(r) == 0 else r[0]
        return orm_module.to_flat_dict(resp) if can_json else resp

    @classmethod
    def reset_info(cls, filter_dict: dict) -> dict:
        """
        重设条码的信息为刚打印状态.给管理端使用的.
        会进行如下操作:
        1. status = 0
        2. task_id 删除
        3. sync_id 删除
        4. output_id 删除
        4. level 删除
        :param filter_dict:  包含id的一个查找过滤器
        :return:
        """
        f = filter_dict
        mes = {"message": "success"}
        d = [
            ("$set", {"status": 0}),
            ("$unset", {"sync_id": "", "task_id": "", "level": "", "output_id": ""})
        ]
        u = orm_module.SON(data=d)
        col = cls.get_collection()
        after = orm_module.ReturnDocument.AFTER
        r = col.find_one_and_update(filter=f, update=u, upsert=False, return_document=after)
        if isinstance(r, dict):
            data = cls.find_info(filter_dict={"_id": filter_dict['_id']}, can_json=True)
            mes['data'] = data
        else:
            mes['message'] = "重置失败"
        return mes

    @classmethod
    def replace_info(cls, old_id: str, new_id: str) -> dict:
        """
        重设条码的信息为刚打印状态.给管理端使用的.
        会替换除 file_id, print_id, _id,之外的所有字段.
        :param old_id:  旧条码id
        :param new_id:  新条码id
        :return:
        """
        f1 = {"_id": old_id}
        f2 = {"_id": new_id}
        mes = {"message": "success"}
        keys = ['sync_id', 'task_id', 'level', 'output_id', 'product_id']
        db_client = orm_module.get_client()
        col = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client)
        with db_client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=orm_module.get_write_concern()):
                r1 = col.find_one(filter=f1, session=ses)
                r2 = col.find_one(filter=f2, session=ses)
                if r1 is None or r2 is None:
                    mes['message'] = "条码信息不全"
                    ses.abort_transaction()
                else:
                    s1 = {k: r2[k] for k in keys if r2.get(k) is not None}
                    us1 = {k: "" for k in keys if k not in s1}
                    s2 = {k: r1[k] for k in keys if r1.get(k) is not None}
                    us2 = {k: "" for k in keys if k not in s2}
                    if len(us1) == 0:
                        u1 = orm_module.SON(data=
                        [
                            ("$set", s1)
                        ])
                    else:
                        u1 = orm_module.SON(data=
                        [
                            ("$unset", us1),
                            ("$set", s1)
                        ])
                    if len(us2) == 0:
                        u2 = orm_module.SON(data=
                        [
                            ("$set", s2)
                        ])
                    else:
                        u2 = orm_module.SON(data=
                        [
                            ("$unset", us2),
                            ("$set", s2)
                        ])
                    after = orm_module.ReturnDocument.AFTER
                    res1 = col.find_one_and_update(filter=f1, update=u1, return_document=after, session=ses)
                    res2 = col.find_one_and_update(filter=f2, update=u2, return_document=after, session=ses)
                    if isinstance(res1, dict) and isinstance(res2, dict):
                        pass
                    else:
                        mes['message'] = '更新失败'
                        ses.abort_transaction()
        if mes['message'] == "success":
            mes['data'] = [
                cls.find_info(filter_dict={"_id": old_id}, can_json=True),
                cls.find_info(filter_dict={"_id": new_id}, can_json=True)
            ]
        return mes


if __name__ == "__main__":
    # CodeInfo.query_code("23132104307180149268677481490882207")
    # CodeInfo.replace_code("23132100917116379735071455644638667", "23132102805841430218730720125819577")
    CodeInfo.find_info({"_id": "23132102805841430218730720125819577"})
    pass
