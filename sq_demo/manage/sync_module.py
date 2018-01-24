# -*- coding:utf-8 -*-
import os
import sys
project_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))  # 项目目录
if project_dir not in sys.path:
    sys.path.append(project_dir)
import mongo_db
import datetime
import random
import time
import threading
from api.data import item_module
import pickle
import requests
from amap_module import scale_mileage
from log_module import recode


GPS_DICT = dict()
REPORT_DICT = dict()
load_lock = threading.RLock()
recalculate_lock = threading.RLock()


"""取固定的3天的gps数据,保存到本地,用于模拟实时的数据传输"""


ObjectId = mongo_db.ObjectId
user_ids = [
    ObjectId("59cda57bad01be0912b352da"),
    ObjectId("59cda964ad01be237680e29d"),
    ObjectId("59cda886ad01be237680e28e")
]                                            # 用户id
names = dict(zip(user_ids, ("刘成刚", "栾新军", "薛飞")))   # 名字和id
raw_date = dict(zip(user_ids,
                    [
                     "2017-12-18",
                     "2017-12-16",
                     "2017-12-17"
                    ]))                      # 原始数据的日期
timeout_seconds_dict = dict()                # 初始化数据时,时间节点和地一个原始gps数据延时,单位秒,用于和旧的gps记录的时间做运算的
prev_gps_dict = {}                           # 存放上一次的实时gps信息
start_time = None                            # 系统的启动/上一次重启时间
restart_hours = [
     "23:00", "18:00", "13:00", "9:00", "4:00"
]                                            # 系统将在这几个时间点重置数据和安全报告的循环.具体timeout在user_timeout_dict里


def init_data() -> dict:
    data = dict()
    for user_id in user_ids:
        select_date = raw_date[user_id]
        dbref = mongo_db.DBRef(collection="user_info", id=user_id, database="platform_db")
        begin = mongo_db.get_datetime_from_str("{} 00:00:00.000".format(select_date))
        end = mongo_db.get_datetime_from_str("{} 12:00:00.000".format(select_date))
        filter_dict = {"user_id": dbref, "time": {"$lt": end, "$gte": begin}}
        sort_dict = {"time": 1}
        res = item_module.Track.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, to_dict=True)
        data[user_id] = res
    return data


def save_data() -> bool:
    """
    保存数据
    :return:
    """
    data = init_data()
    dir_path = os.path.join(project_dir, "resources", "gps")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = os.path.join(dir_path, "gps.pkl")
    f = open(file_path, "bw")
    pickle.dump(data, f)
    f.close()
    url = "http://safego:safego.org@api.safego.org:9200/sfx/daily_report/_search?&pretty&size=1000"
    r = requests.post(url=url)
    hits = r.json()['hits']['hits']
    """注意,报告字典的key是字符串不是ObjectId类型"""
    report_dict = {
        "59cda57bad01be0912b352da": [],
        "59cda964ad01be237680e29d": [],
        "59cda886ad01be237680e28e": []
    }
    [report_dict[hit['_source']['id']].append(hit['_source']) for hit in hits]
    report_dict = {k: sorted(v, key=lambda obj: mongo_db.get_datetime_from_str(obj['report_datetime']))
                   for k, v in report_dict.items()}
    file_path = os.path.join(dir_path, "report.pkl")
    f = open(file_path, "bw")
    pickle.dump(report_dict, f)
    f.close()
    return True


def load_data() -> None:
    """
    读取数据:
    如果本地没有gps和report字典文件,那就从数据库和api获取.然后保存到本地.然后再从本地文件读取.
    如果本地文件已存在,那就从本地读取.
    如果gps和report字典非空.那就直接跳过本函数.
    :return:
    """
    global load_lock
    lock = load_lock
    print(lock)
    while not lock.acquire():
        time.sleep(0.001)
    global GPS_DICT, REPORT_DICT
    if len(GPS_DICT) == 0 or len(REPORT_DICT) == 0:
        dir_path = os.path.join(project_dir, "resources", "gps")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        gps_file_path = os.path.join(dir_path, "gps.pkl")
        report_file_path = os.path.join(dir_path, "report.pkl")
        while not (os.path.isfile(gps_file_path) and os.path.isfile(report_file_path)):
            save_data()
            print("{} 从远端获取数据".format(mongo_db.get_datetime()))
        gps_file = open(gps_file_path, "rb")
        report_file = open(report_file_path, "rb")
        gps_data = pickle.load(gps_file)
        report_data = pickle.load(report_file)
        gps_file.close()
        report_file.close()
        GPS_DICT = gps_data
        REPORT_DICT = report_data
        print("数据初始化完成")
    else:
        print("数据已初始化")
    lock.release()


