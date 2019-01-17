#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import datetime
import logging
from uuid import uuid4
from peewee import *
from playhouse.pool import PooledMySQLDatabase


"""
数据库连接模块
"""


logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
setting = {
    "host": "127.0.0.1",
    "port": 3306,
    "max_connections": 8,
    "stale_timeout": 300,
    "database": "wise_oa",
    "user": "root",
    "password": "Xx@mysql312"
}

db = PooledMySQLDatabase(**setting)


class BaseModel(Model):
    """
    自定义ORM模型基类.
    建议:
    1. 定义外键的时候,最好定义为xxx_id的形式,否则peewee会自动加_id后缀,引起列名不一致的情况.
    2. 没有查询到结果时会抛出 class.DoseNotExist(Person.DoseNotExist)异常
    3. 有关返回值,如果你查询一条记录,直接调用get_dict即可,如果查询多条记录,那就是[x.get_dict() for x in result]
    4. 如果你要自定义一个非自增长的int主键或者uuid主键,请不要使用PrimaryKeyField,而是id = IntegerField(primary_key=True)

    """

    class Meta:
        database = db              # 可被继承
        table_name = "base_model"  # 定义表名,不定义的话直接是类名转成小写. 不可被继承

    def get_dict(self) -> dict:
        """
        获取查询出来的数据的字典类型,注意,这个字典的key是在类中定义的key而不是数据库中对应表的真实列名.
        :return:
        """
        return self.__dict__.get('__data__')

    @classmethod
    def all_fields(cls) -> list:
        """
        返回所有定义的field
        :return:
        """
        return cls._meta.sorted_fields

    @classmethod
    def all_field_names(cls) -> list:
        """
        返回所有定义的field_name
        :return:
        """
        return cls._meta.sorted_field_names


class Employee(BaseModel):
    id = PrimaryKeyField(str)
    user_name = CharField(unique=True)


class Manager(BaseModel):
    employee_id = UUIDField(unique=True)
    message = TextField()
    create_date = DateTimeField(default=datetime.datetime.now)
    is_published = BooleanField(default=True)


class Job(BaseModel):
    model = "job_info"
    name = CharField(unique=True)


class Person(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    job_id = ForeignKeyField(model=Job, backref="person")
    create_time = DateTimeField(default=datetime.datetime.now)


models = [
    BaseModel, Manager, Employee, Job, Person
]
db.create_tables(models=models)

if __name__ == "__main__":
    # job = Job(name="建筑工人")
    # job_id = job.save()
    # pp = {
    #     "job_id": job_id,
    #     "name": "张三"
    # }
    # p = Person(**pp)
    # p.save()
    ##
    # cols = Person.all_fields()
    # cols.extend(Job.all_fields())
    p = dict()
    try:
        resp = Person.select(Person, Job).join(Job).where(Person.name == "张三").get()
        """如果是查询多个,那就是[x.get_dict() for x in p]"""
        p = resp.get_dict()
    except Person.DoesNotExist as e:
        print(e)
    finally:
        print(p)

    pass
