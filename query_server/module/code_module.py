# -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import orm_module
import datetime


"""
条码模块
"""


ObjectId = orm_module.ObjectId
cache = orm_module.RedisCache()


class CodeInfo(orm_module.BaseDoc):
    """条码信息"""
    _table_name = "code_info"
    type_dict = dict()
    type_dict['_id'] = str  # 条码的码
    type_dict['product_id'] = ObjectId  # 产品id
    type_dict['file_id'] = ObjectId     # 导入时的文件id
    type_dict['used'] = int     # 是否使用? 0 是未使用

    @classmethod
    def query_code(cls, code: str) -> int:
        """
        查询条码
        :param code:
        :return:
        """
        res = 4
        f = {"_id": code}
        r = cls.find_one(filter_dict=f)
        if r is None:
            pass
        else:
            r.get("used")
            if r == 0:
                res = 0
            else:
                res = 1
        return res




if __name__ == "__main__":
    pass
