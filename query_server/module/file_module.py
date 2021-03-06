# -*- coding: utf-8 -*-
import os
import sys
__root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __root_path not in sys.path:
    sys.path.append(__root_path)
import orm_module
import gzip
from flask import request
import datetime
from log_module import get_logger
import re
import json
import numpy as np
import chardet
import zipfile
import warnings
from io import TextIOWrapper


"""
文件的处理模块,包括:
1. 导入文件时对文件的解析
2. 合成导出文件
"""

logger = get_logger()
root_dir = __root_path
cache = orm_module.RedisCache()
ObjectId = orm_module.ObjectId
IMPORT_DIR = os.path.join(__root_path, "import_data")  # 上传文件的默认目录
EXPORT_DIR = os.path.join(__root_path, "export_data")  # 导出文件的默认目录
TASK_SYNC = os.path.join(__root_path, "task_sync")  # 回传文件的默认目录
OUTPUT_CODE = os.path.join(__root_path, "output_code")  # 导出最终条码的默认目录
TEMP = os.path.join(__root_path, "temp")  # 临时目录
if not os.path.exists(IMPORT_DIR):
    os.makedirs(IMPORT_DIR)
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)
if not os.path.exists(TASK_SYNC):
    os.makedirs(TASK_SYNC)
if not os.path.exists(OUTPUT_CODE):
    os.makedirs(OUTPUT_CODE)
if not os.path.exists(TEMP):
    os.makedirs(TEMP)