def calculate_timeout() -> None:
    """
    启动时,根据当前时间计算gps数据中各用户的timeout.必须是整点差.否则影响分时安全报告
    :return:
    """
    load_data()  # 计算timeout之前,必须先确认已准备好gps和report字典.
    now = datetime.datetime.now()
    now_hour = now.hour
    global timeout_seconds_dict, start_time
    for hour in restart_hours:
        the_hour = int(hour.split(":")[0])
        if now_hour >= the_hour:
            for user_id in user_ids:
                days = (now - mongo_db.get_datetime_from_str("{} 00:00:00".format(raw_date[user_id]))).days
                timeout_seconds_dict[user_id] = (days * 24 + the_hour) * 3600
            start_time = now
            break  # 终止循环
        else:
            pass
    for k, v in timeout_seconds_dict.items():
        ms = "用户{}的延时是{}秒".format(names[k], v)
        recode(ms)
        print(ms)


def need_recalculate() -> bool:
    """
    检查是否需要重新计算是检查?
    每次发送数据的时候,检测是否到了需要重新初始化数据的时间节点.此函数在运行时需要被线程互斥锁锁定
    :return:
    """
    now = datetime.datetime.now()
    now_hour = now.hour
    res = False
    global start_time
    if start_time is None:
        """第一次发送数据"""
        calculate_timeout()  # 初始化时间差
        res = True
        ms = "{}初始化时间差完成".format(now)
        recode(ms)
        print(ms)
    else:
        prev_hour = start_time.hour
        for hour in restart_hours:
            the_hour = int(hour.split(":")[0])
            # 如果当前时间的小时数大于某个重置时间而且上次重置时间小于这个重置时间
            if prev_hour < the_hour <= now_hour:
                calculate_timeout()  # 重计算时间差
                ms = "{}重计算时间差完成".format(now)
                recode(ms)
                print(ms)
                res = True
                break  # 终止循环
            else:
                pass
    return res


def find_gps_and_modify(user_id, prev_time: datetime.datetime = None, prev_index: int = 0, delay: int = 50):
    """
    根据时间差找到最早的的一个gps信息,添加必要信息并返回
    :param user_id:
    :param prev_time: 如果是第一个数据，这个参数是None，否则是上一个gps的time
    :param prev_index: 如果是第一个数据，这个参数是0，否则是上一个gps的在list中的索引
    :param delay: 两个gps数据包至少相隔的秒数.
    :return:
    """
    # 在线程锁下运行,如果没有初始化,就开始初始化,如果运行到需要重置timeout的时候,那就重置timeout.
    global recalculate_lock
    lock = recalculate_lock
    while not lock.acquire():
        time.sleep(0.000001)
    recalculate = need_recalculate()
    lock.release()
    # 释放锁
    if recalculate:
        """重置过"""
        prev_time = None
        prev_index = 0
    global GPS_DICT, timeout_seconds_dict
    gps_list = GPS_DICT[user_id]  # GPS_DICT的key是ObjectId对象.
    user_id = mongo_db.get_obj_id(user_id)
    delta = timeout_seconds_dict[user_id]
    if prev_time is None:
        """
        第一次请求
        """
        now = datetime.datetime.now()
        prev_time = now - datetime.timedelta(seconds=delta)
    resp = dict()
    for i, d in enumerate(gps_list[prev_index:]):
        # print(d)
        ms = "find_gps_and_modify func: prev_time={}, prev_index={},".format(prev_time, prev_index)
        the_time = d.get("time")
        if the_time > (prev_time + datetime.timedelta(seconds=delay)):
            resp['gps'] = d
            timeout = (d.get('time') - prev_time).total_seconds()  # 延时多久？
            timeout = abs(int(timeout))
            print("timeout: {} - {} = {}".format(d.get('time'), prev_time, timeout))
            resp['timeout'] = timeout
            resp['prev_index'] = i
            resp['prev_time'] = d.get("time")
            ms += "now_time={}, timeout={}".format(d.get("time"), timeout)
            recode(ms)
            break
        else:
            pass
    return resp


def send_gps(user_id: (str, ObjectId), func):
    """向平台发送模拟的实时gps数据"""
    prev_time = None
    prev_index = 0
    while 1:
        ms = "send_gps func: prev_index={},prev_time={},".format(prev_index, prev_time)
        print("{}: {} get gps start".format(datetime.datetime.now(), user_id))
        resp = find_gps_and_modify(user_id, prev_time)
        gps = resp['gps']
        prev_time = resp['prev_time']
        prev_index = resp['prev_index']
        ms += "curr_time={}, curr_index={}".format(prev_time, prev_index)
        timeout = resp['timeout']
        ms += " 用户'{}', 与{}秒延迟后发送数据 gps={}".format(names[user_id], timeout, gps)
        recode(ms)
        print(ms)
        time.sleep(timeout)
        func(gps)  # 发送数据
        print("{}: {} get gps end,timeout is {}".format(datetime.datetime.now(), user_id, timeout))


