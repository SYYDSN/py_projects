#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from pony_orm import *
from uuid import uuid4
import logging
from .organization import *
from pony_orm import *


logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


"""
app模块

用户

 权限(rule),
 
 权限组(权限组和权限之间是n:n的关系)
 权限组和权限的映射关系(表)
 
 角色(role)
  角色组(角色组和角色之间是1:n的关系)
  角色和权限之间的映射关系(表)
  
  用户和权限之间的映射关系(表)
"""

class AppTemplate(db.Entity):
    """
    app模块的原始信息(全集)
    """
    _table_ = "app_template"
    name = Required(str, max_len=128)  # 模块名
    url = Required(str, max_len=128)
    layer = Required(int, default=0)  # 模块的层级,0是顶层的.
    has_entry = Required(int, sql_default=0)  # 是否有自己的登录入口?
    root_id = Optional(int, nullable=True)  # 根app的id,
    parent_id =Required("AppTemplate",  default=0, reverse="parent_id")  # 上一级app的id
    name_en = Optional(str, max_len=128)  # 模块英文名
    desc = Required(str, max_len=1000, default='')  # 备注
    desc_en = Required(str, max_len=1000, default='')  #英文 备注
    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Required(datetime.datetime, default=datetime.datetime.now)  # 最后一次修改时间
    creator = Required("Employee", reverse="creator")  # 创建人.指向管理员id
    last_user = Required("Employee", reverse="last_user")  # 最后修改人.指向系统管理员id


class App(db.Entity):
    """
    app模块的原始信息(全集)
    """
    _table_ = "app"
    group_id = Required("HotelGroup")  # 集团id,外键
    name = Required(str, max_len=128)  # 模块名
    url = Required(str, max_len=128)
    layer = Required(int, default=0)  # 模块的层级,0是顶层的.
    has_entry = Required(int, sql_default=0)  # 是否有自己的登录入口?
    root_id = Optional(int, nullable=True)  # 根app的id,
    parent_id = Required("AppTemplate", default=0, reverse="parent_id")  # 上一级app的id
    name_en = Optional(str, max_len=128)  # 模块英文名
    desc = Required(str, max_len=1000, default='')  # 备注
    desc_en = Required(str, max_len=1000, default='')  # 英文 备注
    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Required(datetime.datetime, default=datetime.datetime.now)  # 最后一次修改时间
    creator = Required("Employee", reverse="creator")  # 创建人.指向管理员id
    last_user = Required("Employee", reverse="last_user")  # 最后修改人.指向系统管理员id


class Rule(db.Entity):
    """
    (业务接口的)权限, 这是用户规则的原始记录
    权限规则和api视图路由是1:1的关系
    """
    _table_ = "rule"
    url = Required(str, max_len=191, unique=True)  # 接口的url地址,不包含host,port和参数的全路径接口path,唯一
    name = Required(str,max_len=128, unique=True)  #  接口/规则的名字.唯一
    name_en = Required(str,max_len=128, unique=True)  #  接口/规则的英文名字.唯一
    desc = Required(str,max_len=1000, default='')  # '描述.本接口是干什么的?
    desc_cn = Required(str,max_len=1000, default='',)  # 英文描述.本接口是干什么的?
    level = Required(int, default=1)  # 权限的级别,0是系统管理员才能设定的选先,1是集团管理员可设定的, 2 是酒店管理员可设定的")
    status = Required(int, default=1)  # 是否可用,默认是可用.0的话就不能被选择加入权限组了.
    reg_time = Required(datetime.datetime, default=datetime.datetime.now)  # 注册时间


class UserRule(db.Entity):
    """
    用户权限. 这里保存的是用户和权限之间的映射关系
    """
    _table_ = "user_rule"
    raw_id = Required(str, max_len=191, unique=True)  # 接口的url地址,不包含host,port和参数的全路径接口path,唯一
    name = Required(str, max_len=128, unique=True)  # 接口/规则的名字.唯一
    name_en = Required(str, max_len=128, unique=True)  # 接口/规则的英文名字.唯一
    desc = Required(str, max_len=1000, default='')  # '描述.本接口是干什么的?
    desc_cn = Required(str, max_len=1000, default='', )  # 英文描述.本接口是干什么的?
    level = Required(int, default=1)  # 权限的级别,0是系统管理员才能设定的选先,1是集团管理员可设定的, 2 是酒店管理员可设定的")
    status = Required(int, default=1)  # 是否可用,默认是可用.0的话就不能被选择加入权限组了.
    reg_time = Required(datetime.datetime, default=datetime.datetime.now)  # 注册时间