class PrintCode(orm_module.BaseDoc):
    """导出打印条码记录"""
    _table_name = "print_code"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['file_name'] = str   # 文件名,包含
    type_dict['file_size'] = int   # 文件大小
    type_dict['count'] = int   # 导出数量
    type_dict['product_id'] = ObjectId
    type_dict['desc'] = str  # 备注
    type_dict['time'] = datetime.datetime  # 导出打印条码的时间

    orm_module.collection_exists(table_name=_table_name, auto_create=True)

    @classmethod
    def pickle(cls, file_name: str, data: list) -> int:
        """
        把数据保存到文件.
        :param file_name: file_name 其实就是记录id
        :param data:
        :return: file_size
        """
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)
        else:
            pass
        file_path = os.path.join(EXPORT_DIR, "{}".format(file_name))
        data = ['{}\r\n'.format(x) for x in data]
        with open(file=file_path, mode="w", encoding="utf-8") as f:
            f.writelines(data)
        size = os.path.getsize(file_path)
        return size

    @classmethod
    def export(cls, number: int, product_id: ObjectId, file_name: str = None, desc: str = '') -> dict:
        """
        导出要打印的条码记录
        :param number: 导出数量
        :param product_id: 产品id
        :param file_name: 文件名
        :param desc: 备注
        :return:
        """
        mes = {"message": "success"}
        db_client = orm_module.get_client()
        write_concern = orm_module.get_write_concern()
        table = "code_info"
        f = {"print_id": {"$exists": False}, "product_id": product_id, "status": 0}
        col = orm_module.get_conn(table_name=table, db_client=db_client)
        me = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client)
        pipeline = list()
        pipeline.append({'$match': f})
        pipeline.append({"$project": {"_id": 1}})
        with db_client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=write_concern):
                r = col.aggregate(pipeline=pipeline, allowDiskUse=True, session=ses)
                codes = [x["_id"] for x in r]
                count = len(codes)
                if count < number:
                    mes['message'] = "空白条码存量不足: 需求: {},库存: {}".format(number, count)
                else:
                    """保存文件"""
                    codes = codes[0: number]
                    _id = ObjectId()
                    save_name = "{}.txt".format(str(_id))
                    file_size = cls.pickle(file_name=save_name, data=codes)
                    if not isinstance(file_size, int):
                        mes['message'] = "保存导出文件失败"
                        ses.abort_transaction()
                    else:
                        """创建一个实例"""
                        now = datetime.datetime.now()
                        file_name = file_name if file_name is not None else "{}.txt".format(now.strftime("%Y-%m-%d %H:%M:%S"))
                        doc = {
                            "_id": _id,
                            "product_id": product_id,
                            "desc": desc,
                            "file_name": file_name,
                            "file_size": file_size,
                            "count": number,
                            "time": now
                        }
                        r2 = me.insert_one(document=doc, session=ses)
                        if isinstance(r2, orm_module.InsertOneResult):
                            inserted_id = r2.inserted_id
                            """批量更新"""
                            f = {"_id": {"$in": codes}}
                            u = {"$set": {"print_id": inserted_id}}
                            r3 = col.update_many(filter=f, update=u, session=ses)
                            if isinstance(r3, orm_module.UpdateResult):
                                matched_count = r3.matched_count
                                modified_count = r3.modified_count
                                if len(codes) == matched_count == modified_count:
                                    pass  # 成功
                                else:
                                    ms = "更新了{}条条码状态, 其中{}条更新成功".format(matched_count, modified_count)
                                    mes['message'] = ms
                                    ses.abort_transaction()
                            else:
                                mes['message'] = "标记导出文件出错,函数未正确执行"
                                ses.abort_transaction()
                        else:
                            mes['message'] = "批量更新条码导出记录出错"
                            ses.abort_transaction()
        return mes

    @classmethod
    def paging_info(cls, filter_dict: dict, sort_cond: dict, page_index: int = 1, page_size: int = 10,
                    can_json: bool = False) -> dict:
        """
        分页查看角色信息
        :param filter_dict: 过滤器,由用户的权限生成
        :param sort_cond: 过滤器,由用户的权限生成
        :param page_index: 页码(当前页码)
        :param page_size: 每页多少条记录
        :param can_json: 转换成可以json的字典?
        :return:
        """
        join_cond = {
            "table_name": "product_info",
            "local_field": "product_id",
            "flat": True
        }
        kw = {
            "filter_dict": filter_dict,
            "join_cond": join_cond,
            "sort_cond": sort_cond,
            "page_index": page_index,
            "page_size": page_size,
            "can_json": can_json
        }
        res = cls.query(**kw)
        return res

    @classmethod
    def all_file_name(cls) -> list:
        """
        获取import_data目录下,所有文件的名字(不包括扩展名).
        用于和数据库记录比对看哪个文件在磁盘上存在?
        :return:
        """
        names = os.listdir(IMPORT_DIR)
        resp = []
        for name in names:
            if os.path.isfile(os.path.join(IMPORT_DIR, name)):
                resp.append(name[0: 24])
            else:
                pass
        return resp

    @classmethod
    def delete_file_and_record(cls, ids: list, include_record: bool = False) -> dict:
        """
        批量删除文件和导入记录.
        :param ids:
        :param include_record: 是否连记录一起删除?
        :return:
        """
        mes = {"message": "success"}
        ids = [x if isinstance(x, ObjectId) else ObjectId(x) for x in ids]
        if include_record:
            cls.delete_many(filter_dict={"_id": {"$in": ids}})
        else:
            pass
        ids = [str(x) for x in ids]
        names = os.listdir(EXPORT_DIR)
        for name in names:
            prefix = name.split(".")[0]
            if prefix in ids:
                os.remove(os.path.join(EXPORT_DIR, name))
            else:
                pass
        return mes

    @classmethod
    def cancel_data(cls, f_ids: list) -> dict:
        """
        撤销导入的文件
        :param f_ids: 文件id的list
        :return:
        """
        mes = {"message": "success"}
        ids2 = [x if isinstance(x, ObjectId) else ObjectId(x) for x in f_ids]
        f = {"print_id": {"$in": ids2}}
        w = orm_module.get_write_concern()
        col = orm_module.get_conn(table_name="code_info", write_concern=w)
        u = {"$unset": {"print_id": ""}}
        col.update_many(filter=f, update=u)
        mes = cls.delete_file_and_record(ids=ids2, include_record=True)
        return mes


