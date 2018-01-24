# -*- coding: utf-8 -*-
from hashlib import md5
import datetime
import os
import pickle
import mongo_db


"""记录mongodb配置的模块,具体的配置文件保存在 resource/mongo_setting目录下"""


class Log(mongo_db.BaseDoc):
    """mongodb数据库的日志类"""
    _table_name = "log_info"
    type_dict = dict()
    type_dict['_id'] = mongo_db.ObjectId  # id 唯一
    type_dict['setting_id'] = mongo_db.DBRef  # 对应的DBSetting的id，相当于外键
    type_dict['log_date'] = datetime.datetime  # 一条日志的时间
    type_dict['log_type'] = str  # 一条日志的类型 一般都是CONTROL
    type_dict['message_type'] = str  # 一条日志的消息类型，中括号里面的部分
    type_dict['log_content'] = str  # 日志的主体内容
    type_dict['last_seek'] = int  # 文件指针最后的位置,用于从最后的位置接着读取。


class DBSetting(mongo_db.BaseDoc):
    """数据库的配置文件"""
    _table_name = "setting_info"
    type_dict = dict()
    type_dict['_id'] = mongo_db.ObjectId  # id 唯一
    type_dict['file_path'] = str  # 日志保存路径
    type_dict['create_date'] = datetime.datetime  # 此对象的创建时间
    type_dict['host'] = str  # 主机地址/域名
    type_dict['port'] = int  # 主机数据库的访问端口

    @classmethod
    def create(cls, **kwargs):
        """创建实例的方法，建议不要使用__init__而是本方法来创建新实例"""
        now = datetime.datetime.now()
        if '_id' not in kwargs:
            kwargs['_id'] = mongo_db.ObjectId()
        if 'create_date' not in kwargs:
            kwargs['create_date'] = now
        if 'db_type' not in kwargs:
            kwargs['db_type'] = 'mongodb'
        if 'port' not in kwargs:
            raise ValueError("缺少必要的参数,port")
        if "host" not in kwargs or "file_path" not in kwargs:
            raise ValueError("缺少必要的参数,name:{},file_path:{}".format(kwargs.get("name"), kwargs.get("file_path")))
        return cls(**kwargs)

    def exists(self) -> bool:
        """
        检查一个实例是否存在于数据库中？
        :return:
        """
        filter_dict = {"host": self.get_attr('host'), 'port': self.get_attr("port"),
                       "file_path": self.get_attr("file_path")}
        res = self.__class__.find_one_plus(filter_dict=filter_dict)
        return False if res is None else True
    
    def read_log(self, threshold_size: int = 64) -> list:
        """
        读取一个mongo实例的日志文件,返回日志文件的记录
        threshold_size: 文件的最大尺寸，超过此此尺寸的文件将只读取最后的部分.
        return: 记录组成的list
        """
        log_path = self.get_attr('file_path')
        f = open(log_path, "r", encoding="utf-8")
        # max_seek = f.seek(0, os.SEEK_END)   # 文件指针到末尾并返回最大指针数值
        # seek_num = max_seek - back_off
        # current_seek = f.seek(seek_num, os.SEEK_SET)  # 调整文件指针到倒数100的位置
        max_seek = f.seek(0, os.SEEK_END)
        file_size = os.path.getsize(log_path)
        print(max_seek, file_size)
        f.close()

if __name__ == "__main__":
    init_dict = {
        "name": "test", "file_path": "/var/log/mongodb/mongod.log",
        "host": "127.0.0.1", "port": 27017
    }
    mon = DBSetting.create(**init_dict)
    mon.save()
    print(mon)