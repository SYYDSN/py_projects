# -*-coding:utf-8-*-
import db_module
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import inspect
import random

"""负责分配策略的模块"""

cache = db_module.cache
Base = declarative_base(bind=db_module.engine)


class Position(Base):
    """职位信息表"""
    __tablename__ = "position_info"
    sn = Column(Integer, primary_key=True, autoincrement=True)
    position_name = Column(String(50), nullable=False, unique=True)  # 职位名称

    def __init__(self, name):
        self.position_name = name

    def get_sn(self):
        return self.sn

    def get_name(self):
        return self.position_name

    def __repr__(self):
        return "sn={} , position_name={};".format(self.sn, self.position_name)


class SourceType(Base):
    """客户来源类型"""
    __tablename__ = "source_type"
    sn = Column(Integer, primary_key=True, autoincrement=True)
    source_name =  Column(String(50), nullable=False, unique=True)

    def __init__(self, source_name):
        self.source_name = source_name


class Customer(Base):
    """客户对象"""
    __tablename__ = "customer_info"
    user_sn = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(50), nullable=False, default='')
    user_phone = Column(String(11), nullable=False, unique=True)
    page_url = Column(String(1000), nullable=False, default='')
    create_date = Column(DateTime, nullable=False)
    team_sn = Column(Integer, ForeignKey("team_info.sn"), default=1)
    source_sn = Column(Integer, ForeignKey("source_type.sn"), default=1)  # 客户来源的sn

    def __init__(self, user_name, user_phone, page_url, source_sn):
        self.user_name = user_name
        self.user_phone = user_phone
        self.page_url = page_url
        self.source_sn = source_sn
        self.create_date = db_module.current_datetime()


class Staff(Base):
    """员工对象"""
    __tablename__ = "staff_info"
    sn = Column(Integer, primary_key=True, autoincrement=True)
    real_name = Column(String(50), nullable=False)
    user_phone = Column(String(11), nullable=False, unique=True)
    user_password = Column(String(200), nullable=False)
    is_leader = Column(Integer, nullable=False, default=0)  # 是否是团队leader，也就是是否可以操作团队对象
    position_sn = Column(Integer, ForeignKey("position_info.sn"))  # 职位sn
    create_date = Column(DateTime, nullable=False)
    staff_status = Column(Integer, nullable=False, default=1)  # 用户状态

    def __init__(self, real_name, user_phone, user_password="123456", is_leader=0, position_sn=1):
        """
        员工构造器
        :param real_name: 真实姓名，必须。
        :param user_phone: 员工手机，唯一。
        :param user_password: 员工密码，默认 123456。
        :param is_leader: 是否有分配权/操作团队的权利。默认0，没有。
        :param position_sn: 职位，默认是0，投资顾问。
        """
        self.real_name = real_name
        self.user_phone = user_phone
        self.user_password = user_password
        self.is_leader = is_leader
        self.position_sn = position_sn
        self.create_date = db_module.current_datetime()
        self.staff_status = 1

    def set_position_sn(self, position_sn):
        self.position_sn = position_sn

    def get_position_sn(self):
        return self.position_sn

    def set_is_leader(self, is_leader):
        self.is_leader = is_leader

    def get_is_leader(self):
        return self.is_leader

    def set_real_name(self, real_name):
        self.real_name = real_name

    def get_real_name(self):
        return self.real_name

    def set_user_phone(self, real_name):
        self.real_name = real_name

    def get_user_phone(self):
        return self.real_name

    def set_user_password(self, user_password):
        self.user_password = user_password

    def get_user_password(self):
        return self.user_password

    def set_staff_status(self, staff_status):
        self.staff_status = staff_status

    def get_staff_status(self):
        return self.staff_status

    def set_all(self, **kwargs):
        for k, v in kwargs.items():
            if k == "sn":
                raise ValueError("sn不可设置")
            elif hasattr(Staff, k):
                o = "self.set_{}('{}')".format(k, v)
                eval(o)
            else:
                raise ValueError("不存在的属性：{}".format(k))

    def __repr__(self):
        return "sn={},real_name={},user_name={},user_password={},is_leader={},position_sn={},create_date={}," \
               "staff_status={}".format(self.sn, self.real_name, self.user_phone, self.user_password, self.is_leader,
                                        self.position_sn, self.create_date, self.staff_status)


class Team(Base):
    __tablename__ = "team_info"
    sn = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String(50), nullable=False, unique=True)
    team_member = relationship("Staff", uselist=True, back_populates="sn")
    customer_pool = relationship("Customer", uselist=True, back_populates="user_sn")

    def __init__(self, team_name, leader_sn):
        """创建一个Team对象"""
        self.team_name = team_name
        self.leader_sn = leader_sn
        self.team_member = list()
        self.customer_pool = list()

    def __repr__(self):
        return "sn={} , team_name={};".format(self.sn, self.team_name)


Base.metadata.create_all()

staff = Staff("张三", "15012343432")
ses = db_module.sql_session()
# ses.add(staff)
# ses.commit()
staff = ses.query(Staff).filter(Staff.sn == 1).one()
staff.set_all(real_name="李四3", user_password=1111111)
ses.merge(staff)
ses.commit()
staff = ses.query(Staff).filter(Staff.sn == 1).all()
ses.close()
print(staff)
