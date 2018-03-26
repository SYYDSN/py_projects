#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import openpyxl


"""excel操作模块"""


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
    读取excel文件里的工作簿，这里读取的是《2017年新振兴车辆信息》
    :param sh:
    :return:
    """
    for i, tr in enumerate(sh):
        if i == 0:
            pass
        else:
            chinese = tr[0].value
            english = tr[0].value


def read_excel(file_path: str):
    """
    读excel文件。
    :param file_path:
    :return:
    """
    excel = openpyxl.load_workbook(file_path)
    sheets = excel.sheetnames
    print(sheets)
    for sheet in sheets:
        sheet = excel.get_sheet_by_name(sheet)
        lines = read_sheet_01(sheet)


if __name__ == "__main__":
    paths = get_excel_path_list()
    for x in paths:
        read_excel(x)