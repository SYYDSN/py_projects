#  -*- coding: utf-8 -*-
import os
import sys

__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from orm_unit.peewee_orm import *

"""
组织架构模块
本模块包含的数据模型:
1. 集团  
2. 酒店
3. 部门
4. 职务
"""


class HotelGroup(BaseModel):
    """
    酒店集团
    酒店集团在组织架构上是酒店的上层组织. 酒店集团和酒店之间是1:n的关系,
    在是实务中, 集团的下级组织包含: 酒店, 各种分支/直属机构.
    """
    id = AutoField(primary_key=True)
    full_name = CharField(verbose_name="集团全称")
    short_name = CharField(verbose_name="集团简称")
    address_1 = CharField(verbose_name="集团办公地址1", max_length=500)
    address_2 = CharField(verbose_name="集团办公地址2", help_text="冗余字段,可空", max_length=500, null=True)
    audit = IntegerField(verbose_name="审核状态", help_text="是否审核过?  0代表未审核, 1代表审核过了",
                         choices=((0, "未审核"), (1, "已审核")), default=0)
    position = CharField(verbose_name="地理位置的经纬度", help_text="使用经纬度表示, 经度+空格+ 纬度的方式表示", null=True)
    city = CharField(verbose_name="城市名称", help_text="城市名称,可自由输入", max_length=128)
    code = CharField(verbose_name="代码", help_text="代表唯一记录, 一般用作快速索引", max_length=40, unique=True)
    country_code = CharField(verbose_name="国家代码", max_length=40)
    create_time = DateTimeField(verbose_name="创建时间", default=datetime.datetime.now)
    last_time = DateTimeField(verbose_name="修改时间", help_text="记录最后一次的修改时间", default=datetime.datetime.now)
    creator = IntegerField(verbose_name="创建者", help_text="创建者id")
    last_user = IntegerField(verbose_name="修改者", help_text="最后一个修改的人的id,创建的时候此id为创建者id")
    order_value = IntegerField(verbose_name="排序的值", default=0)
    desc = CharField(verbose_name="中文描述", max_length=2000, null=True)
    desc_en = CharField(verbose_name="英文描述", max_length=2000, null=True)
    dns = CharField(verbose_name="dns", max_length=40, null=True)
    email = CharField(verbose_name="email地址", null=True)
    office_tel = CharField(verbose_name="总机", max_length=40, null=True)
    reserve_tel = CharField(verbose_name="订房电话", max_length=40, null=True)
    service_tel = CharField(verbose_name="服务电话", help_text="比如400电话之类的", max_length=40, null=True)
    fax = CharField(verbose_name="传真", max_length=40, null=True)
    web_site = CharField(verbose_name="官网地址", null=True)
    logo = CharField(verbose_name="logo",
                     help_text="logo图片保存在图片数据库中(mongodb),这里保存的只是一个logo图片的id,使用的时候根据这个id向图片服务器请求图片",
                     max_length=128, null=True)
    photo = CharField(verbose_name="酒店照片",
                      help_text="酒店集团照片保存在图片数据库中(mongodb),这里保存的只是一个酒店集团照片的id,使用的时候根据这个id向图片服务器请求图片",
                      max_length=128, null=True)
    status = IntegerField(verbose_name="状态", help_text="0代表未禁用, 1代表正常", choices=((0, "已禁用"), (1, "正常")),
                          default=1)

    class Meta:
        table_name = "hotel_group"


