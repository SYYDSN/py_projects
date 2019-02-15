#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from pony_orm import *


"""
组织架构模块
本模块包含的数据模型:
1. 集团  
2. 酒店
3. 部门
4. 职务
"""


class HotelGroup(db.Entity):
    """
    酒店集团
    酒店集团在组织架构上是酒店的上层组织. 酒店集团和酒店之间是1:n的关系,
    在是实务中, 集团的下级组织包含: 酒店, 各种分支/直属机构.
    """
    _table_ = "hotel_group"
    id = PrimaryKey(int, auto=True)
    full_name = Required(str, max_len=40)  # 集团全称
    short_name = Required(str, max_len=10)  # 集团简称
    address_1 = Required(str, max_len=500)  # 集团办公地址1
    address_2 = Optional(str, max_len=500)  # 集团办公地址2 冗余字段,可空
    audit = Required(int, default=0)  # 审核状态, 是否审核过?  0代表未审核, 1代表审核过了
    position = Required(str, max_len=40, nullable=True)  # 地理位置的经纬度使用经纬度表示, 经度+空格+ 纬度的方式表示
    city = Required(str, max_len=40) # 城市名称,可自由输入
    code = Required(str, max_len=20, unique=True)  # 代码, 一般用作快速索引
    country_code = Required(str, max_len=40)  # 国家代码
    order_value = Required(int,  default=0)  # 排序的值
    desc = Optional(str, max_len=2000, nullable=True)  # 中文描述
    desc_en = Optional(str, max_len=2000, nullable=True)  # 英文描述
    dns = Optional(str, max_len=40, nullable=True)  # dns
    email = Optional(str, max_len=80, nullable=True)  # email地址
    office_tel = Optional(str, max_len=40, nullable=True)  # 总机
    reserve_tel = Optional(str, max_len=40, nullable=True)  # 订房电话
    service_tel = Optional(str, max_len=40, nullable=True)  # 服务电话比如400电话之类的
    fax = Optional(str, max_len=40, nullable=True)  # 传真
    web_site = Optional(str, max_len=80, nullable=True)  # 官网地址
    """logo图片保存在图片数据库中(mongodb),这里保存的只是一个logo图片的id,使用的时候根据这个id向图片服务器请求图片"""
    logo = Optional(str, max_len=128, nullable=True)
    """酒店集团照片保存在图片数据库中(mongodb),这里保存的只是一个酒店集团照片的id,使用的时候根据这个id向图片服务器请求图片"""
    photo = Optional(str, max_len=128, nullable=True)  # 酒店照片
    status = Required(int, default=1)  # 状态, 0代表未禁用, 1代表正常

    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Optional(datetime.datetime, default=datetime.datetime.now, nullable=True)  # 最后一次的修改时间
    creator = Required("Employee", reverse="inserted_hotel_groups")  # 创建人.指向管理员id
    last_user = Required("Employee", reverse="updated_hotel_groups")  # 最后修改人.指向系统管理员id

    app_relations = Set("HGroupApp")  # 他一个集团有多个可用的app状态.
    hotels = Set("Hotel")  # 他一个集团有1到多个下属酒店或者同级机构(默认的有个集团总部)


