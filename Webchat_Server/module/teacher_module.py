# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
from module.pickle_data import *


ObjectId = mongo_db.ObjectId


"""
此模块用于根据老师喊单的信号，生成对应的虚拟老师数据
"""


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
    type_dict['profit_amount'] = float  # 总额.每次close时候计算
    type_dict['deposit'] = float  # 存款,当前本金.每次close时候计算
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
    def rebuild(cls) -> None:
        """
        从交易信号中，初始化老师，如果你想重置所有的老师，请手动清空旧的老师列表,
        仅在初始化时候使用。
        :return:
        """
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
    def follow_count(cls) -> dict:
        """
        按老师分组统计跟随人数。
        :return:
        """
        f = dict()
        p = ["_id", "name", "head_img"]
        ts = cls.find_plus(filter_dict=f, projection=p, to_dict=True)
        t_ids = [x['_id'] for x in ts]
        ses = mongo_db.get_conn(table_name="wx_user")
        m = {"$match": {"follow": {"$elemMatch": {"$in": t_ids}}}}
        u = {"$unwind": "$follow"}
        g = {"$group": {"_id": "$_id", "total": {"$sum": 1}}}
        pipeline = [m, u, g]
        r = ses.aggregate(pipeline=pipeline)
        count = {x['_id']: x['total'] for x in r}
        ts = {x['_id']: {"name": x['name'], "head_img": x.get("head_img", "/static/images/head_image/t1.jpg")} for x in ts}
        res = dict()
        for k, v in ts.items():
            temp = dict()
            temp['total'] = count.get(k, 0)
            temp['name'] = v['name']
            temp['head_img'] = v["head_img"]
            res[k] = temp
        return res

    @classmethod
    def index(cls, begin: datetime.datetime = None, end: datetime.datetime = None):
        """
        返回首页所用的信息,一个以胜率排序的列表,元素包含胜率.和跟随人数
        :return:
        """
        """默认查询近30天的胜率数据"""
        data = calculate_win_per_by_teacher_mix(begin=begin, end=end)
        """查询老师的跟随人数"""
        d = cls.follow_count()
        res = list()
        for t_id, v in data.items():
            temp = v
            temp.update(d.get(t_id))
            temp['_id'] = t_id
            res.append(temp)
        res.sort(key=lambda obj: obj['win'], reverse=True)
        return res

    @classmethod
    def single_info(cls, t_id: (str, ObjectId), begin: (str, datetime.datetime) = None, end: (str, datetime.datetime) = None) -> dict:
        """
        老师的个人页面，有图标，持仓和历史数据
        :param t_id:
        :param begin:
        :param end:
        :return:
        """
        t_id = t_id if isinstance(t_id, ObjectId) else ObjectId(t_id)
        now = datetime.datetime.now()
        begin = mongo_db.get_datetime_from_str(begin)
        end = mongo_db.get_datetime_from_str(end)
        if end is None:
            end = now
        if begin is None:
            begin = now - datetime.timedelta(days=60)
        data = calculate_win_per_by_week_single(t_id=t_id, begin=begin, end=end)
        return data


if __name__ == "__main__":
    Teacher.index()
    pass