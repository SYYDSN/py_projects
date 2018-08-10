# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
from log_module import get_logger


ObjectId = mongo_db.ObjectId
logger = get_logger()


"""行情模块,本项目中,这个模块只是示范,用于测试环境,生产环境下,请参考quotations_server.module.quotations_module模块"""


class Quotation(mongo_db.BaseDoc):
    """
    行情报价信息
    """
    __table_name = "quotation"
    type_dict = dict()
    type_dict['_id'] = ObjectId