class OutputCode(orm_module.BaseDoc):
    """
    导出最终条码记录
    """
    _table_name = "output_code"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['file_name'] = str   # 文件名,包含
    type_dict['file_size'] = int   # 文件大小
    type_dict['count'] = int   # 导出数量
    type_dict['product_id'] = ObjectId
    type_dict['desc'] = str  # 备注
    type_dict['time'] = datetime.datetime  # 导出打印条码的时间

    orm_module.collection_exists(table_name=_table_name, auto_create=True)

    @classmethod
    def pickle(cls, file_name: str, data: list) -> int:
        """
        把数据保存到文件.
        :param file_name: file_name 其实就是记录id
        :param data:
        :return: file_size
        """
        if not os.path.exists(EXPORT_DIR):
            os.makedirs(EXPORT_DIR)
        else:
            pass
        file_path = os.path.join(OUTPUT_CODE, "{}".format(file_name))
        data = ['{}\r\n'.format(x) for x in data]
        with open(file=file_path, mode="w", encoding="utf-8") as f:
            f.writelines(data)
        size = os.path.getsize(file_path)
        return size

    @classmethod
    def export(cls, number: int, product_id: ObjectId, file_name: str = None, desc: str = '') -> dict:
        """
        导出已生产的条码记录
        :param number: 导出数量
        :param product_id: 产品id
        :param file_name: 文件名
        :param desc: 备注
        :return:
        """
        mes = {"message": "success"}
        db_client = orm_module.get_client()
        write_concern = orm_module.get_write_concern()
        table = "code_info"
        f = {"sync_id": {"$type": "objectId"}, "product_id": product_id}
        col = orm_module.get_conn(table_name=table, db_client=db_client)
        me = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client)
        pipeline = list()
        pipeline.append({'$match': f})
        pipeline.append({"$project": {"_id": 1}})
        with db_client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=write_concern):
                r = col.aggregate(pipeline=pipeline, allowDiskUse=True, session=ses)
                codes = [x["_id"] for x in r]
                count = len(codes)
                if count < number:
                    mes['message'] = "空白条码存量不足: 需求: {},库存: {}".format(number, count)
                else:
                    """保存文件"""
                    codes = codes[0: number]
                    _id = ObjectId()
                    save_name = "{}.txt".format(str(_id))
                    file_size = cls.pickle(file_name=save_name, data=codes)
                    if not isinstance(file_size, int):
                        mes['message'] = "保存导出文件失败"
                        ses.abort_transaction()
                    else:
                        """创建一个实例"""
                        now = datetime.datetime.now()
                        file_name = file_name if file_name is not None else "{}.txt".format(now.strftime("%Y-%m-%d %H:%M:%S"))
                        doc = {
                            "_id": _id,
                            "product_id": product_id,
                            "desc": desc,
                            "file_name": file_name,
                            "file_size": file_size,
                            "count": number,
                            "time": now
                        }
                        r2 = me.insert_one(document=doc, session=ses)
                        if isinstance(r2, orm_module.InsertOneResult):
                            inserted_id = r2.inserted_id
                            """批量更新"""
                            f = {"_id": {"$in": codes}}
                            u = {"$set": {"output_id": inserted_id}}
                            r3 = col.update_many(filter=f, update=u, session=ses)
                            if isinstance(r3, orm_module.UpdateResult):
                                matched_count = r3.matched_count
                                modified_count = r3.modified_count
                                if len(codes) == matched_count == modified_count:
                                    pass # 成功
                                else:
                                    ms = "更新了{}条条码状态, 其中{}条更新成功".format(matched_count, modified_count)
                                    mes['message'] = ms
                                    ses.abort_transaction()
                            else:
                                mes['message'] = "标记已生产的导出文件出错,函数未正确执行"
                                ses.abort_transaction()
                        else:
                            mes['message'] = "批量更新已生产条码导出记录出错"
                            ses.abort_transaction()
        return mes

    @classmethod
    def paging_info(cls, filter_dict: dict, sort_cond: dict, page_index: int = 1, page_size: int = 10,
                    can_json: bool = False) -> dict:
        """
        分页查看角色信息
        :param filter_dict: 过滤器,由用户的权限生成
        :param sort_cond: 过滤器,由用户的权限生成
        :param page_index: 页码(当前页码)
        :param page_size: 每页多少条记录
        :param can_json: 转换成可以json的字典?
        :return:
        """
        join_cond = {
            "table_name": "product_info",
            "local_field": "product_id",
            "flat": True
        }
        kw = {
            "filter_dict": filter_dict,
            "join_cond": join_cond,
            "sort_cond": sort_cond,
            "page_index": page_index,
            "page_size": page_size,
            "can_json": can_json
        }
        res = cls.query(**kw)
        return res

    @classmethod
    def all_file_name(cls) -> list:
        """
        获取import_data目录下,所有文件的名字(不包括扩展名).
        用于和数据库记录比对看哪个文件在磁盘上存在?
        :return:
        """
        names = os.listdir(IMPORT_DIR)
        resp = []
        for name in names:
            if os.path.isfile(os.path.join(IMPORT_DIR, name)):
                resp.append(name[0: 24])
            else:
                pass
        return resp

    @classmethod
    def delete_file_and_record(cls, ids: list, include_record: bool = False) -> dict:
        """
        批量删除文件和导入记录.
        :param ids:
        :param include_record: 是否连记录一起删除?
        :return:
        """
        mes = {"message": "success"}
        ids = [x if isinstance(x, ObjectId) else ObjectId(x) for x in ids]
        if include_record:
            cls.delete_many(filter_dict={"_id": {"$in": ids}})
        else:
            pass
        ids = [str(x) for x in ids]
        names = os.listdir(OUTPUT_CODE)
        for name in names:
            prefix = name.split(".")[0]
            if prefix in ids:
                os.remove(os.path.join(OUTPUT_CODE, name))
            else:
                pass
        return mes

    @classmethod
    def cancel_data(cls, f_ids: list) -> dict:
        """
        撤销导入的文件
        :param f_ids: 文件id的list
        :return:
        """
        mes = {"message": "success"}
        ids2 = [x if isinstance(x, ObjectId) else ObjectId(x) for x in f_ids]
        f = {"output_id": {"$in": ids2}}
        w = orm_module.get_write_concern()
        col = orm_module.get_conn(table_name="code_info", write_concern=w)
        u = {"$unset": {"output_id": ""}}
        col.update_many(filter=f, update=u)
        mes = cls.delete_file_and_record(ids=ids2, include_record=True)
        return mes


