#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from module.sql_module import *
import datetime
import math
from flask import request
from urllib.parse import unquote
from module.user_module import User


d_path = os.path.join(__project_dir__, "documents")


class Document(BaseModel):
    """
    markdown文档文件
    """
    id = PrimaryKeyField()
    file_name = CharField(max_length=2000)
    file_type = CharField(max_length=100)
    file_series = CharField()                                # 文档类型
    order_value = IntegerField(default=1)  # 排序的值
    file_size = IntegerField()  # 文件尺寸
    dir_path = CharField()     #  相对于系统根目录的路径
    user_id = ForeignKeyField(model=User, field="id", backref="document")
    create_time = DateTimeField(default=datetime.datetime.now)
    last_time = DateTimeField(default=datetime.datetime.now)  # 最后的修改时间

    class Meta:
        table_name = "document"

    @classmethod
    @db.connection_context()
    def get_series(cls) -> list:
        """
        获取所有文档的系列名
        :return:
        """
        r = cls.select(cls.file_series).distinct()
        return [x.file_series for x in r]

    @classmethod
    @db.connection_context()  # 数据库上下文处理器
    def upload_file(cls, req: request, user: dict, force:  bool = False) -> dict:
        """
        上传markdown文件.
        :param req:
        :param user:
        :param force: 是否覆盖同名文件.
        :return:
        """
        mes = {"message": "success"}
        if len(req.files) > 0:
            file = req.files.get("file")
            file_name = file.filename
            file_series = unquote(req.headers.get("series"), encoding="utf-8")  # 文件类别
            if file_name.lower().endswith(".pdf") or file_name.lower().endswith(".md"):
                file_type = file.content_type
                dir_path = os.path.join(d_path, user['root_path'])
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                else:
                    pass
                file_path = os.path.join(dir_path, file_name)
                with open(file_path, "wb") as f:
                    file.save(dst=f)  # 保存文件
                file_size = os.path.getsize(file_path)
                now = datetime.datetime.now()
                user_id = user['id']

                doc = {
                    "file_name": file_name,
                    "file_type": file_type,
                    "file_series": file_series,
                    "file_size": file_size,
                    "dir_path": dir_path,
                    "user_id": user_id,
                    "create_time": now,
                    "last_time": now
                }
                record = cls(**doc)
                r = record.save()
                if isinstance(r, int):
                    pass
                else:
                    mes['message'] = "保存失败"
            else:
                mes['message'] = "目前仅仅支持markdown和pdf类型的文档"
        else:
            mes['message'] = "没有发现需要上传的文件"
        return mes

    @classmethod
    @db.connection_context()  # 数据库上下文处理器
    def paginate(cls, where: dict, page_index: int = 1, page_size: int = 15, ruler: int = 5) -> dict:
        """

        :param where:
        :param page_index:
        :param page_size:
        :param ruler: 翻页器最多显示几个页码？
        :return:
        """
        if len(where) == 0:
            handler = cls.select(cls, User).join(User)
        else:
            if "file_series" in where and "word" in where:
                word = where['word']
                handler = cls.select(cls, User).join(User).where(
                    (cls.file_series == where['file_series']) & (
                                (cls.file_name.contains(word)) or cls.file_name.startswith(word) or
                                cls.file_name.endswith(word)))
            elif "file_series" in where:
                handler = cls.select(cls, User).join(User).where(cls.file_series == where['file_series'])
            else:
                word = where['word']
                handler = cls.select(cls, User).join(User).where((cls.file_name.contains(word)) or
                                                                 cls.file_name.startswith(word) or
                                                                 cls.file_name.endswith(word))
        r = handler.order_by(cls.create_time.desc()).paginate(page=page_index, paginate_by=page_size)
        results = list()
        record_count = handler.count()
        for x in r:
            temp = x.get_dict()
            temp['user_name'] = x.user_id.nick_name if x.user_id.nick_name else x.user_id.user_name
            results.append(temp)
        page_count = math.ceil(record_count / page_size)  # 共计多少页?
        delta = int(ruler / 2)
        range_left = 1 if (page_index - delta) <= 1 else page_index - delta
        range_right = page_count if (range_left + ruler - 1) >= page_count else range_left + ruler - 1
        pages = [x for x in range(range_left, int(range_right) + 1)]
        total_page = 1 if page_count == 0 else page_count  # 最少显示页码1
        resp = {
            "total_record": record_count,
            "total_page": total_page,
            "data": results,
            "current_page": total_page if page_index > total_page else (page_index if page_index > 1 else 1),
            "pages": pages
        }
        return resp

    @classmethod
    @db.connection_context()   # 数据库上下文处理器
    def get_file_path(cls, file_id: int) -> dict:
        """
        获取文件绝对路径
        :param file_id:
        :return: dict
        """
        r = cls.get_by_id(pk=file_id)
        if isinstance(r, Document):
            resp = {
                "file_path": os.path.join(r.dir_path, r.file_name),
                "file_name": r.file_name,
                "file_type": r.file_type
            }
            return resp
        else:
            return None

    @classmethod
    @db.connection_context()  # 数据库上下文处理器
    def remove_one(cls, user_id: int, doc_id: int) -> dict:
        """
        删除一个文档
        :param user_id:
        :param doc_id:
        :return:
        """
        mes = {"message": "success"}
        r = cls. get_by_id(pk=doc_id)
        doc = r.get_dict()
        if user_id != doc['user_id']:
            mes['message'] = "只能删除自己的文档"
        else:
            p = os.path.join(r.dir_path, r.file_name)
            os.remove(p)
            r.delete_instance()
        return mes


models = [
    Document
]
db.create_tables(models=models)


if __name__ == "__main__":
    # print(Document.paginate())
    r = Document.get_by_id(2)
    r = r.get_dict(recurse=True)
    print(r)
    Document.get_series()
    pass