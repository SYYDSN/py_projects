#  -*- coding: utf-8 -*-
import os
import sys

__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import logging
from org_emp.organization import *
from pony_orm import *

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

"""
app, 用户, 权限

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


class App(db.Entity):
    """
    app模块的原始信息(全集)
    app是带有层级关系的树状结构.
    0级别或者has_entry=1的页面是有自己入口的apps
    1级别,一般来说是主导航. 逻辑中叫模块
    2级别和以下的,可能是二级导航(逻辑中叫子模块)或者操作.

    app和原始rule有映射关系.
    app的url和原始rule的url的path的开始部分不一定一致.
    """
    _table_ = "app"
    name = Required(str, max_len=128)  # 模块名
    url = Required(str, max_len=128)
    layer = Required(int, default=0)  # 模块的层级,0是顶层的.
    has_entry = Required(int, sql_default=0)  # 是否有自己的登录入口?
    name_en = Optional(str, max_len=128)  # 模块英文名
    desc = Optional(str, max_len=1000, nullable=True)  # 备注
    desc_en = Optional(str, max_len=1000, nullable=True)  # 英文 备注

    creator = Required("Employee", reverse="inserted_apps")  # 创建人.指向管理员id
    last_user = Required("Employee", reverse="updated_apps")  # 最后修改人.指向系统管理员id
    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Required(datetime.datetime, default=datetime.datetime.now)  # 最后一次修改时间

    root_id = Optional("App", nullable=True)  # 根app的id,
    children_ids = Set("App")  # 所有后代的app的id
    parent_id = Optional("App", nullable=True, reverse="parent_id")  # 上一级app的id, 为0表示自己是顶层元素
    hotel_group_relations = Set("HGroupApp")  # 一个app记录有多条关系记录
    rule_relations = Set("AppRuleRelation")  # app直接对应的AppRuleRelation的记录


class HGroupApp(db.Entity):
    """
    集团和app之间的关系,一个集团用户对应了一组app记录
    """
    _table_ = "hotel_group_app_relation"
    hotel_group_id = Required(HotelGroup)
    app_id = Required(App)
    creator = Required("Employee")  # 创建者
    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间


class Rule(db.Entity):
    """
    (业务接口的)权限, 这是权限规则规则的原始记录
    权限规则和api视图路由是1:1的关系,
    权限规则和app的关系是n:n
    """
    _table_ = "rule"
    url = Required(str, max_len=191, unique=True)  # 接口的url地址,不包含host,port和参数的全路径接口path,唯一
    name = Required(str, max_len=128, unique=True)  # 接口/规则的名字.唯一
    name_en = Required(str, max_len=128, unique=True)  # 接口/规则的英文名字.唯一
    desc = Optional(str, max_len=1000, nullable=True)  # '描述.本接口是干什么的?
    desc_cn = Optional(str, max_len=1000, nullable=True)  # 英文描述.本接口是干什么的?
    level = Required(int, default=1)  # 权限的级别,0是系统管理员才能设定的选先,1是集团管理员可设定的, 2 是酒店管理员可设定的")
    status = Required(int, default=1)  # 是否可用,默认是可用.0的话就不能被选择加入权限组了.

    last_user = Required("Employee", reverse="updated_rules")  # 最后修改人.指向系统管理员id
    last_time = Required(datetime.datetime, default=datetime.datetime.now)  # 最后一次修改时间

    app_relation = Set("AppRuleRelation")  # rule直接对应的AppRuleRelation的记录
    role_rule_mapping = Set("RoleRuleMapping", reverse="rule_id")  # 角色表中和本权限有关的mapping的记录.
    rule_group_id = Optional("RuleGroup", nullable=True)  # 权限组id
    employee_rule_mapping = Set("EmployeeRuleMapping", reverse="rule_id")  # 用户权限映射中,和本权限相关的记录


class RuleGroup(db.Entity):
    """
    权限组, 权限的集合.辅助类.用于吧权限分组.便于快速选择一组相关连的权限.
    """
    _table_ = "rule_group"
    name = Required(str, max_len=40)  # 权限组名称

    creator = Required("Employee", reverse="inserted_rule_groups")  # 创建人.指向管理员id
    last_user = Required("Employee", reverse="updated_rule_groups")  # 最后修改人.指向系统管理员id
    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Required(datetime.datetime, default=datetime.datetime.now)  # 最后一次修改时间

    rules = Set(Rule)  # 权限组下的权限.
    hotel_id = Required(Hotel, reverse="rule_groups")  # 酒店id


class AppRuleRelation(db.Entity):
    """
    app和Rule之间的对应记录,注意,这里记录的是所有可以用来设置权限的
    app和rule之间的映射
    """
    _table_ = "app_rule_relation"
    app_id = Required(App, column="app_id", reverse="rule_relations")  # app的id
    rule_id = Required(Rule, column="rule_id", reverse="app_relation")  # rule的id

    creator = Required("Employee")  # 创建者
    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间


class RoleGroup(db.Entity):
    """
    角色组
    """
    _table_ = "role_group"
    name = Required(str, max_len=40)  # 角色组名
    desc = Required(str, max_len=1000)  # 中文备注
    desc_en = Optional(str, max_len=1000, nullable=True)  # 英文备注
    hotel_id = Required(Hotel)  # 酒店id

    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Optional(datetime.datetime, default=datetime.datetime.now, nullable=True)  # 最后一次的修改时间
    creator = Required("Employee", reverse="inserted_role_groups")  # 创建人
    last_user = Required("Employee", reverse="updated_role_groups")  # 最后修改人.

    roles = Set("Role")  # 角色组下面的角色


class Role(db.Entity):
    """
    角色
    """
    _table_ = "role"
    name = Required(str, max_len=40)  # 角色名
    desc = Required(str, max_len=1000)  # 中文备注
    desc_en = Optional(str, max_len=1000, nullable=True)  # 英文备注

    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Optional(datetime.datetime, default=datetime.datetime.now, nullable=True)  # 最后一次的修改时间
    creator = Required("Employee", reverse="inserted_roles")  # 创建人
    last_user = Required("Employee", reverse="updated_roles")  # 最后修改人.

    hotel_id = Required(Hotel, reverse="roles")  # 酒店id
    role_group_id = Required(RoleGroup, reverse="roles")  # 酒店id
    role_rule_mapping = Set("RoleRuleMapping", reverse="role_id")  # 角色和选择的权限的映射id


class RoleRuleMapping(db.Entity):
    """
    角色权限映射. 这里保存的是角色和权限之间的映射关系
    """
    _table_ = "role_rule_mapping"

    creator = Required("Employee")  # 创建者
    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间

    rule_id = Required(Rule, reverse="role_rule_mapping")  # 规则id
    role_id = Required(Role, reverse="role_rule_mapping")  # 角色id


class EmployeeRuleMapping(db.Entity):
    """
    用户权限映射. 这里保存的是用户和权限之间的映射关系
    """
    _table_ = "employee_rule_mapping"

    creator = Required("Employee")  # 创建者
    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间

    rule_id = Required(Rule, index=True, reverse="employee_rule_mapping")  # 用户对应
    employee_id = Required("Employee", index=True, reverse="employee_rule_mapping")  # 用户id


class Employee(db.Entity):
    """
    用户表,包含
    1. 内控超管
    2. 集团酒店内部的管理员和一般员工
    """
    _table_ = "employee"
    user_name = Required(str, max_len=64)  # 用户名,用来登录.和酒店id构成联合唯一索引
    password = Required(str, max_len=128)  # 密码.md5
    face_id = Optional(str, max_len=128, nullable=True)  # 面部识别的id,暂时是假的
    user_card_id = Optional(str, max_len=128, nullable=True)  # 用户卡id,预留给员工卡登录,暂空
    work_id = Optional(str, max_len=128, nullable=True)  # 工号, 可以用来做唯一性判定
    work_start = Optional(datetime.datetime, nullable=True)  # 参加工作日期
    entry_date = Optional(datetime.datetime, nullable=True)  # 入职时间
    work_status = Required(int, default=1)  # 在职状态,1在职,0离职
    dept_id = Optional(Dept, nullable=True, reverse="employees")  # 部门id
    job_id = Optional(Job, nullable=True, column="employees")  # 职务id
    head_image = Required(str, max_len=128)  # 头像图片的id,文件名或者唯一地址
    real_name = Required(str, max_len=128)  # 真实姓名, 可以登记英文或者中文")
    real_name_en = Required(str, max_len=128)  # 真实姓名, 可以登记英文或者中文
    nick_name = Required(str, max_len=128)  # 昵称", default='')
    gender = Required(str, max_len=10)  # 性别, 中文的男女即可
    birth_date = Optional(datetime.datetime, nullable=True)  # 出生年月
    blood_type = Optional(str, nullable=True)  # 血型, 可选"A", "B", "O", "AB", "其他", "
    degree = Optional(str, nullable=True)  # 学历小学及以下", "初中", "高中/技校", "大专", "本科及以上", "
    phone = Required(str, max_len=40)  # 手机号码, 和work_status, hotel_group_id联合做唯一判定")
    homeland = Required(str, max_len=128)  # 祖籍")
    birth_place = Required(str, nullable=True)  # 出生地")
    domicile_place = Required(str, max_len=128)  # 户口所在地")
    live_place = Required(str, max_len=128)  # 现在居住地")
    address = Required(str, max_len=128)  # 居住地址")
    political_status = Required(str, max_len=40, default="其他")  # 政治面貌"无", "共青团员", "共产党员", "其他"
    email = Required(str, max_len=128, nullable=True)  # 电子邮件")
    wx_code = Required(str, max_len=128, nullable=True)  # 微信号")
    open_id = Required(str, max_len=128, nullable=True)  # 微信open_id")
    union_id = Required(str, max_len=128, nullable=True)  # 微信union_id")
    qq = Required(str, max_len=128, nullable=True)  # qq号码")
    weibo = Required(str, max_len=128, nullable=True)  # 新浪微博")

    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Optional(datetime.datetime, default=datetime.datetime.now, nullable=True)  # 最后一次的修改时间
    creator = Optional("Employee", reverse="inserted_employees")  # 创建人
    last_user = Optional("Employee", reverse="updated_employees")  # 最后修改人

    hotel_group_id = Optional(HotelGroup)  # 集团id
    hotel_id = Optional(Hotel)  # 酒店id
    composite_key(hotel_id, user_name)  # 复合键, 酒店下用户名唯一
    composite_key(hotel_id, phone, work_status)  # 复合键, 酒店下在职人员时间手机号码唯一
    inserted_hotel_groups = Set(HotelGroup, reverse="creator")  # 用户插入的酒店集团的id的list
    updated_hotel_groups = Set(HotelGroup, reverse="last_user")  # 用户修改的酒店集团的id的list
    inserted_hotels = Set(Hotel, reverse="creator")  # 用户插入的酒店的id的list
    updated_hotels = Set(Hotel, reverse="last_user")  # 用户修改的酒店的id的list
    inserted_depts = Set(Dept, reverse="creator")  # 用户插入的部门的id的list
    updated_depts = Set(Dept, reverse="last_user")  # 用户修改的部门的id的list
    inserted_jobs = Set(Job, reverse="creator")  # 用户插入的job的id的list
    updated_jobs = Set(Job, reverse="last_user")  # 用户修改的job的id的list
    inserted_apps = Set(App, reverse="creator")  # 用户插入的app的id的list
    updated_apps = Set(App, reverse="last_user")  # 用户修改的app的id的list
    inserted_hga = Set(HGroupApp, reverse="creator")  # 用户插入的HGroupApp的id的list
    updated_rules = Set(Rule, reverse="last_user")  # 用户修改的Rule的id的list
    inserted_rule_groups = Set(RuleGroup, reverse="creator")  # 用户插入的RuleGroup的id的list
    updated_rule_groups = Set(RuleGroup, reverse="last_user")  # 用户修改的RuleGroup的id的list
    inserted_roles = Set(Role, reverse="creator")  # 用户插入的Role的id的list
    updated_roles = Set(Role, reverse="last_user")  # 用户修改的Role的id的list
    inserted_role_groups = Set(RoleGroup, reverse="creator")  # 用户插入的RoleGroup的id的list
    updated_role_groups = Set(RoleGroup, reverse="last_user")  # 用户修改的RoleGroup的id的list
    inserted_arrs = Set(AppRuleRelation, reverse="creator")  # 用户插入的AppRuleRelation的id的list
    inserted_rrms = Set(RoleRuleMapping, reverse="creator")  # 用户插入的RoleRuleMapping的id的list
    inserted_erms = Set(EmployeeRuleMapping, reverse="creator")  # 用户插入的EmployeeRuleMapping的id的list
    inserted_employees = Set("Employee", reverse="creator")  # 用户插入的Employee的id的list
    updated_employees = Set("Employee", reverse="last_user")  # 用户修改的Employee的id的list
    employee_rule_mapping = Set(EmployeeRuleMapping, reverse="employee_id")  # 和本用户相关的所有用户权限映射的记录

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


db.generate_mapping(create_tables=True)

if __name__ == "__main__":
    init = {
        "full_name": "ddfdf",
        "short_name": "ddfdf",
        "address_1": "sddddddddddddddddddsd号",
        "audit": 1,
        "position": "21,121",
        "city": "上海",
        "code": "fc12b",
        "country_code": "0086",
        "order_value": 1,
        "status": 1,
        "creator": 5,
        "last_user": 5
    }
    HotelGroup.add_one(**init)
    pass
