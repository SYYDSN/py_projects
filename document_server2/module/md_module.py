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
    file_size = IntegerField()  # 文件尺寸
    dir_path = CharField()    #  相对于d_path的路径
    owner_id = IntegerField()
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


if __name__ == "__main__":
    pass