class Hotel(BaseModel):
    """
    酒店
    酒店在组织架构上是酒店集团的下层组织. 酒店集团和酒店之间是1:n的关系.
    在是实务中, 集团的下属机构不仅仅有酒店一种类型, 也存在着其他各种分支/直属机构.这些暂时也都用本类表示.
    """
    id = AutoField(primary_key=True)
    full_name = CharField(verbose_name="酒店全称")
    short_name = CharField(verbose_name="集团简称")
    mechanism_type = IntegerField(verbose_name="机构类型", help_text="集团的下属机构不仅仅有酒店一种类型, 也存在着其他各种分支/直属机构.0,直属机构, 1酒店, 2, 分支机构",
                                  choices=[0, 1, 2], default=1)
    address_1 = CharField(verbose_name="集团办公地址1", max_length=500)
    address_2 = CharField(verbose_name="集团办公地址2", help_text="冗余字段,可空", max_length=500, null=True)
    position = CharField(verbose_name="地理位置的经纬度", help_text="使用经纬度表示, 经度+空格+ 纬度的方式表示", null=True)
    audit = IntegerField(verbose_name="审核状态", help_text="是否审核过?  0代表未审核, 1代表审核过了",
                         choices=((0, "未审核"), (1, "已审核")), default=0)
    city = CharField(verbose_name="城市名称", help_text="城市名称,可自由输入", max_length=128)
    code = CharField(verbose_name="代码", help_text="代表唯一记录, 一般用作快速索引", max_length=40, unique=True)
    country_code = CharField(verbose_name="国家代码", max_length=40)
    create_time = DateTimeField(verbose_name="创建时间", default=datetime.datetime.now)
    last_time = DateTimeField(verbose_name="修改时间", default=datetime.datetime.now)
    creator = IntegerField(verbose_name="创建者", help_text="创建者id")
    last_user = IntegerField(verbose_name="修改者", help_text="最后一个修改的人的id,创建的时候此id为创建者id")
    order_value = IntegerField(verbose_name="排序的值", default=0)
    desc = CharField(verbose_name="中文描述", max_length=2000, null=True)
    desc_en = CharField(verbose_name="英文描述", max_length=2000, null=True)
    dns = CharField(verbose_name="dns", max_length=40, null=True)
    email = CharField(verbose_name="email地址", null=True)
    office_tel = CharField(verbose_name="总机", max_length=40, null=True)
    reserve_tel = CharField(verbose_name="订房电话", max_length=40, null=True)
    service_tel = CharField(verbose_name="服务电话", help_text="比如400电话之类的", max_length=40, null=True)
    fax = CharField(verbose_name="传真", max_length=40, null=True)
    web_size = CharField(verbose_name="官网地址", null=True)
    logo = CharField(verbose_name="logo",
                     help_text="logo图片保存在图片数据库中(mongodb),这里保存的只是一个logo图片的id,使用的时候根据这个id向图片服务器请求图片",
                     max_length=128, null=True)
    photo = CharField(verbose_name="酒店照片",
                      help_text="酒店照片保存在图片数据库中(mongodb),这里保存的只是一个酒店照片的id,使用的时候根据这个id向图片服务器请求图片",
                      max_length=128, null=True)
    status = IntegerField(verbose_name="状态", help_text="0代表未禁用, 1代表正常", choices=((0, "已禁用"), (1, "正常")),
                          default=1)

    class Meta:
        table_name = "hotel"


class Dept(BaseModel):
    """
    部门信息
    部门是隶属于酒店的下级组织单位.部门之间也存在上下级关系.
    如果是集团直属的部门. 那么, 这些部门是依附于一个类似"总部"Hotel类的特例.hotel_id就指向这个实例的id.
    """
    id = AutoField(primary_key=True)
    name = CharField(verbose_name="部门名称")
    hotel_id = IntegerField(verbose_name="酒店id", help_text="部门所属酒店的id")
    parent_id = IntegerField(verbose_name="上级部门id", help_text="这是一个自引用字段, 指向Dept.id", null=True)
    creator = IntegerField(verbose_name="创建者", help_text="创建者id")
    create_time = DateTimeField(verbose_name="创建时间", default=datetime.datetime.now)
    last_user = IntegerField(verbose_name="修改者", help_text="最后一个修改的人的id,创建的时候此id为创建者id, 注意,这里的操作者是酒店内部的管理员")
    last_time = DateTimeField(verbose_name="修改时间", help_text="记录最后一次的修改时间, 注意,这里的操作者是酒店内部的管理员", default=datetime.datetime.now)

    class Meta:
        table_name = "department"


class Job(BaseModel):
    """
    职务.
    职务依附于Hotel类型存在. 常常作为员工信息的字段.
    """
    id = AutoField(primary_key=True)
    name = CharField(verbose_name="职务名称")
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
