#  -*- coding: utf-8 -*-
import requests
import random
import datetime
import grequests
from uuid import uuid4
import os
import time
import random
import pickle
import threading


"""测试模块,增强版"""

"""
全局变量,存放每个异步请求的信息,其组成如下:
G_DICT = {
    count: 100,   # 请求总数
    success: 80,  # 成功计数
    error: 20,    # 失败计数
    records: {    # 记录详情
        kye_1: {"begin": "2017-12-12 0:0:0.123", "end": "2017-12-12 0:0:3.123", "status": 200, "delta": delta},
        kye_2: {"begin": "2017-12-12 0:0:2.123", "end": "2017-12-12 0:0:4.123", "status": 200, "delta": delta},
        kye_1: {"begin": "2017-12-12 0:0:4.123", "end": "2017-12-12 0:0:5.123", "status": 500, "delta": delta},
        .......
    }
}
"""
G_DICT = dict()


def test_gps_push(num_str: str = "0"):
    """测试是是上传gps数据"""
    auth_token = "a129da33b21a4bb6800847d6627b2f4f"  # app段登录标识
    headers = {"auth_token": auth_token}
    args = {
        "ct": "上海市",
        "dt": "嘉定区",
        "speed": 0.0,
        "longitude": 121 + random.randint(1, 99999) / 100000,
        "be": 0.0,
        "fl": "false",
        "app_version": "1.2.4.0122 Debug",
        "pv": "上海市",
        "ac": 15.0,
        "ts": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %f"),
        "latitude": 31 + random.randint(1, 99999) / 100000,
        "ad": "310114",
        "altitude": 0.0,
        "amap": "amap",
        "flag": "test"
    }
    # print(args)
    print("{} begin".format(num_str))
    res = requests.post("http://safego.org:5000/api/gps_push", headers=headers, data=args)
    status = res.status_code
    if status == 200:
        print("{} end".format(num_str))
    else:
        print("{} error, code={}".format(num_str.format(status)))
        # print(res.json())


def pickle_data(data_dict: dict) -> bool:
    """
    打包数据到pkl文件
    :param data_dict:
    :return:
    """
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_name = "{}.pkl".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    file_path = os.path.join(dir_path, file_name)
    out_put = open(file_path, 'wb')
    pickle.dump(data_dict, out_put)
    out_put.close()
    return True


def async_callback(*args, **kwargs):
    """grequests的回调函数"""
    resp = args[0]
    status = resp.status_code
    key = resp.url.split("=")[-1]
    global G_DICT
    count = G_DICT['count']
    records = G_DICT['records']
    success = G_DICT['success']
    error = G_DICT['error']
    temp = records[key]
    b = temp['begin']
    e = datetime.datetime.now()
    delta = (e - b).total_seconds()
    temp['end'] = e
    temp['delta'] = delta
    temp['status'] = status
    if status == 200:
        success += 1
    else:
        print(status)
        error += 1
    G_DICT['success'] = success
    G_DICT['error'] = error
    records[key] = temp
    G_DICT['records'] = records
    # print(count, success, error)
    if (success + error) == count:
        """所有请求都已经返回"""
        pickle_data(G_DICT)
    else:
        pass


def except_handler(*args, **kwargs) -> None:
    """
    异常处理函数
    :param args:
    :param kwargs:
    :return:
    """
    print(args, kwargs)
    pass


def generator_gps_dict(ran: int = None) -> dict:
    """
    随机生成一个gps字典信息
    :param ran: 随机因子
    :return:
    """
    ran = random.randint(1, 999999) if ran is None else ran
    the_date = datetime.datetime.now()
    delta = datetime.timedelta(microseconds=ran)
    the_date = the_date - delta
    args = {
        "ct": "上海市",
        "dt": "嘉定区",
        "speed": 0.0,
        "longitude": 121 + random.randint(1, 99999) / 100000,
        "be": 0.0,
        "fl": "false",
        "app_version": "1.2.4.0122 Debug",
        "pv": "上海市",
        "ac": 15.0,
        "ts": the_date.strftime("%Y-%m-%d %H:%M:%S %f"),
        "latitude": 31 + random.randint(1, 99999) / 100000,
        "ad": "310114",
        "altitude": 0.0,
        "amap": "amap",
        "flag": "test"
    }
    return args


