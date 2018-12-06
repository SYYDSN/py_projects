# -*- coding: utf-8 -*-
import os
import sys
__root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __root_path not in sys.path:
    sys.path.append(__root_path)
import orm_module
from flask import request
import datetime
import re
import json
import numpy as np
import chardet
from io import TextIOWrapper


"""
文件的处理模块,包括:
1. 导入文件时对文件的解析
2. 合成导出文件
"""

root_dir = __root_path
cache = orm_module.RedisCache()
ObjectId = orm_module.ObjectId
IMPORT_DIR = os.path.join(__root_path, "import_data")  # 上传文件的默认目录
EXPORT_DIR = os.path.join(__root_path, "export_data")  # 导出文件的默认目录
if not os.path.exists(IMPORT_DIR):
    os.makedirs(IMPORT_DIR)
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)


class PrintCode(orm_module.BaseDoc):
    """导出打印条码记录"""
    _table_name = "print_code"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['file_name'] = str   # 文件名,包含
    type_dict['file_size'] = int   # 文件名,包含
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
                                    pass # 成功
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


class UploadFile(orm_module.BaseDoc):
    """上传文件的记录/导入记录"""
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
            print(product_id)
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
                        pass  # 成功
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
    type_dict['file_type'] = str           # 上传的时候使用的文件的类型
    type_dict['task_id'] = ObjectId        # 关连的任务id
    type_dict['product_id'] = ObjectId     # 关连的产品id
    type_dict['embedded_id'] = ObjectId    # 关连的主控板id
    type_dict['time'] = datetime.datetime  # 同步日期

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
            mes['message'] = "没有找到回传的文件"
        else:
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
                    pass  # 成功
                r = col1.insert_one(document=doc)
                if isinstance(r, orm_module.InsertOneResult):
                    pass  # 成功
                else:
                    mes['message'] = "保存导入记录失败"


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
        data = list()
        with open(file=file_path, mode="rb", encoding="utf-8") as f:
            data = json.loads(f)

        """条码统计的信息"""

        res = {
            "valid_count": res['valid_count'],
            "values": res.pop('values', None)
        }
        f.close()
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


if __name__ == "__main__":
    # a = "aasa\n\r\n\t"
    # UploadFile.import_code("5bf3aad85e32d75611898054")
    # UploadFile.all_file_name()
    """测试导出文件"""
    col = orm_module.get_conn(table_name="code_info")
    col.delete_many(filter=dict())
    pass