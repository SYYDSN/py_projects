#  -*- coding: utf-8 -*-
import os
import sys
"""直接运行此脚本，避免import失败的方法"""
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))  # 项目目录
if project_dir not in sys.path:
    print(project_dir)
    sys.path.append(project_dir)
from manage import company_module
from mongo_db import ObjectId, MyDBRef


"""这是一个存放函数/方法名称和函数/方法对应关系的文件,为role_module模块服务"""


def get_func(func_name: str):
    """
    根据权限提供的函数名,返回对应的函数体
    :param func_name:
    :return:
    """
    func_map = {
        "create_dept": company_module.DBRef()
    }


def create_dept(admin_id: ObjectId, company_id: ObjectId) -> dict:
    """
    创建部门
    :param admin_id:  管理员id
    :param company_id: 公司id
    :return:
    """
    message = {"message": "success"}
    if isinstance(admin_id, ObjectId) and isinstance(company_id, ObjectId):
        admin_dbref = MyDBRef(collection=company_module.CompanyAdmin.get_table_name(), database="platform_db",
                           id=admin_id) if isinstance(admin_id, ObjectId) else admin_id
        filter_dict = {"admin": admin_dbref, "_id": company_id}

    else:
        message['message'] = "参数错误"
    return message