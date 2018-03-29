#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from manage.company_module import Employee
import mongo_db
import datetime
from pandas import Series
from pandas import DataFrame
from api.data.item_module import GPS
from api.data.item_module import EventRecord
import pandas as pd
import pickle


"""分析模块"""

dir_path = os.path.dirname(os.path.realpath(__file__))
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


def get_user_data(filter_dict: dict = None):
    """
    获取用户的注册信息,用于数据分析
    :param filter_dict:
    :return:
    """
    if filter_dict is None:
        filter_dict = {'create_date': {"$gte": mongo_db.get_datetime_from_str("2018-3-20 0:0:0")}}
    users = Employee.find_plus(filter_dict=filter_dict, to_dict=True)
    objs = list()
    for user in users:
        obj = Series(user)
        objs.append(obj)
    frame = DataFrame(data=objs, index=range(len(objs)))
    return frame


def simple_query(begin, end):
    filter_dict = {'create_date': {
        "$gte": mongo_db.get_datetime_from_str("{} 0:0:0".format(begin)),
        "$lte": mongo_db.get_datetime_from_str("{} 23:59:59.999".format(end))
        },
        "description": {"$exists": False}
    }
    es = Employee.find_plus(filter_dict=filter_dict, to_dict=False)
    print("总共的注册人数:{}".format(len(es)))
    for e in es:
        print(e.get_attr("phone_num"), e.get_attr("create_date"))
    dbrefs = [e.get_dbref() for e in es]
    f = {
        "user_id": {"$in": dbrefs},
        "time": {
        "$gte": mongo_db.get_datetime_from_str("{} 0:0:0".format(begin)),
        "$lte": mongo_db.get_datetime_from_str("{} 23:59:59.999".format(end)),
        }
    }
    r = GPS.find_plus(filter_dict=f, to_dict=True)
    print(len(r))
    l2 = list(set([x['user_id'].id for x in r]))
    l1 = list(set([x.get_attr("_id") for x in es]))
    for x in l2:
        if x in l1:
            l2.remove(x)
            l1.remove(x)
    f = {"_id": {"$in": l2}}
    # 注册没登录的
    r_2 = Employee.find_plus(f, to_dict=True)
    phone2 = [x['phone_num'] for x in r_2]
    f = {"_id": {"$in": l1}}
    # 活跃的用户
    r_1 = Employee.find_plus(f, to_dict=True)
    phone1 = [x['phone_num'] for x in r_1]
    print(phone2)
    print(phone1)


def backup():
    begin = "2018-03-26"
    end = datetime.datetime.today().strftime("%F")
    filter_dict = {'create_date': {
        "$gte": mongo_db.get_datetime_from_str("{} 0:0:0".format(begin)),
        "$lte": mongo_db.get_datetime_from_str("{} 23:59:59.999".format(end))
    },
        "description": {"$exists": False}
    }
    es = Employee.find_plus(filter_dict=filter_dict, can_json=True)
    # es = EventRecord.find_plus(filter_dict={})
    print("总共的注册人数:{}".format(len(es)))
    file_path = os.path.join(dir_path, "h5", "{}.apk".format(datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")))
    f = open(file_path, 'wb')
    pickle.dump(es, f)
    f.flush()
    f.close()


def read_h5(file_name: str = None):
    parent_path = os.path.join(dir_path, "h5")
    names = os.listdir(parent_path)
    names = [x for x in names if os.path.isfile(os.path.join(parent_path, x))]
    names.sort(key=lambda obj: datetime.datetime.strptime(obj.split(".")[0], '%Y-%m-%d %H_%M_%S'), reverse=True)
    # for name in names:
    #     file_path = os.path.join(parent_path, name)
    #     print(file_path)
    file_path = os.path.join(parent_path, names[0])
    print(file_path)
    f = open(file_path, "rb")
    data = pickle.load(f)
    print(len(data))
    for x in data:
        print(x['create_date'], x['phone_num'], x['_id'])


def find_gps(lat: float = None, lon: float = None):
    d = {"latitude": 31.285110405816, "121.122932671441": 121.122932671441}


    f = {"time":
        {
            "$gte": mongo_db.get_datetime_from_str("2018-3-28 17:00:0"),
            "$lte": mongo_db.get_datetime_from_str("2018-3-29 02:59:59.999")
        }
         }
    g = GPS.find_plus(filter_dict=f, to_dict=True)
    g.sort(key=lambda obj: obj['time'], reverse=False)
    count = 0
    flag = False
    for x in g:
        if str(x['latitude']) == "31.296568196614583":
            flag = True
        else:
            pass
        if flag:
            count += 1
            l = x['loc']['coordinates']
            print("时间: {}, 坐标: lat={},lon={}".format(x['time'].strftime("%Y-%m-%d %H:%M:%S"), l[1], l[0]))
        if count >= 7:
            break


if __name__ == "__main__":
    # res = get_user_data()
    # print(res)
    # backup()
    read_h5()
    # find_gps()
    pass