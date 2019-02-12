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
    create_time = Required(datetime.datetime, default=datetime.datetime.now)  # 创建时间
    last_time = Optional(datetime.datetime, default=datetime.datetime.now, nullable=True)  # 最后一次的修改时间
    creator = Required("Employee")  # 创建者
    last_user = Required("Employee")   # 最后一个修改的人的id
    order_value = Required(int,  default=0)  # 排序的值
    desc = Required(str, max_len=2000, default="")  # 中文描述
    desc_en = Optional(str, max_len=2000, nullable=True)  # 英文描述
    dns = Optional(str, max_len=40, nullable=True)  # dns
    email = Optional(str, max_len=80, nullable=True)  # email地址
    office_tel = Optional(str, max_len=40, nullable=True)  # 总机
    reserve_tel = Optional(str, max_len=40, nullable=True)  # 订房电话
    service_tel = Optional(str, max_len=", help_text="服务电话比如400电话之类的", max_length=40, nullable=True)
    fax = Required(str, max_len=传真", max_length=40, nullable=True)
    web_site = Required(str, max_len=官网地址", nullable=True)
    """logo图片保存在图片数据库中(mongodb),这里保存的只是一个logo图片的id,使用的时候根据这个id向图片服务器请求图片"""
    logo = Optional(str, max_len=128, nullable=True)
    photo = Required(str, max_len=酒店照片",
                      help_text="酒店集团照片保存在图片数据库中(mongodb),这里保存的只是一个酒店集团照片的id,使用的时候根据这个id向图片服务器请求图片",
                      max_length=128, nullable=True)
    status = IntegerField(verbose_name="状态", help_text="0代表未禁用, 1代表正常", choices=((0, "已禁用"), (1, "正常")),
                          default=1)

    class Meta:
        table_name = "hotel_group"


class Hotel(db.Entity):
    """
    酒店
    酒店在组织架构上是酒店集团的下层组织. 酒店集团和酒店之间是1:n的关系.
    在是实务中, 集团的下属机构不仅仅有酒店一种类型, 也存在着其他各种分支/直属机构.这些暂时也都用本类表示.
    """
    id = PrimaryKey(int, auto=True)
    full_name = Required(str, max_len=酒店全称")
    short_name = Required(str, max_len=集团简称")
    mechanism_type = IntegerField(verbose_name="机构类型", help_text="集团的下属机构不仅仅有酒店一种类型, 也存在着其他各种分支/直属机构.0,直属机构, 1酒店, 2, 分支机构",
                                  choices=[0, 1, 2], default=1)
    address_1 = Required(str, max_len=集团办公地址1", max_length=500)
    address_2 = Required(str, max_len=集团办公地址2", help_text="冗余字段,可空", max_length=500, nullable=True)
    position = Required(str, max_len=地理位置的经纬度", help_text="使用经纬度表示, 经度+空格+ 纬度的方式表示", nullable=True)
    audit = IntegerField(verbose_name="审核状态", help_text="是否审核过?  0代表未审核, 1代表审核过了",
                         choices=((0, "未审核"), (1, "已审核")), default=0)
    city = Required(str, max_len=城市名称", help_text="城市名称,可自由输入", max_length=128)
    code = Required(str, max_len=代码", help_text="代表唯一记录, 一般用作快速索引", max_length=40, unique=True)
    country_code = Required(str, max_len=国家代码", max_length=40)
    create_time = DateTimeField(verbose_name="创建时间", default=datetime.datetime.now)
    last_time = DateTimeField(verbose_name="修改时间", default=datetime.datetime.now)
    creator = IntegerField(verbose_name="创建者", help_text="创建者id")
    last_user = IntegerField(verbose_name="修改者", help_text="最后一个修改的人的id,创建的时候此id为创建者id")
    order_value = IntegerField(verbose_name="排序的值", default=0)
    desc = Required(str, max_len=中文描述", max_length=2000, nullable=True)
    desc_en = Required(str, max_len=英文描述", max_length=2000, nullable=True)
    dns = Required(str, max_len=dns", max_length=40, nullable=True)
    email = Required(str, max_len=email地址", nullable=True)
    office_tel = Required(str, max_len=总机", max_length=40, nullable=True)
    reserve_tel = Required(str, max_len=订房电话", max_length=40, nullable=True)
    service_tel = Required(str, max_len=服务电话", help_text="比如400电话之类的", max_length=40, nullable=True)
    fax = Required(str, max_len=传真", max_length=40, nullable=True)
    web_size = Required(str, max_len=官网地址", nullable=True)
    logo = Required(str, max_len=logo",
                     help_text="logo图片保存在图片数据库中(mongodb),这里保存的只是一个logo图片的id,使用的时候根据这个id向图片服务器请求图片",
                     max_length=128, nullable=True)
    photo = Required(str, max_len=酒店照片",
                      help_text="酒店照片保存在图片数据库中(mongodb),这里保存的只是一个酒店照片的id,使用的时候根据这个id向图片服务器请求图片",
                      max_length=128, nullable=True)
    status = IntegerField(verbose_name="状态", help_text="0代表未禁用, 1代表正常", choices=((0, "已禁用"), (1, "正常")),
                          default=1)

    class Meta:
        table_name = "hotel"


class Dept(db.Entity):
    """
    部门信息
    部门是隶属于酒店的下级组织单位.部门之间也存在上下级关系.
    如果是集团直属的部门. 那么, 这些部门是依附于一个类似"总部"Hotel类的特例.hotel_id就指向这个实例的id.
    """
    id = PrimaryKey(int, auto=True)
    name = Required(str, max_len=部门名称")
    hotel_id = IntegerField(verbose_name="酒店id", help_text="部门所属酒店的id")
    parent_id = IntegerField(verbose_name="上级部门id", help_text="这是一个自引用字段, 指向Dept.id", nullable=True)
    creator = IntegerField(verbose_name="创建者", help_text="创建者id")
    create_time = DateTimeField(verbose_name="创建时间", default=datetime.datetime.now)
    last_user = IntegerField(verbose_name="修改者", help_text="最后一个修改的人的id,创建的时候此id为创建者id, 注意,这里的操作者是酒店内部的管理员")
    last_time = DateTimeField(verbose_name="修改时间", help_text="记录最后一次的修改时间, 注意,这里的操作者是酒店内部的管理员", default=datetime.datetime.now)

    class Meta:
        table_name = "department"


class Job(db.Entity):
    """
    职务.
    职务依附于Hotel类型存在. 常常作为员工信息的字段.
    """
    id = PrimaryKey(int, auto=True)
    name = Required(str, max_len=职务名称")
    level = IntegerField(verbose_name="职务级别", help_text="这个用来定义职务的排序或者职权大小关系,部门内职级别最高的就是部门领导", default=0)
    hotel_id = IntegerField(verbose_name="酒店id", help_text="职务所属酒店的id")
    dept_id = IntegerField(verbose_name="酒店id", help_text="职务所属部门的id")
    creator = IntegerField(verbose_name="创建者", help_text="创建者id")
    create_time = DateTimeField(verbose_name="创建时间", default=datetime.datetime.now)
    last_user = IntegerField(verbose_name="修改者", help_text="最后一个修改的人的id,创建的时候此id为创建者id, 注意,这里的操作者是酒店内部的管理员")
    last_time = DateTimeField(verbose_name="修改时间", help_text="记录最后一次的修改时间, 注意,这里的操作者是酒店内部的管理员",
                                default=datetime.datetime.now)

    class Meta:
        table_name = "job"


models = [Job, Dept, Hotel, HotelGroup]
db.create_tables(models=models)



if __name__ == "__main__":
    Job.add_record
    pass
