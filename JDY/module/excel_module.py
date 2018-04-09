#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import datetime
import openpyxl



"""excel操作模块，用于导入数据"""


excel_dir = "excel"
excel_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), excel_dir)


def get_excel_path_list(dir_path: str = None) -> list:
    """
    根据目录获取excel文件的列表
    :param dir_path:
    :return:
    """
    if dir_path is None:
        dir_path = excel_path
    r = list()
    for name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, name)
        if os.path.isfile(file_path) and (name.lower().endswith("xls") or name.lower().endswith("xlsx")):
            r.append(file_path)
        else:
            pass
    return r


def read_sheet_01(sh) -> list:
    """
    读取excel文件里的工作簿，这里代码要根据读取的文件不同自行该比那
    :param sh:
    :return:
    """
    res = list()
    now = datetime.datetime.now()
    for i, tr in enumerate(sh):
        if i == 0:
            pass
        else:
            p = tr[6].value
            if p == '盛汇中国':
                p = 'shengfxchina'
            elif p == 'fx888':
                p = 'shengfx888'
            elif p == 'fx china':
                p = 'shengfxchina'
            else:
                pass
            init = {
                "customer_name": tr[3].value,
                "mt4_account": tr[5].value,
                "platform": p,
                "sales_name": tr[7].value,
                "manager_name": tr[8].value,
                "director_name": tr[9].value,
                "create_date": now
            }
            res.append(init)
    return res


def read_excel(file_path: str):
    """
    读excel文件。
    :param file_path:
    :return:
    """
    excel = openpyxl.load_workbook(file_path)
    sheets = excel.sheetnames
    res = list()
    for sheet in sheets:
        sheet = excel.get_sheet_by_name(sheet)
        lines = read_sheet_01(sheet)
        res.extend(lines)
    return res


if __name__ == "__main__":
    pass