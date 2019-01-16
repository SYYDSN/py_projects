#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from pony.orm import Database
from pony.orm import PrimaryKey
from pony.orm import Required
from pony.orm import Optional
from pony.orm import Set
import datetime
from uuid import uuid4


"""
数据库连接模块
"""

db = Database()
setting = {
    "provider": "mysql",
    "host": "127.0.0.1",
    "port": 3306,
    "db": "wise_oa",
    "user": "root",
    "password": "Xx@mysql312"
}
db.bind(**setting)
# db.generate_mapping(create_tables=True)


class BaseEntity(db.Entity):
    """
    基础实体类
    """


class Rule(db.Entity):
    """
    用户规则.
    用于视图url和定义规则的值之间的关系.
    """
    url = Required(str, unique=True)



db.generate_mapping(create_tables=True)


if __name__ == "__main__":
    pass