def run_send_gps(user_id, func):
    """向平台发送模拟的实时gps数据的线程"""
    t = threading.Thread(target=send_gps, args=(user_id, func), daemon=True)  # daemon表示是否主线程结束就放弃运行?
    t.start()
    return True


def analysis_gps(user_id: str) -> None:
    """
    分析gps数据
    :return:
    """
    print(user_id)
    global REPORT_DICT, GPS_DICT
    gps_list = GPS_DICT[ObjectId(user_id) if isinstance(user_id, str) else user_id]
    reports = REPORT_DICT[str(user_id) if isinstance(user_id, ObjectId) else user_id]
    for report in reports:
        report_datetime = report['report_datetime']
        end = mongo_db.get_datetime_from_str(report_datetime)
        # begin = end - datetime.timedelta(hours=1)
        # sub_gps = [gps for gps in gps_list if begin <= gps['time'] < end]
        # if len(sub_gps) > 1:
        #     # 统计这一个分时区间的数据
        #     print(sub_gps)
        #     begin_position = sub_gps[0]
        #     end_position = sub_gps[-1]
        #     total_mileage = scale_mileage(begin_position['loc']['coordinates'], end_position['loc']['coordinates'])  # 里程
        #     total_mileage = 92 if total_mileage > 100 else total_mileage
        #     max_speed = max([gps['speed'] for gps in sub_gps])  # 最高速度
        #     the_time = (end_position['time'] - begin_position['time']).total_seconds() / 3600
        #     avg_speed = total_mileage / the_time
        #     print(total_mileage, max_speed, the_time, avg_speed, end_position['time'])
        #     print(report['drive_distance'], report['max_speed'], report['average_speed'], report['report_datetime'])
        #     report['drive_distance'] = total_mileage
        #     report['max_speed'] = max_speed if max_speed > avg_speed else avg_speed + random.randint(30, 60) / 10
        #     report['average_speed'] = avg_speed
        #     report['drive_time'] = the_time

    dir_path = os.path.join(project_dir, "resources", "gps")
    file_path = os.path.join(dir_path, "report.pkl")
    f = open(file_path, "bw")
    REPORT_DICT['59cda964ad01be237680e29d'] = REPORT_DICT['59cda964ad01be237680e29d'][0:7]
    t = REPORT_DICT['59cda886ad01be237680e28e']
    t2 = []
    for x in t:
        if isinstance(x['drive_distance'], str):
            x['drive_distance'] = float(x['drive_distance'].split("km")[0])
        t2.append(x)
    REPORT_DICT['59cda886ad01be237680e28e'] = t2
    pickle.dump(REPORT_DICT, f)
    f.close()


def create_drive_action(report_list: list) -> list:
    """
    根据用户的报告list,随机生产不良驾驶行为的报告.
    :param report_list:
    :return:
    """
    """
            'speeding drive': '超速行驶',
            'speeding left turn': '急转',
            'speeding right turn': '急转',
            'calling drive': '打电话',
            'quickly accelerate': "急加速",
            'quickly decelerate': "急减速",
            'fatigue drive': '疲劳驾驶',
            'play phone drive': '玩手机',
            'quick lane': '急变道'
    """
    for i, report in enumerate(report_list):
        if i == 4:
            report['bad_drive_action'].append({"type": "fatigue drive"})
        if random.randint(0, 5) % 2 == 0 and len(report['bad_drive_action']) < 2:
            name = random.choice(['speeding left turn', 'speeding right turn', 'quickly accelerate', 'play phone drive', 'quick lane'])
            report['bad_drive_action'].append({"type": name})
    indexs = [i for i, report in enumerate(report_list) if {"type": "play phone drive"} in report['bad_drive_action']]
    if len(indexs) > 3 and random.choice([True, False]):
        report_list[random.choice(indexs)]['bad_drive_action'].append({"type": 'calling drive'})
    return report_list


