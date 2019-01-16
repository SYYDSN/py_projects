#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from peewee import MySQLDatabase


"""
数据库连接模块
"""

setting = {
    "provider": "mysql",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "wise_oa",
    "user": "root",
    "password": "Xx@mysql312"
}
mysql_db = MySQLDatabase(**setting)



if __name__ == "__main__":
    pass
