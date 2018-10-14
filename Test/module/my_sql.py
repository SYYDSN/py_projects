# -*- coding: utf-8 -*-
import os
import sys
__root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __root_path not in sys.path:
    sys.path.append(__root_path)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import redis


"""配置数据库相关参数"""

ip = "127.0.0.1"
user = "root"  # 生产用数据库账户
password = "123456"  # 生产用数据库密码
database = "test_db"  # 数据库名称
charset = "utf8"  # 数据库字符集
pool_size = 20  # 数据库连接池
max_overflow = 5  # 数据库连接溢出数
pool_recycle = 3600  # 数据库连接超时回收时间


"""
初始化SQLalchemy引擎,其中strategy='threadlocal' 是使用本地线程模式。其目的是为了保证
在多线程状态下的线程安全。max_overflow是指数据库连接池满了以后，还允许新建多少线程?
如果设置过大，可能触及mysql配置的底线导致mysql出错。如果设置太小，那么一点超出连接池
的话，可能会遇到获取不到数据库连接的错误。session会自己管理连接池和连接的断开情况。
pool_recycle这个参数一定要设置，这个是数据库连接的闲置超时回收时间，默认是-1，也就是永远不主动
回收数据库连接，这样的话，一旦连接的闲置时间超过数据库的默认设置（mysql默认是8个小时，也就是28800秒。）
数据库就会主动断开连接，而应用却不知道连接已断开。当前的设置是3600秒，
也就是一小时，实际设置只要小于数据库的默认闲置超时就好了，
mysql下查看相关设置可以使用
show variables like '%timeout%';
其中的wait_timeout 就是对应的值
注意url结尾的那个?charset=utf8 必须设置，否则中文插入会出问题，因为sqlalchemy默的是
latin1字符集
"""
engine = create_engine(
    "mysql+pymysql://{0}:{1}@{2}/{3}?charset={4}".format(user, password, ip, database, charset),
    echo=False, echo_pool=False, max_overflow=max_overflow, pool_size=pool_size, pool_recycle=pool_recycle,
    strategy='threadlocal')

"""autoflush的意思是在orm状态下，使用session的add(a)方法加入或者delete(a)方法从数据库删除
一个a对象对应的记录时，无需flush的方法即可生效，可以理解为类似conn.commit()的方法，如果你不使用orm的话，
这个设置选项无关紧要,autocommit的默认值就是False，这里设置是为了做示范"""
DB_Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def sql_session():
    """返回一个SQLalchemy.orm.session.Session 的实例"""
    return DB_Session()


def structure_sql(the_type, table_name, query_terms=None, **kwargs):
    """
    构造对数据库的添加，删除，修改 功能的sql语句。
    第一个参数是the_type，表示操作的类型：add,delete,edit
    第二个参数是要操作的表名。
    第三个参数是是查询的条件的sql语句部分，包括where order by等，
    例如：query_terms='where sn=123 and name like '%张%'order by create_date desc'
    **kwargs表示关键字参数，是user_info的表的列名和值组成的字典。例如：
    {"user_name":username,....,"user_password":user_password}
    """
    if the_type == "add":
        """生成insert语句"""
        data = kwargs
        sql = "insert into {}".format(table_name)
        keys = "("
        values = "values("
        for k, v in data.items():
            keys += "{},".format(k)
            values += "'{}',".format(v) if isinstance(v, str) else "{},".format(v)
        keys = keys.rstrip(",")
        values = values.rstrip(",")
        keys += ") "
        values += ")"
        sql += keys + values
        return sql
    elif the_type == 'edit':
        """生成update语句"""
        data = kwargs
        sql = "update {} set ".format(table_name)
        part = ""
        for k, v in data.items():
            part += "{0}={1},".format(k, "'{}'".format(v) if isinstance(v, str) else v)
        part = part.rstrip(",")
        if query_terms is None:
            raise ValueError("编辑时，筛选条件不能为空")
        else:
            return sql + part + " " + query_terms
    elif the_type == "select":
        if query_terms is None:
            raise ValueError("查找时，筛选条件不能为空")
        else:
            sql = "select {} from {} {}".format(",".join(get_columns(table_name)), table_name, query_terms)
            return sql
    elif the_type == "delete":
        """生成delete语句"""
        sql = "delete from {0} ".format(table_name)
        if query_terms is None:
            raise ValueError("删除时，筛选条件不能为空")
        else:
            return sql + query_terms
    else:
        raise KeyError("未知的操作类型")


def get_columns(table_name, first=False):
    """获取所有的table_name表的列名，只在启动程序时运行一次,参数
    first是代表是否第一次启动，如果第一次启动要强制重新加载列名"""
    redis_client = MyRedis.redis_client()
    key = "{}_columns".format(table_name)
    value = redis_client.get(key)
    if value is None or first:
        sql = "SHOW columns FROM {}".format(table_name)
        session = sql_session()
        proxy_result = session.execute(sql)
        session.close()
        result = proxy_result.fetchall()
        """列名包含infocol字段的是预留列，不参与操作"""
        value = json.dumps([x[0] for x in result if x[0].find("infocol") == -1]).encode()
        redis_client.set(key, value)
    return json.loads(value.decode())


class MyRedis:
    """获取redis的客户端"""

    def __init__(self):
        """注意，数据的存储方式都是：表名+_+主键"""
        pass

    def __new__(cls, *args, **kwargs):
        """获取连接池的初始化方法，单例模式，因为redis会自己管理连接池"""
        if not hasattr(cls, 'instance'):
            obj = super(MyRedis, cls).__new__(cls)
            pool = redis.ConnectionPool(host='localhost', port=6379, db=0, password='')
            client = redis.Redis(connection_pool=pool)
            obj.client = client
            cls.instance = obj
        return cls.instance

    def get_redis_client(self):
        """返回一个Redis对象的实例"""
        return self.client

    def get_redis_pipe(self):
        """返回一个Redis的管道化实例，这在批量操作时会有更好的性能,但和Redis实例比，
        要多一个execute的动作"""
        return self.client.pipeline()

    def get_redis_pubsub(self):
        """返回一个pubsub的实例。注意，这个实例对象是用来订阅消息的。
        如果你需要发送或者发送+订阅消息，你需要的是一个Redis的实例对象"""
        return self.client.pubsub()

    @staticmethod
    def redis_client():
        """返回一个Redis对象的实例的静态方法"""
        return MyRedis().get_redis_client()

    @staticmethod
    def redis_pubsub():
        """返回一个pubsub的实例的静态方法。注意，这个实例对象是用来订阅消息的。
        如果你需要发送或者发送+订阅消息，你需要的是一个Redis的实例对象"""
        return MyRedis().get_redis_pubsub()

    @staticmethod
    def redis_pipe():
        """返回一个Redis的管道化实例的静态方法，这在批量操作时会有更好的性能,但和Redis实例比，
        要多一个execute的动作"""
        return MyRedis().get_redis_pipe()
