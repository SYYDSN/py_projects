#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import random
import mongo_db
import datetime
from io import BytesIO
from PIL import Image
from model.driver_module import *


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef


"""用于生成数据的模块"""


def produce_route(user_id: DBRef) -> object:
    """
    随机生成熟悉的路线的数据.保存数据,并返回实例本身
    :param user_id:
    :return:
    """
    cities = ["上海", "北京", "南京", "苏州", "杭州", "宁波", "成都", "重庆", "贵阳", "武汉", "长沙", "南昌"]
    l = random.randint(2, 3)
    c = list()
    while len(c) < l:
        city = random.choice(cities)
        if city not in c:
            c.append(city)
        else:
            pass
    init = {
        "_id": ObjectId(),
        "cities": cities,
        "driver_id": user_id,
        "create_date": datetime.datetime.now()
    }
    obj = Route(**init)
    obj.save_plus()
    return obj


def show_honor_image(o_id: ObjectId) -> None:
    """
    显示荣誉证书的图片.
    :param o_id:
    :return:
    """
    d = Honor.find_by_id(o_id=o_id)
    data = d.get_attr("image")
    store = BytesIO(initial_bytes=data)
    """
    也可以这样:
    store = BytesIO()
    store.write(data)
    """
    img = Image.open(store)
    img.show()
    # img.close()


def produce_honor(user_id: DBRef) -> object:
    """
    随机生成荣誉证书的数据.保存数据,并返回实例本身
    :param user_id:
    :return:
    """
    p = "/home/walle/图片/2018-05-28 18-42-07屏幕截图.png"
    f = open(file=p, mode="rb")
    image = f.read()
    f.close()
    init = {
        "_id": ObjectId(),
        "driver_id": user_id,
        "image": image,
        "time": mongo_db.get_datetime_from_str("2018-01-01"),
        "info": "xxx同志获得2017年度工作标兵称号",
        "create_date": datetime.datetime.now()
    }
    obj = Honor(**init)
    obj.save_plus()
    return obj


def generate_plate() -> str:
    """
    生成车牌
    :return:
    """
    p = [x for x in "黑吉辽京津蒙鲁苏浙沪闽粤桂琼晋陕甘宁青新藏川云渝湘鄂赣豫港澳皖冀"]
    l = [x.upper() for x in "abcdefghijklmnopqrstuvwxyz"]
    n = str(random.randint(0, 99999)).zfill(5)
    return "{}{}{}".format(random.choice(p), random.choice(l), n)


def produce_vehicle(user_id: DBRef) -> object:
    """
    随机生成车辆信息的数据.保存数据,并返回实例本身
    :param user_id:
    :return:
    """
    p = "/home/walle/图片/timg.jpeg"
    f = open(file=p, mode="rb")
    image = f.read()
    f.close()
    now = datetime.datetime.now()
    init = {
        "_id": ObjectId(),
        "driver_id": user_id,
        "image": image,
        "plate_number": generate_plate(),
        "vehicle_type": "大型客车",
        "vehicle_load": 14,
        "vehicle_length": 9.6,
        "owner_name": "无名氏",
        "address": "xx省xx市xxx路xxx号",
        "vehicle_model": "一汽解放J6",
        "vin_id": str(random.randint(100000, 999999)),
        "engine_id": str(random.randint(100000, 999999)),
        "register_date": now - datetime.timedelta(days=300),
        "issued_date": now - datetime.timedelta(days=300),
        "create_date": now
    }
    obj = Vehicle(**init)
    obj.save_plus()
    return obj