class Hotel(db.Entity):
    """
    酒店
    酒店在组织架构上是酒店集团的下层组织. 酒店集团和酒店之间是1:n的关系.
    在是实务中, 集团的下属机构不仅仅有酒店一种类型, 也存在着其他各种分支/直属机构.这些暂时也都用本类表示.
    """
    _table_ = "hotel"
    full_name = Required(str, max_len=80)  # 酒店全称
    short_name = Optional(str, max_len=20, nullable=True)  # 集团简称
    """集团的下属机构不仅仅有酒店一种类型, 也存在着其他各种分支/直属机构(总部是最常见的).0,直属机构, 1酒店, 2, 其他分支机构"""
    mechanism_type = Required(int, default=1)  # 机构类型
    address_1 = Required(str, max_len=500)  # 集团办公地址1
    address_2 = Optional(str, max_len=500, nullable=True)  # 集团办公地址2
    position = Required(str, max_len=40, nullable=True)  # 地理位置的经纬度.使用经纬度表示, 经度+空格+ 纬度的方式表示
    audit = Required(int,  default=0)  # 审核状态是否审核过?  0代表未审核, 1代表审核过了
    city = Required(str, max_len=40)  # 城市名称,可自由输入
    code = Required(str, max_len=40, unique=True)  # 快速代码
    country_code = Optional(str,  max_len=40, nullable=True)  # 国家代码
    order_value = Required(int, default=0)  # 排序的值
    desc = Optional(str, max_len=2000, nullable=True)  # 中文描述
    desc_en = Optional(str, max_len=2000, nullable=True)  # 英文描述
    dns = Optional(str, max_len=40, nullable=True)  # dns
    email = Optional(str, max_len=60, nullable=True)  # email地址
    office_tel = Optional(str, max_len=40, nullable=True)  # 总机
    reserve_tel = Optional(str, max_len=40, nullable=True)  # 订房电话
    service_tel = Optional(str, max_len=40, nullable=True)  # 服务电话比如400电话之类的
    fax = Optional(str, max_len=40, nullable=True)  # 传真
    web_site = Optional(str, max_len=80, nullable=True)  # 官网地址
    """logo图片保存在图片数据库中(mongodb),这里保存的只是一个logo图片的id,使用的时候根据这个id向图片服务器请求图片"""
    logo = Optional(str, max_len=128, nullable=True)
    """酒店集团照片保存在图片数据库中(mongodb),这里保存的只是一个酒店集团照片的id,使用的时候根据这个id向图片服务器请求图片"""
    photo = Optional(str, max_len=128, nullable=True)  # 酒店照片
    status = Required(int, default=1)  # 状态, 0代表未禁用, 1代表正常

    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Required(datetime.datetime, default=datetime.datetime.now)  # 修改时间
    creator = Required("Employee", reverse="inserted_hotels")  # 创建人.指向管理员id
    last_user = Required("Employee", reverse="updated_hotels")  # 最后修改人.指向系统管理员id

    hotel_group_id = Required(HotelGroup)  # 上级集团id
    employees = Set("Employee")  # 酒店的员工们
    rule_groups = Set("RuleGroup")  # 酒店的权限组
    roles = Set("Role")  # 酒店的角色
    role_groups = Set("RoleGroup")  # 酒店的角色组
    depts = Set("Dept")  # 酒店下属部门


class Dept(db.Entity):
    """
    部门信息
    部门是隶属于酒店的下级组织单位.部门之间也存在上下级关系.
    如果是集团直属的部门. 那么, 这些部门是依附于一个类似"总部"Hotel类的特例.hotel_id就指向这个实例的id.
    """
    _table_ = "dept"
    id = PrimaryKey(int, auto=True)
    name = Required(str, max_len=40)  # 部门名称
    hotel_id = Required(Hotel)  # 部门所属酒店的id
    parent_id = Optional("Dept", nullable=True, reverse="parent_id")  # 上级部门id这是一个自引用字段, 指向Dept.id
    creator = Required("Employee", reverse="inserted_depts")  # 创建人.指向管理员id
    last_user = Required("Employee", reverse="updated_depts")  # 最后修改人.指向系统管理员id
    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Required(datetime.datetime, default=datetime.datetime.now)  # 修改时间

    jobs = Set("Job")  # 部门下职务信息
    employees = Set("Employee")  # 部门职员信息


class Job(db.Entity):
    """
    职务.
    职务依附于Hotel类型存在. 常常作为员工信息的字段.
    """
    _table_ = "job"
    id = PrimaryKey(int, auto=True)
    name = Required(str, max_len=40)  # 职务名称
    level = Required(int, default=0)  # "职务级别,这个用来定义职务的排序或者职权大小关系,部门内职级别最高的就是部门领导"
    dept_id = Required(Dept)  # 职务所属部门的id

    creator = Required("Employee", reverse="inserted_jobs")  # 创建人.指向管理员id
    last_user = Required("Employee", reverse="updated_jobs")  # 最后修改人.指向系统管理员id
    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Required(datetime.datetime, default=datetime.datetime.now)  # 修改时间

    employees = Set("Employee")  # 担任本岗位的员工


# db.generate_mapping(create_tables=True)


if __name__ == "__main__":
    pass
