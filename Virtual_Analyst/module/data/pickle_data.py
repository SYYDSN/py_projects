# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
from log_module import get_logger
import pandas as pd


Series = pd.Series
DataFrame = pd.DataFrame
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
cache = mongo_db.RedisCache()
logger = get_logger()


def draw_data_from_db():
    """
    从数据库获取分析师的喊单信号。打包成DataFrame类型并返回
    :return:
    """
    ses = mongo_db.get_conn("signal_info")
    signals = ses.find(filter=dict())
    signals = [x for x in signals]
    signals = DataFrame(data=signals)
    print(signals)


if __name__ == "__main__":
    draw_data_from_db()