def produce_history(user_id: DBRef) -> object:
    """
    随机生成工作履历.保存数据,并返回实例本身
    :param user_id:
    :return:
    """
    n = random.randint(1, 5)
    now = datetime.datetime.now()
    init = {
        "_id": ObjectId(),
        "driver_id": user_id,
        "begin": now - datetime.timedelta(n * 365),
        "end": now - datetime.timedelta((n - 1) * 365),
        "enterprise_name": "xx物流集团公司",
        "enterprise_scale": 100,
        "dept_name": "运输一部",
        "post_name": "驾驶员",
        "team_size": 0,
        "vehicle_type": "平板式货车",
        "vehicle_load": 14,
        "vehicle_length": 9.6,
        "description": "负责xxx到xx之间的物流工作,遵守工作纪律恪守职业道德具备良好的职业修养为领导开车的专职司机要谦虚谨慎"
                       "严守公司机密维护公司利益",
        "achievement": "工作努力,热情为公司领导服务一切以领导满意为宗旨",
        "create_date": datetime.datetime.now()
    }
    obj = WorkHistory(**init)
    obj.save_plus()
    return obj


def produce_resume() -> None:
    """
    随机生成司机简历并保存
    :return:
    """
    p = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍" \
        "史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈" \
        "项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯"
    p = [x for x in p]
    p1 = "/home/walle/图片/驾照.jpeg"
    f1 = open(file=p1, mode="rb")
    dl_image = f1.read()
    f1.close()
    phone = "1{}".format(random.randint(3000000000, 9999999999))
    now = datetime.datetime.now()
    y = random.randint(1960, 1995)
    m = str(random.randint(1, 12)).zfill(2)
    d = str(random.randint(1, 28)).zfill(2)
    birth_date = mongo_db.get_datetime_from_str("{}-{}-{}".format(y, m, d))
    id_num = "{}{}{}{}{}".format(random.randint(111000, 999999), y, m, d, str(random.randint(1, 9999)).zfill(4))
    base = random.randint(5, 10) * 1000
    u_id = ObjectId()
    ref = DBRef(database=mongo_db.db_name, collection=DriverResume.get_table_name(), id=u_id)
    init = {
        "_id": u_id,
        "user_name": phone,
        "real_name": random.choice(p) + "某某",
        "gender": "男",
        "birth_place": "上海",
        "living_place": "上海",
        "address": "上海市嘉定区安亭镇昌吉东路58号",
        "phone": phone,
        "email": "{}@qq.com".format(phone[3:]),
        "birth_date": birth_date,
        "id_num": id_num,
        "age": now.year - y + 1,
        "driving_experience": 10,
        "industry_experience": 7,
        "education": 2,
        "status": 1,
        "dl_image": dl_image,
        "dl_license_class": "B1",
        "dl_first_date": mongo_db.get_datetime_from_str("2008-1-1"),
        "dl_valid_begin": mongo_db.get_datetime_from_str("2018-1-1"),
        "dl_valid_duration": 5,
        "rtqc_image": dl_image,
        "rtqc_license_class": "危险货物运输驾驶员",
        "rtqc_first_date": mongo_db.get_datetime_from_str("2010-1-1"),
        "rtqc_valid_begin": mongo_db.get_datetime_from_str("2015-1-1"),
        "rtqc_valid_end": mongo_db.get_datetime_from_str("2025-1-1"),
        "vehicle": [produce_vehicle(ref).get_dbref()],
        "want_job": True,
        "remote": True,
        "expected_salary": [base, base * 1.5],
        "routes": [produce_route(ref).get_dbref()],
        "work_history": [produce_history(ref).get_dbref(), produce_history(ref).get_dbref()],
        "last_company": "xx物流集团公司",
        "self_evaluation": "自我评价是多学科研究的对象它已经被哲学、心理学、社会心理学、社会学、"
                           "教育学、文化学、人学、价值科学等都许多学科所关注",
        "honor": [produce_honor(ref).get_dbref()],
        "create_date": datetime.datetime.now()
    }
    obj = DriverResume(**init)
    obj.save_plus()


if __name__ == "__main__":
    # ref = DBRef(database=mongo_db.db_name, collection="user_info", id=ObjectId())
    # produce_honor(ref)
    # xx = ObjectId("5b2cad1a4660d33bbe4d3481")
    # show_honor_image(xx)
    """生成300个司机简历"""
    # for i in range(300):
    #     produce_resume()
    f = dict()
    u = {"$set": {"last_company": "xx物流集团公司"}}
    DriverResume.update_many_plus(filter_dict=f, update_dict=u)
    pass