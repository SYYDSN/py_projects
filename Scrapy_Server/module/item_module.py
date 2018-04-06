# -*- coding:utf-8 -*-
import sys
import os
"""直接运行此脚本，避免import失败的方法"""
__item_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __item_dir not in sys.path:
    sys.path.append(__item_dir)
import mongo_db
from log_module import get_logger
import scrapy


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
logger = get_logger()