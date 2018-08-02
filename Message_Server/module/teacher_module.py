# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
from bson.objectid import ObjectId
import datetime
import random
from log_module import get_logger
from werkzeug.contrib.cache import SimpleCache


simple_cache = SimpleCache()
logger = get_logger()


"""
此模块用于根据老师喊单的信号，生成对应的虚拟老师数据
"""


class Deposit(mongo_db.BaseDoc):
    """
    入金/存款(记录),当老师做单的时候,如果资金不足,就会激发入金行为
    """
    _table_name = "deposit"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['t_id'] = ObjectId  # 老师id
    type_dict['num'] = float  # 入金金额.
    type_dict['time'] = datetime.datetime

    @classmethod
    def generator_deposit(cls, min_money: float) -> float:
        """
        生成一个加金的数字
        :param min_money: 最低额度.加金金额必须大于此额度.
        :return: 实际的加金额度.
        """
        l = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000,  15000, 20000, 30000, 50000, 100000]
        r = 0
        for x in l:
            if min_money * 2 <= x:
                r = x
                break
            else:
                pass
        return r


class Teacher(mongo_db.BaseDoc):
    """
    老师,微信项目（Webchat_Server）有一个同名的类，不同的是：
    Message_Server项目下的Teacher类主要负责item_module.Trade.sync_from_signal(生成虚拟老师交易信号)时取老师列表。
    Webchat_Server项目项目下的Teacher类，主要负责老师的管理。（属性，头像的修改）
    两个类属性的字段相同即可.
    Webchat_Server项目项目下的teacher_module函数更丰富一些。
    你会在2个项目下分别看到这两个模块。
    """
    _table_name = "teacher"
    type_dict = dict()
    """真实老师的id取自简道云"""
    type_dict['_id'] = ObjectId
    """真实老师的name可能取自简道云(也可再修改)"""
    type_dict['name'] = str   # 展示的名字，比如青云老师等
    type_dict['real_name'] = str  # 真实姓名，非必须
    type_dict['head_img'] = str  # 头像文件相当与项目根目录的路径
    type_dict['img'] = str  # 半身像文件相当与项目根目录的路径
    type_dict['level'] = str  # 老师等级
    type_dict['motto'] = str  # 座右铭
    type_dict['feature'] = str  # 特性，风格，特点
    type_dict['resume'] = str  # 简历
    type_dict['create_date'] = datetime.datetime
    type_dict['native'] = bool  # 是否是真实的teacher？
    type_dict['from_id'] = ObjectId  # 虚拟老师专有，发源老师id，保持不连，除非修改
    type_dict['direction'] = str  # 虚拟老师专有，跟的方向，有三种 follow/reverse/random
    type_dict['profit_ratio'] = float  # 盈利率, 每次close时候计算
    type_dict['profit_amount'] = float  # 盈利总额.每次close时候计算
    type_dict['deposit'] = float  # 存款,当前本金.每次close时候计算
    type_dict['deposit_amount'] = float  # 历次存款总额,每次close时候计算
    type_dict['lots_range'] = list  # 手数范围.

    @classmethod
    def instance(cls, **kwargs):
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        if "name" not in kwargs:
            ms = "name必须"
            raise ValueError(ms)
        if "native" not in kwargs:
            ms = "native必须"
            raise ValueError(ms)
        return cls(**kwargs)

    @classmethod
    def init_head_image_list(cls) -> list:
        """
        初始化头像列表
        :return:
        """
        d = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        p = os.path.join(d, "static", 'images', 'head_image')
        ns = os.listdir(p)
        res = list()
        for name in ns:
            u = os.path.join(p, name)
            res.append(u)
        key = "t_head_img"
        simple_cache.set(key=key, value=res, timeout=900)
        return res

    @classmethod
    def pop_head_image(cls) -> str:
        """
        尽量不重复的生成老师的头像,如果头像资源用尽,那就重头来.
        :return:
        """
        key = "t_head_img"
        m = simple_cache.get(key)
        if m is None or len(m) == 0:
            m = cls.init_head_image_list()
        else:
            pass
        url = m.pop(random.randint(0, len(m) - 1))
        simple_cache.set(key=key, value=m, timeout=900)
        return url

    @classmethod
    def generator_lots_range(cls) -> list:
        """
        虚拟一个手数范围
        :return:
        """
        begin = random.choice([1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3])
        step = random.choice([2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 7, 7])
        return [begin, begin + step]

    @classmethod
    def generator_init(cls, t_id: (str, ObjectId), t_name: str, create_date: datetime.datetime) -> list:
        """
        根据一个老师的id,名字和创建时间.生成3个虚拟的老师,加上原始的真实老师,一起返回(4个doc)
        type_dict['name'] = str   # 展示的名字，比如青云老师等
        type_dict['real_name'] = str  # 真实姓名，非必须
        type_dict['head_img'] = str  # 头像文件相当与项目根目录的路径
        type_dict['img'] = str  # 半身像文件相当与项目根目录的路径
        type_dict['level'] = str  # 老师等级
        type_dict['motto'] = str  # 座右铭
        type_dict['feature'] = str  # 特性，风格，特点
        type_dict['resume'] = str  # 简历
        type_dict['create_date'] = datetime.datetime
        type_dict['native'] = bool  # 是否是真实的teacher？
        type_dict['from_id'] = ObjectId  # 虚拟老师专有，发源老师id，保持不连，除非修改
        type_dict['direction'] = str  # 虚拟老师专有，跟的方向，有三种 follow/reverse/random
        type_dict['profit_ratio'] = float  # 盈利率, 每次close时候计算
        type_dict['profit_amount'] = float  # 总额.每次close时候计算
        type_dict['deposit'] = float  # 存款,当前本金.每次close时候计算
        type_dict['lots_range'] = list  # 手数范围.
        #########################################
        [{"_id": k, "name": v, "native": True},
         {"name": "{}_正向".format(v), "native": False, "from_id": k, "direction": "follow"},
            t2 = {"name": "{}_反向".format(v), "native": False, "from_id": k, "direction": "reverse"}
            t3 = {"name": "{}_随机".format(v), "native": False, "from_id": k, "direction": "random"}
        :param t_id:
        :param t_name:
        :param create_date:
        :return:
        """
        t_id = ObjectId(t_id) if isinstance(t_id, str) and len(t_id) == 24 else t_id
        """原始的老师的init字典"""
        raw = {
            "_id": t_id,  # 老师id
            "name": t_name,
            "head_img": cls.pop_head_image(),
            "create_date": create_date,
            "native": True,  # 真实老师
            "lots_range": cls.generator_lots_range(), # 手数范围,和性格有关
            "deposit": 0.0,     # 存款,初始资金,都是0
            "profit_ratio": 0.0,   # 盈利率, 每次close时候计算,profit_amount/deposit得出.百分比数值
            "profit_amount": 0,        # 盈利总额.每次close时候计算,初始0,
            # "from_id": t_id,  # 发源老师id, 主要是名字来源,没有其他方面的意义
        }
        """正向"""
        follow =

    @classmethod
    def rebuild(cls) -> None:
        """
        从交易信号中，初始化老师，这个动作会清除所有的老师记录.
        仅在初始化时候使用。
        :return:
        """
        t_list = []  # 存放生成的老师的容器
        f = dict()
        s = [("create_time", -1)]
        p = ['creator_id', 'creator_name', 'create_time']
        ses = mongo_db.get_conn(table_name="signal_info")
        args = {"filter": f, "sort": s, "projection": p}
        r = ses.find(**args)
        native = dict()
        for x in r:
            _id = ""
            try:
                _id = x['creator_id']
                name = x['creator_name']
            except KeyError as e:
                # print(e)
                # print(x)
                try:
                    name = x['updater_name']
                except KeyError as e:
                    print(e)
                    print(x)
            if isinstance(_id, str) and len(_id) == 24:
                _id = ObjectId(_id)
                if _id not in native:
                    native[_id] = name
                else:
                    prev_name = native[_id]
                    if prev_name == name:
                        pass
                    else:
                        ms = "新旧老师名字不一致：prev={}, now={}".format(prev_name, name)
                        raise ValueError(ms)
            else:
                ms = "异常的_id：{}".format(_id)
                print(ms)
        print(native)
        for k, v in native.items():
            t = {"_id": k, "name": v, "native": True}
            t1 = {"name": "{}_正向".format(v), "native": False, "from_id": k, "direction": "follow"}
            t2 = {"name": "{}_反向".format(v), "native": False, "from_id": k, "direction": "reverse"}
            t3 = {"name": "{}_随机".format(v), "native": False, "from_id": k, "direction": "random"}
            cls(**t).save_plus()
            cls(**t1).save_plus()
            cls(**t2).save_plus()
            cls(**t3).save_plus()

    @classmethod
    def direction_map(cls) -> dict:
        """
        获取以方向为key,老师的doc的list为val的字典.
        用于在生成虚拟信号的时候提供随机特性
        :return:
        """
        ts = Teacher.find_plus(filter_dict=dict(), to_dict=True)
        t_dict = dict()  # 方向和老师的字典
        for t in ts:
            d = t.get("direction")
            if d is not None:
                if d in t_dict:
                    t_dict[d].append(t)
                else:
                    t_dict[d] = [t]
        return t_dict


if __name__ == "__main__":
    Teacher.init_head_image_list()
    pass