class UploadFile(orm_module.BaseDoc):
    """上传空白条码文件的记录/导入记录"""
    _table_name = "upload_file_history"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['product_id'] = ObjectId  # 对应的产品id
    type_dict['file_name'] = str
    type_dict['storage_name'] = str
    type_dict['file_size'] = int  # 单位字节
    type_dict['file_type'] = str
    type_dict['status'] = int     # 状态,1是成功.0是失败
    type_dict['valid_count'] = int      # 有效条码计数
    type_dict['upload_time'] = datetime.datetime
    type_dict['import_time'] = datetime.datetime

    @classmethod
    def upload(cls, req: request, dir_path: str = None) -> dict:
        """
        上传条码文件
        :param req:
        :param dir_path: 保存上传文件的目录
        :return:
        """
        dir_path = IMPORT_DIR if dir_path is None else dir_path
        if not os.path.exists(dir_path):
            os.makedirs(path=dir_path)
        mes = {"message": "success"}
        file = req.files.get("file")
        if file is None:
            mes['message'] = "没有找到上传的文件"
        else:
            product_id = req.headers.get("product_id", None)
            print("product_id is {}".format(product_id))
            if isinstance(product_id, str) and len(product_id) == 24:
                product_id = ObjectId(product_id)
                file_name = file.filename
                file_type = file.content_type
                _id = ObjectId()
                storage_name = "{}.{}".format(str(_id), file_name.split(".")[-1])
                f_p = os.path.join(dir_path, storage_name)
                with open(f_p, "wb") as f:
                    file.save(dst=f)  # 保存文件
                """读取文件信息"""
                file_info = cls.read_file(f_p)
                values = file_info.pop('values', None)
                file_size = os.path.getsize(f_p)
                now = datetime.datetime.now()

                if values is None or len(values) == 0:
                    mes['message'] = "没有在文件里发现条码信息"
                else:
                    w = orm_module.get_write_concern()
                    db_client = orm_module.get_client()
                    col1 = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client, write_concern=w)
                    col2 = orm_module.get_conn(table_name="code_info", db_client=db_client, write_concern=w)
                    """数据可能会很大,不能使用事务,开始批量插入"""
                    values = [{"_id": x, "status": 0, "file_id": _id, "product_id": product_id} for x in values]
                    begin = datetime.datetime.now()
                    r = None  # 批量插入状态位
                    count = 1
                    for docs in cls.split_list(array=values):
                        try:
                            r = col2.insert_many(documents=docs, ordered=False, bypass_document_validation=True)
                            print("第{}批成功".format(count))
                            count += 1
                        except orm_module.BulkWriteError as e1:
                            mes['message'] = "有重复的数据"
                            r = None
                        except Exception as e:
                            mes['message'] = "{}".format(e)
                            r = None
                        finally:
                            if isinstance(r, orm_module.InsertManyResult):
                                pass
                            else:
                                """出错了"""
                                print("第{}批出错了".format(count))
                                break
                    end = datetime.datetime.now()
                    print((end - begin).total_seconds())
                    doc = {
                        "_id": _id,
                        "file_name": file_name,
                        "product_id": product_id,
                        "storage_name": storage_name,
                        "file_size": file_size,
                        "file_type": file_type,
                        "valid_count": file_info['valid_count'],
                        "status": 1,
                        "upload_time": now,
                        "import_time": now
                    }
                    if r is None:
                        """出错了,回退数据"""
                        col2.delete_many(filter={"file_id": _id})
                        doc['status'] = 0
                    else:
                        """成功"""
                        r = col1.insert_one(document=doc)
                        if isinstance(r, orm_module.InsertOneResult):
                            pass  # 成功
                        else:
                            mes['message'] = "保存导入记录失败"

            else:
                mes['message'] = "没有发现产品信息"
        return mes

    @classmethod
    def split_list(cls, array: list, size: int = 10000) -> list:
        """
        把大数组拆分成小数组
        :param array:
        :param size:
        :return:
        """
        l = int(len(array) / size)
        step = [size * i for i in range(1, l + 1)]
        r = np.split(array, step)
        r = [x.tolist() for x in r if len(x) > 0]
        return r

    @classmethod
    def read_file(cls, file_path: str) -> dict:
        """
        根据文件路径读取文件
        :param file_path:
        :return:
        """
        res = None
        f = open(file=file_path, mode="rb")
        data = f.readline()
        info = chardet.detect(data)
        print("info={}".format(info))
        encoding = info['encoding']      # 编码
        confidence = info['confidence']  # 置信度
        language = info.get('language')      # 语言不一定能获取的到
        if os.path.exists(file_path):
            with open(file_path, mode="r", encoding=encoding) as lines:
                res = cls.parse_lines(lines)
        else:
            pass
        """条码统计的信息"""

        res = {
                "valid_count": res['valid_count'],
                "values": res.pop('values', None)
            }
        f.close()
        return res

    @classmethod
    def discovery_feature(cls, line: str) -> str:
        """
        从一行读取的数据提取一个大于18位纯数字
        :param line:
        :return:
        """
        r = re.search('\d{18,}', line)
        if r:
            return r.group()

    @classmethod
    def parse_lines(cls, lines: (TextIOWrapper, list)) -> dict:
        """
        解析读取的一行数据
        :param lines:
        :return:
        """
        values = [cls.discovery_feature(line) for line in lines if cls.discovery_feature(line)]
        valid_count = len(values)      # 有效条码统计
        res = {
            "valid_count": valid_count,
            "values": values
        }
        return res

    @classmethod
    def delete_file_and_record(cls, ids: list, include_record: bool = False) -> dict:
        """
        批量删除文件和导入记录.
        :param ids:
        :param include_record: 是否连记录一起删除?
        :return:
        """
        mes = {"message": "success"}
        ids = [x if isinstance(x, ObjectId) else ObjectId(x) for x in ids]
        if include_record:
            cls.delete_many(filter_dict={"_id": {"$in": ids}})
        else:
            pass
        ids = [str(x) for x in ids]
        names = os.listdir(IMPORT_DIR)
        for name in names:
            prefix = name.split(".")[0]
            if prefix in ids:
                os.remove(os.path.join(IMPORT_DIR, name))
            else:
                pass
        return mes

    @classmethod
    def cancel_data(cls, f_ids: list) -> dict:
        """
        撤销导入的文件
        :param f_ids: 文件id的list
        :return:
        """
        mes = {"message": "success"}
        ids2 = [x if isinstance(x, ObjectId) else ObjectId(x) for x in f_ids]
        f = {"file_id": {"$in": ids2}}
        w = orm_module.get_write_concern()
        col = orm_module.get_conn(table_name="code_info", write_concern=w)
        col.delete_many(filter=f)
        mes = cls.delete_file_and_record(ids=ids2, include_record=True)
        return mes

    @classmethod
    def paging_info(cls, filter_dict: dict, sort_cond: dict, page_index: int = 1, page_size: int = 10, can_json: bool = False) -> dict:
        """
        分页查看角色信息
        :param filter_dict: 过滤器,由用户的权限生成
        :param sort_cond: 过滤器,由用户的权限生成
        :param page_index: 页码(当前页码)
        :param page_size: 每页多少条记录
        :param can_json: 转换成可以json的字典?
        :return:
        """
        join_cond = {
            "table_name": "product_info",
            "local_field": "product_id",
            "flat": True
        }
        kw = {
            "filter_dict": filter_dict,
            "join_cond": join_cond,
            "sort_cond": sort_cond,
            "page_index": page_index,
            "page_size": page_size,
            "can_json": can_json
        }
        res = cls.query(**kw)
        return res

    @classmethod
    def all_file_name(cls) -> list:
        """
        获取import_data目录下,所有文件的名字(不包括扩展名).
        用于和数据库记录比对看哪个文件在磁盘上存在?
        :return:
        """
        names = os.listdir(IMPORT_DIR)
        resp = []
        for name in names:
            if os.path.isfile(os.path.join(IMPORT_DIR, name)):
                resp.append(name[0: 24])
            else:
                pass
        return resp