class Employee(db.Entity):
    """
    企业内部的员工,
    由于员工的登录比较频繁.所以有专门的表记录员工的登录和操作.
    """
    _table_ = "employee"
    create_hotel_group = Set(HotelGroup)   # 外键设定
    user_name = Required(str, max_len=64)  # 用户名,用来登录
    password = Required(str, max_len=128)  # 密码.md5
    face_id = Optional(max_len=128,  nullable=True)  # 面部识别的id,暂时是假的
    user_card_id = Optional(max_len=128, nullable=True)  # 用户卡id,预留给员工卡登录,暂空

    employee_id = Optional(max_len=128, nullable=True)  # 工号, 可以用来做唯一性判定
    work_start = Optional(datetime.datetime, nullable=True)  # 参加工作日期
    entry_date = Optional(datetime.datetime, nullable=True)  # 入职时间
    work_status = Required(int, default=1)  # 在职状态,1在职,0离职
    hotel_id = Required(Hotel, column="hotel_id", reverse="employee")
    dept_id = Optional(Dept, column="dept_id", reverse="employee")
    job_id = Optional(Job, nullable=True, column="job_id")  # 职务id
    role_id = ForeignKeyField(model=UserRole, column="role_id", backref="employee")

    head_image = Required(str,max_len=128)  # 头像图片的id,文件名或者唯一地址")
    real_name = Required(str,max_len=128)  # 真实姓名, 可以登记英文或者中文")
    real_name_en = Required(str,max_len=128)  # 真实姓名, 可以登记英文或者中文")
    nick_name = Required(str,max_len=128)  # 昵称", default='')
    gender = Required(str,choices=("男", "女"), verbose_name="gender")  # 性别, 中文的男女即可")
    birth_date = DateField(formats='%Y-%m-%d', nullable=True)  # 出生年月")
    blood_type = Required(str,choices=("A", "B", "O", "AB", "其他", "未知"))  # 血型")
    degree = Required(str,choices=("小学及以下", "初中", "高中/技校", "大专", "本科及以上", "未知"))  # 学历")
    phone = Required(str,max_len=128)  # 手机号码, 和work_status, hotel_group_id联合做唯一判定")
    homeland = Required(str,max_len=128)  # 祖籍")
    birth_place = Required(str,nullable=True)  # 出生地")
    domicile_place = Required(str,max_len=128)  # 户口所在地")
    live_place = Required(str,max_len=128)  # 现在居住地")
    address = Required(str,max_len=128)  # 居住地址")
    political_status = Required(str,choices=("无", "共青团员", "共产党员", "其他"))  # 政治面貌")
    email = Required(str,max_len=128, nullable=True)  # 电子邮件")
    wx_code = Required(str,max_len=128, nullable=True)  # 微信号")
    open_id = Required(str,max_len=128, nullable=True)  # 微信open_id")
    union_id = Required(str,max_len=128, nullable=True)  # 微信union_id")
    qq = Required(str,max_len=128, nullable=True)  # qq号码")
    weibo = Required(str,max_len=128, nullable=True)  # 新浪微博")

    status = IntegerField(choices=(1, 0), default=1)  # 账户状态,1正常,0停用.")
    creator = IntegerField(verbose_name="创建者")  # 创建者id")
    create_time = DateTimeField(verbose_name="创建时间", default=datetime.datetime.now)
    last_user = IntegerField(verbose_name="修改者")  # 最后一个修改的人的id,创建的时候此id为创建者id, 注意,这里的操作者是酒店内部的管理员")
    last_time = DateTimeField(verbose_name="修改时间")  # 记录最后一次的修改时间, 注意,这里的操作者是酒店内部的管理员",
                              default=datetime.datetime.now)

    class Meta:
        table_name = "employee"
        indexes = [
            # 手机号码,酒店id和在职状态
            (("phone", "hotel_id", "work_status"), True),
            # 酒店下用户名唯一
            (("user_name", "hotel_id"), True),
        ]

    @classmethod
    @db.connection_context()
    def account_login(cls, user_name: str, password: str, hotel_id: int) -> dict:
        """
        账户密码登录,
        :param user_name:
        :param password:
        :param hotel_id:
        :return:
        用户登录成功后, 查询用户的
        1. app可访问列表.
        2. Role的id
        3. 一个时间戳

        """
        # mes = {"message": "success"}
        # cols = [
        #     cls.id, cls.real_name, cls.nick_name, cls.role_id, cls.dept_id, cls.job_id,
        #     UserRole.role_name,
        #     # Dept.name,
        #     # Job.name
        # ]
        # obj = cls.select(*cols).join_from(cls, UserRole).join_from(cls, Dept).join_from(cls, Hotel, on=(cls.hotel_id==Hotel.id)).join_from(cls, Job, on=(cls.job_id==Job.id)).where(
        #     (cls.user_name == user_name) & (cls.password == password)
        # ).get()
        # obj.get_dict(recurse=True, backrefs=True)
        obj = cls.select(
            cls, Job, UserRole, Dept, Hotel
        ).join_from(
            cls, UserRole
        ).join_from(
            cls, Dept
        ).join_from(
            cls, Hotel
        ).join_from(
            cls, Job, on=(Job.id == cls.job_id), attr='log'
        ).where(cls.id == 2).get()
        obj.get_dict(recurse=True, backrefs=True)
        """
        测试用的返回体.
        resp = {
            "message": "success",
            "apps": [                 # 可用的app列表
                      {
                        "project_name":'PMS',
                       "path":'/firstIndex'
                      },
                      {
                        "project_name":'内控店控',
                        "path":'/organizationchart'
                      },
                      {
                        "project_name":'会员',
                        "path":'/member'
                      },
                      {
                        "project_name":'铁管家',
                        "path":'/ironsteward'
                      },
                      {
                        "project_name":'会管家',
                        "path":'/firstIndex'
                      },
        
                      {
                        "project_name":'销控宝',
                        "path":'/firstIndex'
                      },
                      {
                        "project_name":'库管家',
                        "path":'/firstIndex'
                      },
                      {
                        "project_name":'地管家',
                        "path":'/firstIndex'
                      },
                      {
                        "project_name":'钱管家',
                        "path":'/firstIndex'
                      },
                      {
                        "project_name":'车管家',
                        "path":'/firstIndex'
                      },
                      {
                        "project_name":'客管家',
                        "path":'/firstIndex'
                      },
                      {
                        "project_name":'任务体系',
                        "path":'/firstIndex'
                      }
                ],
            "user_id": 5,
            "real_name": "张三",
            "job": "系统管理员",
            "role_id": 12,
        }
        """
        resp = {
            "message": "success",
            "apps": [  # 可用的app列表
                {
                    "project_name": 'PMS',
                    "path": '/firstIndex'
                },
                {
                    "project_name": '内控店控',
                    "path": '/organizationchart'
                },
                {
                    "project_name": '会员',
                    "path": '/member'
                },
                {
                    "project_name": '铁管家',
                    "path": '/ironsteward'
                },
                {
                    "project_name": '会管家',
                    "path": '/firstIndex'
                },

                {
                    "project_name": '销控宝',
                    "path": '/firstIndex'
                },
                {
                    "project_name": '库管家',
                    "path": '/firstIndex'
                },
                {
                    "project_name": '地管家',
                    "path": '/firstIndex'
                },
                {
                    "project_name": '钱管家',
                    "path": '/firstIndex'
                },
                {
                    "project_name": '车管家',
                    "path": '/firstIndex'
                },
                {
                    "project_name": '客管家',
                    "path": '/firstIndex'
                },
                {
                    "project_name": '任务体系',
                    "path": '/firstIndex'
                }
            ],
            "user_id": 5,
            "real_name": "张三",
            "job": "系统管理员",
            "role_id": 12,
        }
        return resp


models = [Employee]
db.create_tables(models=models)

if __name__ == "__main__":
    """添加酒店"""
    # args = {
    #     "full_name": "xdfdf大酒店",
    #     "short_name": "A大酒店",
    #     "mechanism_type": 1
    # }
    # print(Hotel.add_record(**args))
    # """添加部门"""
    # args = {
    #     "name": "客房部",
    #     "hotel_id": 1,
    #     "creator": 12
    # }
    # print(Dept.add_record(**args))
    """添加职务"""
    # args = {
    #     "name": "IT管理员",
    #     "hotel_id": 1,
    #     "dept_id": 1,
    #     "creator": 12
    # }
    # print(Job.add_record(**args))
    """添加员工"""
    # args = {
    #     "user_name": "admin",
    #     "hotel_id": 1,
    #     "dept_id": 1,
    #     "job_id": 1,
    #     "role_id": 9,
    #     "creator": 12
    # }
    # print(Employee.add_record(**args))
    Employee.account_login("admin", "", 2)
    pass