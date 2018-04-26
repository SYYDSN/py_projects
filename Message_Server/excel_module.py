#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import datetime
from item_module import Signal
from mongo_db import get_datetime_from_str
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
            tt = tr[0].value
            t = tr[10].value
            init = {
                "op": "data_update",
                "datetime": tt,
                "create_time": tt,
                "update_time": tt,
                "product": tr[1].value,
                "the_type": tr[2].value,
                "direction": tr[3].value,
                "enter_price": tr[4].value,
                "exit_price": tr[5].value,
                "profit": tr[6].value,
                "each_profit_dollar": tr[7].value,
                "each_profit": tr[8].value,
                "each_cost": tr[9].value,
                "creator_name": t,
                "updater_name": t,
                "from": "excel"
            }
            if tr[8].value != "徐立杰":
                res.append(init)
    f = {"creator_name": {"$ne": "徐立杰"}}
    s = {'receive_time': 1}
    insert = list()
    al = Signal.find_one_plus(filter_dict=f, sort_dict=s, instance=False)
    if isinstance(al, dict):
        last = get_datetime_from_str(al['datetime'])
        for x in res:
            create_time = x['create_time']
            if create_time < last:
                insert.append(x)
    else:
        insert = res
    print(len(insert))
    conn = Signal.get_collection()
    conn.insert_many(insert)
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
    for p in get_excel_path_list():
        read_excel(p)
    pass