class TaskSync(orm_module.BaseDoc):
    """
    嵌入式设备同步工作任务信息
    在每天的工作结束后,嵌入式设备同步工作任务信息.同步的步骤如下:
    1. 嵌入式设备将当日使用的条码信息组装成json格式的数据,写入文件.
    2. 压缩成zip文件(非必须, 但建议使用.但能大大降低文件尺寸)
    3. 嵌入式将文件使用http协议的post方法发送给服务端.
    4. 服务端接受到文件后先缓存文件.
    5. 服务端解析文件.如果解析出错,提醒,否则提示成功.
    6. 会同时修改条码信息.记录相关信息
    """
    _table_name = "task_sync"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['file_name'] = str           # 上传的时候使用的文件名
    type_dict['file_suffix'] = str           # 上传的时候使用的文件名后缀,用于和_id拼接文件名
    type_dict['file_type'] = str           # 上传的时候使用的文件的类型
    type_dict['task_id'] = ObjectId        # 关连的任务id
    type_dict['desc'] = str                # 解析失败会在这里备注,否则会分类显示条码数量
    type_dict['count'] = int               # 条码数量
    type_dict['status'] = int               # code_info数据同步是否完成?. 完成1, 0未完脸任务, -1 已清除回传的信息
    type_dict['product_id'] = ObjectId     # 关连的产品id
    type_dict['embedded_ip'] = str         # 关连的主控板ip地址
    type_dict['time'] = datetime.datetime  # 同步日期

    @classmethod
    def upload(cls, req: request, dir_path: str = None) -> dict:
        """
        接收从嵌入式回传的条码文件
        :param req:
        :param dir_path: 保存上传文件的目录
        :return:
        """
        dir_path = TASK_SYNC if dir_path is None else dir_path
        if not os.path.exists(dir_path):
            os.makedirs(path=dir_path)
        mes = {"message": "success"}
        file = req.files.get("file")
        if file is None:
            mes['message'] = "没有找到回传的文件"
        else:
            file_name = file.filename
            file_type = file.content_type
            _id = ObjectId()
            file_suffix = file_name.split(".")[-1]
            storage_name = "{}.{}".format(str(_id), file_suffix)
            f_p = os.path.join(dir_path, storage_name)
            with open(f_p, "wb") as f:
                file.save(dst=f)  # 保存文件
            """装配doc"""
            now = datetime.datetime.now()
            doc = {
                "_id": _id,
                "file_name": file_name,
                "file_suffix": file_suffix,
                "storage_name": storage_name,
                "file_type": file_type,
                "embedded_ip":  req.remote_addr,
                "time": now
            }
            """读取文件信息"""
            desc = ""
            file_info = dict()
            try:
                file_info = cls.read_file(f_p)
            except FileNotFoundError as e:
                print(e)
                desc = "文件没有找到"
            except Exception as e:
                print(e)
                desc = "读取文件时发生错误"
            finally:
                if desc != "":
                    """读取文件有问题"""
                    doc['count'] = 0
                    doc['desc'] = desc
                    mes['message'] = "error"
                    cls.insert_one(doc=doc)
                else:
                    """读取文件成功"""
                    file_size = os.path.getsize(f_p)
                    doc['file_size'] = file_size
                    status = file_info['message']
                    if status != "success":
                        doc['desc'] = status
                        mes['message'] = "没有在文件里发现条码信息"
                    else:
                        count = file_info['count']
                        doc['count'] = count
                        data = file_info.pop('data', None)
                        w = orm_module.get_write_concern()
                        db_client = orm_module.get_client()
                        col1 = orm_module.get_conn(table_name=cls.get_table_name(), db_client=db_client, write_concern=w)
                        col2 = orm_module.get_conn(table_name="code_info", db_client=db_client, write_concern=w)
                        """数据可能会很大,不能使用事务,开始批量更新"""
                        begin = datetime.datetime.now()
                        r = None  # 批量插入状态位
                        for k, v in data.items():
                            if k != 1:
                                """不是一级码,数量有限"""
                                f = {"_id": {"$in": v}}
                                u = {"$set": {"status": 1, "level": k, "sync_id": _id}}
                                r = col2.update_many(filter=f, update=u)
                                if r is None:
                                    """出错了"""
                                    break
                                else:
                                    """正常"""
                                    pass
                            else:
                                count = 1
                                for ids in cls.split_list(array=v):
                                    try:
                                        f = {"_id": {"$in": ids}}
                                        u = {"$set": {"status": 1, "level": k, "sync_id": _id}}
                                        r = col2.update_many(filter=f, update=u)
                                        print("第{}批成功.match: {}".format(count, r.matched_count))
                                        count += 1
                                    except Exception as e:
                                        mes['message'] = "{}".format(e)
                                        r = None
                                    finally:
                                        if isinstance(r, orm_module.UpdateResult):
                                            pass
                                        else:
                                            """出错了"""
                                            print("第{}批出错了".format(count))
                                            break
                        end = datetime.datetime.now()
                        print((end - begin).total_seconds())
                        if r is None:
                            """出错了,回退数据"""
                            for k, v in data.items():
                                if k != 1:
                                    """不是一级码,数量有限"""
                                    f = {"_id": {"$in": v}}
                                    u = {"$set": {"status": 0, "level": None}}
                                    r = col2.update_many(filter=f, update=u)
                                else:
                                    count = 1
                                    for ids in cls.split_list(array=v):
                                        try:
                                            f = {"_id": {"$in": ids}}
                                            u = {"$set": {"status": 0, "level": None}}
                                            r = col2.update_many(filter=f, update=u,
                                                                 bypass_document_validation=True)
                                            print("第{}批成功".format(count))
                                            count += 1
                                        except Exception as e:
                                            mes['message'] = "{}".format(e)
                                            logger.exception(e)
                                            r = None
                                        finally:
                                            if isinstance(r, orm_module.InsertManyResult):
                                                pass
                                            else:
                                                """出错了"""
                                                print("第{}批出错了".format(count))
                            doc['status'] = 0
                        else:
                            doc['status'] = 1  # 成功
                        r = col1.insert_one(document=doc)
                        if isinstance(r, orm_module.InsertOneResult):
                            pass  # 成功
                        else:
                            mes['message'] = "保存回传数据失败"

        return mes

    @classmethod
    def relate_task(cls, sync_id: ObjectId, task_id: ObjectId) -> dict:
        """
        关联任务
        :param sync_id:
        :param task_id:
        :return:
        """
        mes = {"message": "success"}
        db_client = orm_module.get_client()
        col1 = cls.get_collection()
        col2 = orm_module.get_conn(table_name="code_info")
        w = orm_module.get_write_concern()
        with db_client.start_session(causal_consistency=True) as ses:
            with ses.start_transaction(write_concern=w):
                f = {"sync_id": sync_id}
                u = {"$set": {"task_id": task_id}}
                r = col2.update_many(filter=f, update=u, upsert=False, session=ses)
                if isinstance(r, orm_module.UpdateResult) and r.matched_count > 0:
                    """匹配到记录了"""
                    f2 = {"_id": sync_id}
                    u2 = {"$set": {"task_id": task_id}}
                    after = orm_module.ReturnDocument.AFTER
                    r2 = col1.find_one_and_update(filter=f2, update=u2, upsert=False, return_document=after, session=ses)
                    if isinstance(r2, dict) and task_id == r2['task_id']:
                        """修改成功"""
                        pass
                    else:
                        mes['message'] = '修改同步记录失败'
                else:
                    ses.abort_transaction()
                    mes['message'] = "没有找到对应的条码记录"
        return mes

    @classmethod
    def split_list(cls, array: list, size: int = 10000) -> list:
        """
        把大数组拆分成小数组
        :param array:
        :param size:
        :return:
        """
        l = int(len(array) / size)
        step = [size * i for i in range(1, l + 1)]
        r = np.split(array, step)
        r = [x.tolist() for x in r if len(x) > 0]
        return r

    @classmethod
    def parse_json(cls, content) -> list:
        """
        解析json文件的内容
        :param content:
        :return:
        """
        data = json.loads(content)
        return data

    @staticmethod
    def add_group(group: dict, level: int, sn: str) -> dict:
        """
        cls.group_code的辅助函数,用于把条码信息分类然后返回
        :param group:
        :param level:
        :param sn:
        :return:
        """
        d = list() if group.get(level) is None else group[level]
        d.append(sn)
        group[level] = d

    @classmethod
    def group_code(cls, codes: list, code_package: dict = None) -> dict:
        """
        把回传的字典类型的数组按照条码的级别归类.以方便快速批量修改
        :param codes:
        :param code_package: 递归专用,无需传递此参数
        :return:
        """
        code_package = dict() if code_package is None else code_package
        for x in codes:
            if isinstance(x, list):
                cls.group_code(codes=x, code_package=code_package)
            elif isinstance(x, dict):
                level = int(x.get("level").strip()) if isinstance(x.get("level"), str) else x.get("level")
                code = x.get("code")
                cls.add_group(group=code_package, level=level, sn=code)
                children = x.get("children")
                cls.group_code(codes=children, code_package=code_package)
            else:
                cls.add_group(group=code_package, level=1, sn=x)
        return code_package

    @classmethod
    def read_file(cls, file_path: str) -> dict:
        """
        根据文件路径读取回传文件,注意.这个文件可能是压缩文件.也可能只是普通的
        而且是json格式的文件.
        :param file_path:
        :return:
        """
        res = None
        mes = {"message": "success"}
        if file_path.lower().endswith(".json") or file_path.lower().endswith(".zip"):
            data = list()
            if file_path.lower().endswith(".json"):
                """读取json文件"""
                file = open(file=file_path, mode="r", encoding="utf-8")
                data = cls.parse_json(file.read())
                file.close()
            else:
                """读取压缩文件"""
                try:
                    file = zipfile.ZipFile(file=file_path, mode="r", compression=zipfile.ZIP_DEFLATED)
                    name_list = file.namelist()
                    if len(name_list) == 0:
                        mes['message'] = "压缩文件为空"
                    else:
                        for name in name_list:
                            content = file.read(name=name)
                            if content == '':
                                print("{}是空文件".format(name))
                            else:
                                temp = cls.parse_json(content=content)
                                data.extend(temp)
                    file.close()
                except zipfile.BadZipFile as e:
                    ms = str(e)
                    logger.exception(msg=ms)
                    warnings.warn(message=ms)
                    file = gzip.open(filename=file_path)
                    content = None
                    try:
                        content = file.read()
                    except OSError as e:
                        ms = str(e)
                        logger.exception(msg=ms)
                        warnings.warn(message=ms)
                        mes['message'] = "作为gzip类型读取失败"
                    except Exception as e:
                        ms = str(e)
                        logger.exception(msg=ms)
                        warnings.warn(message=ms)
                        mes['message'] = "处理gzip文件时遇到错误: {}".format(ms)
                    finally:
                        file.close()
                        if content is None:
                            """处理出错了"""
                            pass
                        elif content == '':
                            print("{}是空文件".format(file_path))
                        else:
                            temp = cls.parse_json(content=content)
                            data.extend(temp)
                except Exception as e:
                    ms = str(e)
                    logger.exception(msg=ms)
                    warnings.warn(message=ms)
                    mes['message'] = "读取zip文件时发生未知错误: {}".format(ms)
                finally:
                    pass
            result = cls.group_code(codes=data)
            desc = ""
            count = 0
            for k, v in result.items():
                temp = len(v)
                desc += "{}级码: {}个;".format(k, temp)
                count += temp
            desc += "共计 {}条".format(count)
            mes['desc'] = desc
            mes['count'] = count
            mes["data"] = result
        else:
            mes['message'] = "格式错误.只能是json或者zip格式的文件"
        return mes

    @classmethod
    def delete_file_and_record(cls, ids: list, include_record: bool = False) -> dict:
        """
        批量删除文件和导入记录.
        :param ids:
        :param include_record: 是否连记录一起删除?
        :return:
        """
        mes = {"message": "success"}
        ids = [x if isinstance(x, ObjectId) else ObjectId(x) for x in ids]
        if include_record:
            cls.delete_many(filter_dict={"_id": {"$in": ids}})
        else:
            pass
        ids = [str(x) for x in ids]
        names = os.listdir(TASK_SYNC)
        for name in names:
            prefix = name.split(".")[0]
            if prefix in ids:
                os.remove(os.path.join(TASK_SYNC, name))
            else:
                pass
        return mes

    @classmethod
    def cancel_data(cls, ids: list) -> dict:
        """
        撤销导入的文件
        :param ids: cls._id的list
        :return:
        """
        mes = {"message": "success"}
        ids2 = [x if isinstance(x, ObjectId) else ObjectId(x) for x in ids]
        f = {"sync_id": {"$in": ids2}}
        w = orm_module.get_write_concern()
        col = orm_module.get_conn(table_name="code_info", write_concern=w)
        u = {"$unset": {"sync_id": "", "task_id": "", "level": ""}}
        col.update_many(filter=f, update=u)
        mes = cls.delete_file_and_record(ids=ids2, include_record=True)
        return mes

    @classmethod
    def paging_info(cls, filter_dict: dict, sort_cond: dict = None, page_index: int = 1, page_size: int = 10,
                    can_json: bool = False) -> dict:
        """
        分页查看角色信息
        :param filter_dict: 过滤器,由用户的权限生成
        :param sort_cond: 过滤器,由用户的权限生成
        :param page_index: 页码(当前页码)
        :param page_size: 每页多少条记录
        :param can_json: 转换成可以json的字典?
        :return:
        """
        sort_cond = {"time": -1} if sort_cond is None else sort_cond
        join_cond = {
            "table_name": "produce_task",
            "local_field": "task_id",
            "field_map": {"batch_sn": "batch_sn", "_id": 0},
            "flat": True
        }
        kw = {
            "filter_dict": filter_dict,
            "join_cond": join_cond,
            "sort_cond": sort_cond,
            "page_index": page_index,
            "page_size": page_size,
            "can_json": can_json
        }
        res = cls.query(**kw)
        return res


if __name__ == "__main__":
    # a = "aasa\n\r\n\t"
    # UploadFile.import_code("5bf3aad85e32d75611898054")
    # UploadFile.all_file_name()
    f = "/home/walle/work/projects/query_server/task_sync"
    f_name2 = "task.json"
    f_name1 = "task.zip"
    p = os.path.join(f, f_name2)
    TaskSync.read_file(p)
    pass