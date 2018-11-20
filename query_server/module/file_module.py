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
from io import TextIOWrapper


"""
文件的处理模块,包括:
1. 导入文件时对文件的解析
2. 合成导出文件
"""


cache = orm_module.RedisCache()
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
    type_dict['valid_index'] = int      # 有效列
    type_dict['valid_count'] = int      # 有效条码计数
    type_dict['valid_count'] = int      # 无效条码计数
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
                r = cls.read_file(file_path=f_p)
                if isinstance(r, dict) and r.get("valid_count", 0) > 0:
                    """成功"""
                    pass
                else:
                    mes['message'] = "没有解析到正确的结果"
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
                res = cls.parse_lines(lines)
        else:
            pass
        """修改条码统计的信息"""
        _id = ObjectId(file_path.split("/")[-1].split(".")[0])
        f = {"_id": _id}
        u = {"$set":
            {
                "valid_index": res['valid_index'],
                "valid_count": res['valid_count'],
                "invalid_count": res['invalid_count']
            }
        }
        w = orm_module.get_write_concern()
        col = cls.get_collection(write_concern=w)
        col.find_one_and_update(filter=f, update=u, upsert=False)
        values = res.pop('values', None)
        if values is not None:
            """设置缓存"""
            cls.cache_values(_id, values)
        else:
            pass
        return res

    @classmethod
    def discovery_feature(cls, lines: list) -> dict:
        """
        从一行读取的数据中发现特征
        :param lines:
        :return:
        """
        value = ""
        index = -1
        for i, x in enumerate([re.findall('\d{12,}', line) for line in lines]):
            if len(x) > len(value):
                value = x
                index = i

        return dict() if index == -1 else {"index": index, "value": value[0]}

    @classmethod
    def parse_lines(cls, lines: (TextIOWrapper, list)) -> dict:
        """
        解析读取的一行数据
        :param lines:
        :return:
        """
        s = dict()
        for line in lines:
            line = line.strip()
            res = cls.discovery_feature(line.split(","))
            index = res.get("index")
            if index is None:
                pass
            else:
                temp = s.get(index)
                if temp is None:
                    temp = {"count": 0, "values": []}
                else:
                    pass
                temp['count'] += 1
                temp['values'].append(res['value'])
                s[index] = temp
        s = [{"index": k, "info": v} for k, v in s.items()]
        s.sort(key=lambda obj: obj['info']['count'], reverse=True)
        valid = s.pop(0)
        valid_index = valid['index']      # 有效索引
        info = valid['info']
        valid_count = info['count']      # 有效条码统计
        values = info['values']          # 有效条码
        invalid_count = sum([x['count'] for x in s])
        res = {
            "valid_count": valid_count, "invalid_count": invalid_count,
            "values": values, "valid_index": valid_index
        }
        return res

    @staticmethod
    def cache_values(file_id: (str, ObjectId), values: list) -> None:
        """
        缓存值
        :param file_id:
        :param values:
        :return:
        """
        file_id = file_id if isinstance(file_id, str) else str(file_id)
        cache.set(file_id, values, timeout=60 * 60)

    @staticmethod
    def get_values(key: str) -> list:
        """
        获取缓存的值
        :param key:
        :return:
        """
        values = cache.get(key=key)
        return list() if values is None else values

    @staticmethod
    def remove_cache(key: str) -> None:
        """
        清除缓存
        :param key:
        :return:
        """
        cache.delete(key=key)

    @classmethod
    def import_code(cls, key: str) -> bool:
        """
        导入数据
        :param key:
        :return:
        """
        key = str(key) if isinstance(key, ObjectId) else key
        values = cls.get_values(key)
        res = False
        if values is not None:
            file_id = ObjectId(key)
            values = [{"_id": x, "used": 0, "file_id": file_id} for x in values]
            w = orm_module.get_write_concern()
            col = orm_module.get_conn(table_name="code_info", write_concern=w)
            r = col.insert_many(documents=values)
            print(r)
            res = True
        return res


if __name__ == "__main__":
    a = "aasa\n\r\n\t"
    UploadFile.import_code("5bf3aad85e32d75611898054")
    pass