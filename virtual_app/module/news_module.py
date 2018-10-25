#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
import datetime
from tools_module import get_logger


"""新闻模块"""


logger = get_logger()
ObjectId = orm_module.ObjectId


class News(orm_module.BaseDoc):
    """新闻"""
    _table_name = "news_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['title'] = str
    type_dict['img'] = str
    type_dict['content'] = str

    @classmethod
    def read_js(cls):
        """导入json文件,一次性函数"""
        file_path = "services.js"
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            content = eval(content)
            insert_list = [{"title": x['titleNews'], "img": x['imgNews'], "content": x['contentNews']} for x in content]
        if len(insert_list) > 0:
            insert_result = cls.insert_many(doc_list=insert_list)
            print(insert_result)


if __name__ == "__main__":
    pass