def test_gps_push_async(length: int = 10) -> bool:
    """
    测试是是上传gps数据,注意,这是异步方式
    :param length: 并发数字
    :return: True
    """
    auth_token = "a129da33b21a4bb6800847d6627b2f4f"  # app段登录标识
    headers = {"auth_token": auth_token}

    tasks = []
    global G_DICT
    if len(G_DICT) > 0:
        G_DICT = dict()
    records = dict()
    G_DICT['count'] = length
    G_DICT['success'] = 0
    G_DICT['error'] = 0
    for i in range(length):
        key = uuid4().hex
        records[key] = {"begin": datetime.datetime.now()}
        # url = "http://5k.safego.org/api/gps_push".format(key)
        # url = "http://5k.safego.org/hello".format(key)
        # url = "http://127.0.0.1:5000/api/gps_push".format(key)
        # url = "http://192.168.0.112:5000/api/gps_push".format(key)
        url = "http://127.0.0.1:5000/hello?uuid={}".format(key)
        # url = "http://192.168.0.112:5000/hello?uuid={}".format(key)
        # url = "http://39.108.67.178:5000/register".format(key)
        # url = "http://safego.org/app/".format(key)
        req = grequests.AsyncRequest(method='get', url=url,
                                     headers=headers, data=generator_gps_dict(), callback=async_callback)
        tasks.append(req)
    G_DICT['records'] = records
    grequests.map(tasks, exception_handler=except_handler)
    print("成功率: {}%".format((G_DICT['success'] / G_DICT['count']) * 100))
    return True  # 任务成功结束


def batch_test_async(num: int = 10, length: int = 100):
    """
    批量请求压力测试,异步方式
    :param num: 测试次数
    :param length: 并发数次
    :return:
    """
    for i in range(num):
        b = datetime.datetime.now()
        print("{} {} 并发测试开始".format(b, length))
        test_gps_push_async(length)
        e = datetime.datetime.now()
        d = (e - b).total_seconds()
        print("{} {} 并发测试结束,耗时: {}秒".format(e, length, d))


t_count = 0
t_success = 0
lock_add = threading.Lock()  # 多线程锁
lock_success = threading.Lock()  # 多线程锁
lock_stop = threading.Lock()  # 多线程锁
stop_count = 0  # 停止的线程计数

def add_count():
    """请求数+1"""
    lock_add.acquire()
    global t_count
    t_count += 1
    lock_add.release()
        
        
def add_success():
    """成功请求数+1"""
    lock_success.acquire()
    global t_success
    t_success += 1
    lock_success.release()


def add_stop():
    """停止线程数+1"""
    lock_stop.acquire()
    global stop_count
    stop_count += 1
    lock_stop.release()


def test_gps_push_always(stop_time: datetime.datetime):
    """
    测试是是上传gps数据,一直发送.注意,这是一普通的函数,给多线程方式调用的
    :return:
    """
    auth_token = "a129da33b21a4bb6800847d6627b2f4f"  # app段登录标识
    headers = {"auth_token": auth_token}
    # url = "http://5k.safego.org/api/gps_push"
    # url = "http://safego.org:7777/api/gps_push"
    # url = "http://5k.safego.org/hello"
    # url = "http://127.0.0.1:5000/api/gps_push"
    # url = "http://192.168.0.112:5000/api/gps_push"
    url = "http://127.0.0.1:5000/hello"
    # url = "http://192.168.0.112:9999"
    ses = requests.Session()
    ses.headers = headers
    flag = True
    while flag:
        data = generator_gps_dict()
        add_count()
        try:
            res = ses.post(url, data=data)
            status = res.status_code
            if status == 200:
                add_success()
            else:
                print(status)
        except Exception as e:
            print(e)
        now = datetime.datetime.now()
        if (now - stop_time).total_seconds() >= 0:
            flag = False
        time.sleep(random.randint(1, 10) / 1000)
    add_stop()
    

def batch_test_thread(minute: (float, int) = 1, length: int = 100):
    """
    多线程的压力测试
    :param minute: 测试持续几分钟?
    :param length: 并发数
    :return:
    """
    begin = datetime.datetime.now()
    stop = begin + datetime.timedelta(minutes=minute)
    for i in range(length):
        t = threading.Thread(target=test_gps_push_always, args=(stop, ), daemon=True)
        t.start()
        print("线程{} go!".format(i + 1))
    global stop_count
    while stop_count < length:
        time.sleep(1)
    print("测试时间:{}分钟, 共计发送{}个gps数据, 成功{}个, 成功率: {}%".format(minute, t_count, t_success,
                                                            (t_success / t_count) * 100))


if __name__ == "__main__":
    """异步方法测试并发gps接口并发能力"""
    batch_test_async(1, 1200)
    """多线程方法测试并发gps接口并发能力"""
    # batch_test_thread(1, 500)
    pass
