#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from orm_unit.sql_module import *
from authorization_package.organization import *
from authorization_package.permission_module import *
import logging


logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


"""用户模块"""


class Employee(BaseModel):
    """
    企业内部的员工,
    由于员工的登录比较频繁.所以有专门的表记录员工的登录和操作.
    """
    id = AutoField(primary_key=True)
    user_name = CharField(max_length=64, help_text="用户名,用来登录")
    password = CharField(max_length=128, help_text="密码.md5")
    face_id = CharField(max_length=128, null=True, help_text="面部识别的id,暂空")
    user_card_id = CharField(max_length=128, null=True, help_text="用户卡id,预留给员工卡登录,暂空")

    employee_id = CharField(max_length=128, null=True, help_text="工号, 可以用来做唯一性判定")
    work_start = DateField(formats='%Y-%m-%d', null=True, help_text="参加工作日期")
    entry_date = DateField(formats='%Y-%m-%d', null=True, help_text="入职时间")
    work_status = IntegerField(choices=(1, 0), default=1, help_text="在职状态,1在职,0离职.")
    # hotel_group_id = ForeignKeyField(model=HotelGroup, column_name="hotel_group_id", backref="employee")
    hotel_id = ForeignKeyField(model=Hotel, column_name="hotel_id", backref="employee")
    dept_id = ForeignKeyField(model=Dept, column_name="Dept_id", backref="employee")
    # job_id = ForeignKeyField(model=Job, column_name="job_id", backref="employee")
    job_id = IntegerField(column_name="job_id", help_text="职务id")
    role_id = ForeignKeyField(model=UserRole, column_name="role_id", backref="employee")

    head_image = CharField(max_length=128, help_text="头像图片的id,文件名或者唯一地址")
    real_name = CharField(max_length=128, help_text="真实姓名, 可以登记英文或者中文")
    real_name_en = CharField(max_length=128, help_text="真实姓名, 可以登记英文或者中文")
    nick_name = CharField(max_length=128, help_text="昵称", default='')
    gender = CharField(choices=("男", "女"), verbose_name="gender", help_text="性别, 中文的男女即可")
    birth_date = DateField(formats='%Y-%m-%d', null=True, help_text="出生年月")
    blood_type = CharField(choices=("A", "B", "O", "AB", "其他", "未知"), help_text="血型")
    degree = CharField(choices=("小学及以下", "初中", "高中/技校", "大专", "本科及以上", "未知"), help_text="学历")
    phone = CharField(max_length=128, help_text="手机号码, 和work_status, hotel_group_id联合做唯一判定")
    homeland = CharField(max_length=128, help_text="祖籍")
    birth_place = CharField(null=True, help_text="出生地")
    domicile_place = CharField(max_length=128, help_text="户口所在地")
    live_place = CharField(max_length=128, help_text="现在居住地")
    address = CharField(max_length=128, help_text="居住地址")
    political_status = CharField(choices=("无", "共青团员", "共产党员", "其他"), help_text="政治面貌")
    email = CharField(max_length=128, null=True, help_text="电子邮件")
    wx_code = CharField(max_length=128, null=True, help_text="微信号")
    open_id = CharField(max_length=128, null=True, help_text="微信open_id")
    union_id = CharField(max_length=128, null=True, help_text="微信union_id")
    qq = CharField(max_length=128, null=True, help_text="qq号码")
    weibo = CharField(max_length=128, null=True, help_text="新浪微博")

    status = IntegerField(choices=(1, 0), default=1, help_text="账户状态,1正常,0停用.")
    creator = IntegerField(verbose_name="创建者", help_text="创建者id")
    create_time = DateTimeField(verbose_name="创建时间", default=datetime.datetime.now)
    last_user = IntegerField(verbose_name="修改者", help_text="最后一个修改的人的id,创建的时候此id为创建者id, 注意,这里的操作者是酒店内部的管理员")
    last_time = DateTimeField(verbose_name="修改时间", help_text="记录最后一次的修改时间, 注意,这里的操作者是酒店内部的管理员",
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