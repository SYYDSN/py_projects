# -*- coding: utf-8 -*-
import os
import sys
__root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __root_path not in sys.path:
    sys.path.append(__root_path)
import orm_module
import json
import zipfile
import datetime


ObjectId = orm_module.ObjectId


"""测试文件生成.py"""


def generator_import_file():
    """生成一个导入的文件"""
    now = str(int(datetime.datetime.now().timestamp()))
    with open("100万.txt", "a", encoding="utf-8") as f:
        count = 100000000000000
        for x in range(100 * 10000):
            if x % 100000 == 0:
                print("{}万, {}".format(x / 10000, datetime.datetime.now()))
            else:
                pass
            s = now + str(count + 1)
            count += 1
            print(s, file=f)


def generator_task_sync(num: int = 10):
    """生成一个回传的文件"""
    now = str(int(datetime.datetime.now().timestamp()))
    # now = '15441752831'
    l1 = 40
    l2 = 20
    l3 = 10
    resp = list()
    json_data = ''
    file_name = "task.json"
    with open(file_name, "w", encoding="utf-8") as f:
        count = 100000000000000
        for i in range(num):
            box4 = dict()
            box4['code'] = now + str(count + 1)
            box4['level'] = 4
            children4 = []
            count += 1
            for m in range(l3):
                box3 = dict()
                box3['code'] = now + str(count + 1)
                box3['level'] = 3
                children3 = []
                count += 1
                for n in range(l2):
                    box2 = dict()
                    box2['code'] = now + str(count + 1)
                    box2['level'] = 2
                    children2 = []
                    count += 1
                    for p in range(l1):
                        children2.append(now + str(count + 1))
                        count += 1
                    box2['children'] = children2
                    children3.append(box2)
                box3['children'] = children3
                children4.append(box3)
            box4['children'] = children4
            resp.append(box4)
        json_data = json.dumps(resp)
        f.write(json_data)
        z = zipfile.ZipFile(file="task.zip", mode="w", compression=zipfile.ZIP_DEFLATED)
        z.write(filename=file_name)
        z.close()
        print("{}条记录回传数据生成完毕".format(l2 * l3 * l1 * num))


def generator_task_sync2(data: dict = None):
    """根据字典内容生成一个回传的文件"""
    data = [
        {"code": "1234", "level": 2, "children": ["3343,", "2211", "5112"]},
        {"code": "1235", "level": 2, "children": ["3344,", "2212", "5113"]},
        {"code": "1236", "level": 2, "children": ["3345,", "2213", "5114"]},
    ] if data is None else data
    json_data = ''
    file_name = "task3.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json_data = json.dumps(data)
        f.write(json_data)
        f.close()
        z = zipfile.ZipFile(file="task3.zip", mode="w", compression=zipfile.ZIP_DEFLATED)
        z.write(filename=file_name)
        z.close()



if __name__ == "__main__":
    # TempRecord.insert_mongodb()
    generator_task_sync2()
    pass