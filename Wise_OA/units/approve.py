#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from units.peewee_sql import *
from peewee import *
from units.permission import Role
import datetime


"""
批准流程模块
"""


class ApproveFlowStep(BaseModel):
    """
    审批流步骤(审批流中的每一步)
    """
    id = PrimaryKeyField()
    flow_id = IntegerField()                 # 对应的ApproveFlow的id
    step_number = IntegerField()  # 审批步骤的序号,从1开始
    step_name = CharField()  # 审批步骤的名称
    role_id = ForeignKeyField(model=Role, backref="approve_step")  # 执行本步骤审核的权限组的id

    class Meta:
        table_name = "approve_flow_step"


class ApproveFlow(BaseModel):
    """
    审批流程
    """

    id = PrimaryKeyField()
    flow_name = CharField(unique=True)  # 审批流的名称
    table_name = CharField()            # 审批流对应的表的名称
    create_time = DateTimeField(default=datetime.datetime.now)  # 创建时间

    class Meta:
        table_name = "approve_flow"


class ApproveRecordStep(BaseModel):
    """
    审批记录中的步骤(审批记录中的每一步)
    """
    id = PrimaryKeyField()
    record_id = IntegerField()  # 对应的ApproveRecord的id
    user_id = IntegerField(null=True)        # 审核人员的id
    approve_time = DateTimeField(null=True)  # 审核时间.
    status = IntegerField(default=0)  # 状态, 0 为待审核, -1, 是驳回.1 是审核通过
    desc = CharField(max_length=8000, default="")             # 审批的备注
    step_number = IntegerField()  # 审批记录步骤的序号,审批记录创建时生成,生成后不可修改,从1开始
    step_name = CharField()  # 审批记录步骤的名称,审批记录创建时生成,生成后不可修改,
    role_id = ForeignKeyField(model=Role, backref="approve_step")  # 执行本步骤审核的权限组的id

    class Meta:
        table_name = "approve_record_step"


class ApproveRecord(BaseModel):
    """
    审批记录,用于记录每一个审批过程.审批记录的id会被作为外键被需要审批文档流本身所引用.
    一个审批记录及其内部的流程在审批文档提交时从审批文档对应的ApproveFlow中生成(拷贝一份).
    """

    id = PrimaryKeyField()
    status = IntegerField(default=0)  # 状态, 0 为审核中, -1, 是驳回.1 是完成(待审核文档提交后才会有审核记录)
    create_time = DateTimeField(default=datetime.datetime.now)  # 创建时间
    complete_time = DateTimeField(null=True, default=datetime.datetime.now)  # 完成时间,可能为空

    class Meta:
        table_name = "approve_record"


models = [
    ApproveFlowStep, ApproveFlow, ApproveRecord, ApproveRecordStep
]
db.create_tables(models=models)


if __name__ == "__main__":
    pass