def time_shard_report(user_id: (str, ObjectId)) -> list:
    """
    查询用户的当天分时安全报告.注意,这个报告是从本地取的.
    :param user_id:
    :return:
    """
    global REPORT_DICT, timeout_seconds_dict
    delta = timeout_seconds_dict[ObjectId(user_id) if isinstance(user_id, str) else user_id]
    user_id = str(user_id) if isinstance(user_id, ObjectId) else user_id
    reports = REPORT_DICT[user_id]
    now = datetime.datetime.now()
    # 把当前时间换算成原始的数据时间
    query_datetime = now - datetime.timedelta(seconds=delta)
    querys = [report for report in reports if mongo_db.get_datetime_from_str(report['report_datetime']) <= query_datetime]
    print(querys)
    """合成一个的报告"""
    """
    {'max_speed': 0.0,
    'drive_rank': 10,
    'bad_drive_action': [{}],
    'username': '刘成刚',
    'reset_time': 1,
    'company': '顺风快运',
    'average_speed': 0.025138574939575768,
    'drive_score': 97,
    'phone_num': '17317656212',
    'health': {
                'sleep_time': {'datetime': '2017-12-18 01:00:00', 'value': 3},
                'heart_rate': {'datetime': '2017-12-18 01:00:00', 'value':
                                                                        {'03:00': 82, '15:00': 75, '12:00': 83,
                                                                         '16:00': 90, '13:00': 83, '19:00': 81,
                                                                         '02:00': 99, '07:00': 86, '14:00': 86,
                                                                         '11:00': 80, '01:00': 81, '22:00': 90,
                                                                         '10:00': 85, '23:00': 75, '24:00': 99,
                                                                         '20:00': 97, '18:00': 91, '09:00': 82,
                                                                         '06:00': 82, '04:00': 97, '08:00': 94,
                                                                         '21:00': 92, '17:00': 100, '05:00': 82
                                                                         }
                                },
                'mood': {'datetime': '2017-12-18 01:00:00', 'value':
                                                                    {'03:00': 78, '15:00': 75, '12:00': 78, '16:00': 81,
                                                                     '13:00': 93, '19:00': 93, '02:00': 80, '07:00': 93,
                                                                     '14:00': 77, '11:00': 89, '01:00': 82, '22:00': 93,
                                                                     '10:00': 91, '23:00': 89, '24:00': 88, '20:00': 91,
                                                                     '18:00': 95, '09:00': 81, '06:00': 77, '04:00': 76,
                                                                     '08:00': 79, '21:00': 96, '17:00': 86, '05:00': 91
                                                                     }
                         }
               },
    'drive_age': 6,
    'oil_cost': 48,
    'drive_time': 8,
    'drive_distance': 0.024,
    'id': '59cda57bad01be0912b352da',
    'report_datetime': '2017-12-18T01:00:00'
    }
    """
    report = dict()
    report['report_datetime'] = now.strftime("%F")
    report['drive_distance'] = str(round(sum([x['drive_distance'] for x in querys]), 1)) + "km"
    report['drive_time'] = round(sum([x['drive_time'] for x in querys]), 2)
    report['oil_cost'] = round(sum([x['drive_time'] for x in querys]) / len(querys), 1)
    report['average_speed'] = round(sum([x['average_speed'] for x in querys]) / len(querys), 1)
    report['drive_score'] = round(sum([x['drive_score'] for x in querys]) / len(querys), 0)
    report['drive_age'] = querys[-1]['drive_age']
    report['phone_num'] = querys[-1]['phone_num']
    report['username'] = querys[-1]['username']
    health = querys[-1]['health']
    report['health'] = health
    report['id'] = querys[-1]['id']
    report['drive_rank'] = querys[-1]['drive_rank']
    report['company'] = querys[-1]['company']
    report['max_speed'] = round(max([x['max_speed'] for x in querys]), 1)
    report['reset_time'] = int(sum([x['reset_time'] for x in querys]))
    bad_drive_action = []
    [bad_drive_action.extend(x['bad_drive_action']) for x in querys]
    report['bad_drive_action'] = bad_drive_action
    return [{"_source": report}]


need_recalculate()  # 检查


if __name__ == "__main__":
    # for user_id in user_ids:
    #     run_send_gps(user_id, print)
    #################################
    # for x in range(2):
    #     t = threading.Thread(target=load_data,  args=(str(x),), daemon=False)
    #     t.start()
    ##########################

    # for user_id in user_ids:
    #     # time_shard_report(user_id)
    #     analysis_gps(user_id)
    """生成不良驾驶行为"""
    global REPORT_DICT
    for k, v in REPORT_DICT.items():
        v = create_drive_action(v)
    dir_path = os.path.join(project_dir, "resources", "gps")
    file_path = os.path.join(dir_path, "report.pkl")
    f = open(file_path, "bw")
    pickle.dump(REPORT_DICT, f)
    f.close()
    pass