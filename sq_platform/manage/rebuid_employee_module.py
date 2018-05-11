# -*- coding:utf-8 -*-
import sys
import os
"""直接运行此脚本，避免import失败的方法"""
__project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # 项目目录
if __project_dir not in sys.path:
    sys.path.append(__project_dir)
from mongo_db import ObjectId
from mongo_db import get_obj_id
from api.data.item_module import User
from manage.company_module import Company
from manage.company_module import Employee
from manage.company_module import Dept
from manage.company_module import Post
import openpyxl


"""从数据库表格读取用户信息,再将对应的用户和公司建立关联"""


excel_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "excel")


def read_excel():
    """
    从excel读取用户信息,返回list
    return: [
    {"user_name": "张三","phone_num": "13848482925", "employee_number": 3434},
    {"user_name": "李四","phone_num": "15644525789", "employee_number: 3435},
    ...
     ]
    """
    file_path = os.path.join(excel_path, "华新中转场驾驶员使用保驾犬明细_2018_5_9.xlsx")
    excel = openpyxl.load_workbook(file_path)
    sheets = excel.sheetnames
    users = list()
    for sheet in sheets:
        sheet = excel.get_sheet_by_name(sheet)
        lines = list()
        for tr in sheet:
            first = tr[0].value
            if first is not None and (isinstance(first, int) or first.isdigit()):
                line = dict()
                line['employee_number'] = str(tr[1].value)
                line['real_name'] = tr[2].value
                line['phone_num'] = str(tr[3].value)
                line['line'] = tr[4].value
                lines.append(line)
        users.extend(lines)
    return users


def rebuild() -> None:
    """
    重建关系员工和公司
    :return:
    """
    us = read_excel()
    p_map = {x['phone_num']: {
        "real_name": x['real_name'],
        "employee_number": x['employee_number'],
        "line": x['line'],
    } for x in us}
    phones = list(p_map.keys())
    f = {"phone_num": {"$in": phones}}
    users = User.find_plus(filter_dict=f, to_dict=False)
    ids = list()
    for e in users:
        phone = e.get_attr('phone_num')
        temp = p_map[phone]
        e.set_attr('real_name', temp['real_name'])
        e.set_attr('employee_number', temp['employee_number'])
        e.set_attr('line', temp['line'])
        r = e.save_plus()
        if r is None:
            print("保存失败")
        else:
            ids.append(r)
    company_id = get_obj_id("59a671a0de713e3db34de8bf")  # 顺丰公司
    dept_id = get_obj_id("5abcac4b4660d3599207fe18")  # 顺丰华新分部
    post_id = get_obj_id("59a67348de713e3f43dcf0d7")  # 司机岗位
    Company.rebuild_relation(company_id=company_id, dept_id=dept_id, post_id=post_id, employee_list=ids)


if __name__ == "__main__":
    """修复顺丰员工和企业的关系"""
    rebuild()
    pass
