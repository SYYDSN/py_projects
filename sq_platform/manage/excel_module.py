#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
import openpyxl
import xlrd
import re
import datetime
import time
from api.user.sms import send_download_sms


"""excel操作模块"""

ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
excel_dir = "excel"
excel_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), excel_dir)


class SpreadCustomer(mongo_db.BaseDoc):
    """推广客户"""
    _table_name = "spread_customer_info"
    type_dict = dict()
    type_dict['_id'] = mongo_db.ObjectId
    type_dict['real_name'] = str
    type_dict['phone'] = str
    type_dict['create_date'] = datetime.datetime

    def __init__(self, **kwargs):
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(SpreadCustomer, self).__init__(**kwargs)


class Spread(mongo_db.BaseDoc):
    """推广活动"""
    _table_name = "spread_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['name'] = str   # 推广活动的名称
    type_dict['description'] = str     # 推广活动内容的说明
    type_dict['create_date'] = datetime.datetime  # 推广活动的创建时间

    def __init__(self, **kwargs):
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(Spread, self).__init__(**kwargs)


class SpreadRecord(mongo_db.BaseDoc):
    """推广活动的记录"""
    _table_name = "spread_record_info"
    type_dict = dict()
    type_dict['_id'] = mongo_db.ObjectId
    type_dict['spread_id'] = DBRef  # 推广活动的id
    type_dict['customer_id'] = DBRef  # 客户的id
    type_dict['event_date'] = datetime.datetime  # 推广活动执行的的时间
    type_dict['result'] = str  # 推广活动执行的结果

    def __init__(self, **kwargs):
        if "event_date" not in kwargs:
            kwargs['event_date'] = datetime.datetime.now()
        super(SpreadRecord, self).__init__(**kwargs)

    @classmethod
    def rebuild_event_date(cls):
        """
        修复事件日期
        :return:
        """
        f = {
            "event_date": {"$exists": False}
        }
        records = cls.find_plus(filter_dict=f, to_dict=False)
        for record in records:
            _id = record.get_attr("_id")
            record.set_attr('create_date', _id.generation_time)
            record.save_plus()


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


def read_sheet_01(sh) -> dict:
    """
    读取excel文件里的工作簿，这里读取的是《2017年新振兴车辆信息》
    :param sh:
    :return:
    """
    data = dict()
    phone_index = None
    name_index = None
    max_row = sh.nrows
    flag = False
    for i in range(max_row):
        row = sh.row_values(i)
        if flag:
            name = row[name_index]
            phone = row[phone_index]
            phone = str(int(phone))if isinstance(phone, float) else str(phone)
            phone = phone.strip()
            """检查手机号码是否合法?"""
            phones = [x.strip() for x in phone.split("\n")]
            pattern = re.compile(r"1\d{10}")
            for phone in phones:
                m = re.search(pattern=pattern, string=phone)
                if m:
                    data[m.group()] = name
                else:
                    print("{} 第{}行,错误的手机号码:{}".format(sh.name, i, phone))
        elif "车主姓名" in row and "联系电话" in row:
            name_index = row.index('车主姓名')
            phone_index = row.index('联系电话')
            flag = True
        else:
            print(row)
    return data


def read_excel(file_path: str):
    """
    读excel文件。
    :param file_path:
    :return:
    """
    res = dict()
    if file_path.lower().endswith(".xlsx"):
        excel = openpyxl.load_workbook(file_path)
        sheets = excel.sheetnames
        print(sheets)
        for sheet in sheets:
            """循环处理工作簿"""
            sheet = excel.get_sheet_by_name(sheet)
            lines = read_sheet_01(sheet)
    else:
        excel = xlrd.open_workbook(file_path)
        sheets = excel.sheet_names()
        print(sheets)
        for sheet in sheets:
            """循环处理工作簿"""
            sheet = excel.sheet_by_name(sheet)
            sheet_dict = read_sheet_01(sheet)
            res.update(sheet_dict)
    return res


def batch_add_customer_from_excel():
    """
    批量从excel导入新振兴的司机的联系方式,作为推广的对象
    :return:
    """
    customer_dict = dict()
    paths = get_excel_path_list()
    for x in paths:
        customer_dict.update(read_excel(x))
    res = list()
    for phone, name in customer_dict.items():
        item = dict()
        item['real_name'] = name
        item['phone'] = phone
        item['create_date'] = datetime.datetime.now()
        res.append(item)
    SpreadCustomer.insert_many(res)


def batch_send_sms(spread: Spread, max_count: int = 50):
    """
    批量发送短信,判断是否发送的结果是:
    是否存在
    1. SpreadRecord.event_date==today
    2. SpreadRecord.spread_id == spread.get_dbref()
    3. SpreadRecord.result == "success"
    :param spread: Spread
    :param max_count: 最多发送多少条短信?
    :return:
    """
    today = datetime.datetime.today().strftime("%F")
    begin = mongo_db.get_datetime_from_str("{} 0:0:0".format(today))
    end = mongo_db.get_datetime_from_str("{} 23:59:59.999".format(today))
    spread_dbref = spread.get_dbref()
    filter_dict = {
        "spread_id": spread_dbref,
        "event_date": {"$gte": begin, "$lte": end},
        "result": "success"
    }
    records = SpreadRecord.find_plus(filter_dict=filter_dict, to_dict=True)
    ignore_customer = [record['customer_id'].id for record in records]
    customers = SpreadCustomer.find_plus(filter_dict={}, to_dict=True)
    customers = [customer for customer in customers if customer['_id'] not in ignore_customer]
    # send_download_sms("15618317376")
    count = 0
    for customer in customers:
        count += 1
        phone = customer['phone']
        res = send_download_sms(phone)
        f = {
            "customer_id": DBRef(collection=SpreadRecord.get_table_name(), database="platform_db", id=customer['_id']),
            "spread_id": spread_dbref,
            "event_date": {"$gte": begin, "$lte": end}
        }
        u = {"$set": {"result": res['message'], "event_date": datetime.datetime.now()}}
        record = SpreadRecord.find_one_and_update_plus(filter_dict=f, update_dict=u)
        print("第{}个用户,号码:{},发送结果:{}".format(count, phone, res['message']))
        if count >= max_count:
            break
        else:
            pass
        time.sleep(3)


if __name__ == "__main__":
    """批量发送"""
    spread = Spread.find_by_id(ObjectId("5ab9f0324660d34e9f4328fa"))  # 发送下载app的短信
    batch_send_sms(spread=spread, max_count=500)
    # SpreadRecord.rebuild_event_date()
    pass