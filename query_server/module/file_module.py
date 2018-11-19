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
import chardet


"""
文件的处理模块,包括:
1. 导入文件时对文件的解析
2. 合成导出文件
"""


ObjectId = orm_module.ObjectId


class UploadFile(orm_module.BaseDoc):
    """上传文件的记录"""
    _table_name = "upload_file_history"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['file_name'] = str
    type_dict['storage_name'] = str
    type_dict['file_size'] = int  # 单位字节
    type_dict['file_type'] = str
    type_dict['upload_time'] = datetime.datetime
    type_dict['import_time'] = datetime.datetime

    @classmethod
    def upload(cls, req: request, dir_path: str) -> dict:
        """
        上传条码文件
        :param req:
        :param dir_path:
        :return:
        """
        mes = {"message": "success"}
        file = req.files.get("file")
        if file is None:
            mes['message'] = "没有找到上传的文件"
        else:
            file_name = file.filename
            file_type = file.content_type
            _id = ObjectId()
            storage_name = "{}.{}".format(str(_id), file_name.split(".")[-1])
            f_p = os.path.join(dir_path, storage_name)
            with open(f_p, "wb") as f:
                file.save(dst=f)
            file_size = os.path.getsize(f_p)
            doc = {
                "_id": _id,
                "file_name": file_name,
                "storage_name": storage_name,
                "file_size": file_size,
                "file_type": file_type,
                "upload_time": datetime.datetime.now()
            }
            col = cls.get_collection(write_concern=orm_module.get_write_concern())
            r = col.insert_one(document=doc)
            if isinstance(r, orm_module.InsertOneResult):
                cls.read_file(file_path=f_p)
            else:
                mes['message'] = "保存失败"
        return mes

    @classmethod
    def read_file(cls, file_path) -> dict:
        """
        读取文件
        :param file_path:
        :return:
        """
        res = None
        f = open(file=file_path, mode="rb")
        data = f.readline()
        info = chardet.detect(data)
        encoding = info['encoding']      # 编码
        confidence = info['confidence']  # 置信度
        language = info['language']      # 语言
        f.close()
        if os.path.exists(file_path):
            with open(file_path, mode="r", encoding=encoding) as lines:
                for line in lines:
                    print(line)
        else:
            pass
        return res

    @classmethod
    def parse_line(cls, line: str) -> dict:
        """
        解析读取的一行数据
        :param line:
        :return:
        """
        line = line.strip()
        print(line)
        re.


def get_file_info(file_name: str, limit: int = 100) -> dict:
    """
    获取文件信息
    :param file_name:
    :param limit:
    :return:
    """


if __name__ == "__main__":
    a = "aasa\n\r\n\t"
    UploadFile.parse_line(a)
    pass