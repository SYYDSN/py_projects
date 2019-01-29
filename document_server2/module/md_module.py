#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from module.sqlite_module import *
import datetime
from flask import request


d_path = os.path.join(__project_dir__, "documents")


class Document(BaseModel):
    """
    markdown文档文件
    """
    id = PrimaryKeyField()
    file_name = CharField(max_length=2000)
    file_type = CharField(max_length=100)
    file_size = IntegerField()  # 文件尺寸
    dir_path = CharField()    #  相对于系统根目录的路径
    user_id = IntegerField()
    create_time = DateTimeField(default=datetime.datetime.now)
    last_time = DateTimeField(default=datetime.datetime.now)  # 最后的修改时间

    class Meta:
        table_name = "document"

    @classmethod
    def upload_file(cls, req: request, user: dict, force:  bool = False) -> dict:
        """
        上传markdown文件.
        :param req:
        :param user:
        :param force: 是否覆盖同名文件.
        :return:
        """
        mes = {"message": "success"}
        files = req.files
        if len(req.files) > 0:
            file = req.files.get("file")
            file_name = file.filename
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
                "file_size": file_size,
                "dir_path": dir_path,
                "user_id": user_id,
                "create_time": now,
                "last_time": now
            }
            r = cls.insert(**doc)
            r
        else:
            mes['message'] = "没有发现需要上传的文件"
        return mes


if __name__ == "__main__":
    pass