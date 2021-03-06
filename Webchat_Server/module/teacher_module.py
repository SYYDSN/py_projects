# -*- coding: utf-8 -*-
import os
import sys

__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
import random
import hashlib
from module.pickle_data import *
from werkzeug.contrib.cache import SimpleCache

ObjectId = mongo_db.ObjectId
simple_cache = SimpleCache()

"""
此模块用于根据老师喊单的信号，生成对应的虚拟老师数据
"""


class TeacherLog(mongo_db.BaseDoc):
    """
    老师客户端操作的错误日志
    """
    _table_name = "teacher_log"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['url'] = str
    type_dict['error'] = str
    type_dict['args'] = str
    type_dict['error_time'] = datetime.datetime
    type_dict['save_time'] = datetime.datetime

    @classmethod
    def log(cls, t_id: ObjectId, url: str, error_time: datetime.datetime, error: str, content: str) -> None:
        """记录"""
        d = dict()
        d['_id'] = ObjectId()
        d['t_id'] = t_id
        d['error'] = error
        d['url'] = url
        d['args'] = content
        d['error_time'] = error_time
        d['save_time'] = datetime.datetime.now()
        ses = mongo_db.get_conn(table_name=cls.get_table_name())
        ses.insert_one(d)


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
        l = [10000, 15000, 20000, 30000, 50000, 100000]
        r = 0
        for x in l:
            if min_money * 2 <= x:
                r = x
                break
            else:
                pass
        return r


class TeacherImage(mongo_db.BaseFile):
    """老师相关图片"""
    _table_name = "teacher_image"


class Teacher(mongo_db.BaseDoc):
    """
    1. 导入的老师都是真实老师,
    2. 虚拟虚拟老师.以1:4的比例自动生成,
    3. 真实老师和虚拟老师都可以修改资料. 但虚拟老师不能登录.
    :return:

    v_t = [                               # 虚拟老师
        '子中', '一鸣', '连彬',
        越林', '自宾', '成其'
        ]
    2018-11-21新增真实老师(从虚拟老师调整成真实老师).真实老师的几个字段
    native = True, direction字段删除

    以下是真实老师:

    0020 豪何
    0019 誉杰
    0018 东晖
    0017 宇向
    0016 铭远
    0015 俊彦
    0014 扬波
    0013 宗晨
    0012 宜修   2018-12-5 新增
    0011 凯风   2018-12-5 新增
    0010 孟林   2018-12-5 新增
    0009 秦观
    0005 乐天
    0001 北仑

    默认密码都是 xd123457
    0000 非攻 是测试账户 密码:Xd@123457
    老师,Message_server项目有一个同名的类，不同的是：
    Message_Server项目下的Teacher类主要负责item_module.Trade.sync_from_signal(生成虚拟老师交易信号)时取老师列表。
    Webchat_Server项目项目下的Teacher类，主要负责老师的管理。（属性，头像的修改）
    两个类属性的字段相同即可.
    Webchat_Server项目项目下的teacher_module函数更丰富一些。
    你会在2个项目下分别看到这两个模块。
    2018-9-2 新增老师
    为了便于统计成绩和管理,原来的老师会慢慢的停止使用,使用新的一批老师账户来操作.中间会有过度期.2套账户都可以使用
    新的账户体系.
    2919-1-12b 旧账户体系失效. 目前有效的账户是(特征是invalid字段没有)
    [
        ObjectId('5b8c5451dbea62189b5c28eb'), ObjectId('5b8c5451dbea62189b5c28ed'), ObjectId('5b8c5451dbea62189b5c28ee'),
        ObjectId('5b8c5451dbea62189b5c28ea'), ObjectId('5b8c5451dbea62189b5c28f0'), ObjectId('5b8c5451dbea62189b5c28f1'),
        ObjectId('5b8c5451dbea62189b5c28f2'), ObjectId('5b8c5451dbea62189b5c28ef'), ObjectId('5b8c5452dbea62189b5c28f4'),
        ObjectId('5b8c5452dbea62189b5c28f5'), ObjectId('5b8c5452dbea62189b5c28f6'), ObjectId('5b8c5452dbea62189b5c28f3'),
        ObjectId('5b8c5452dbea62189b5c28f8'), ObjectId('5b8c5452dbea62189b5c28f9'), ObjectId('5b8c5452dbea62189b5c28fa'),
        ObjectId('5b8c5452dbea62189b5c28f7'), ObjectId('5b8c5452dbea62189b5c28fc'), ObjectId('5b8c5452dbea62189b5c28fd'),
        ObjectId('5b8c5452dbea62189b5c28fe'), ObjectId('5b8c5452dbea62189b5c28fb'), ObjectId("5bbd3279c5aee8250bbe17d0")
    ]
    其中, 非功老师的id是ObjectId("5bbd3279c5aee8250bbe17d0"),多了一个hide=true的属性
    """
    _table_name = "teacher"
    type_dict = dict()
    """真实老师的id取自简道云"""
    type_dict['_id'] = ObjectId
    """真实老师的name可能取自简道云(也可再修改)"""
    type_dict['name'] = str  # 展示的名字，比如青云老师等
    type_dict['phone'] = str  # 手机号码，用来登录
    type_dict['password'] = str  # 密码.md5加密
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
    type_dict['lots_range'] = list  # 手数范围.
    type_dict['hide'] = bool  # 是否隐藏?
    type_dict['deposit'] = float  # 存款,当前本金.每次close时候计算
    type_dict['deposit_amount'] = float  # 累计存款,所有本金.会累计每次加金的综合
    type_dict['profit_ratio'] = float  # 盈利率, 每次close时候计算
    type_dict['profit_amount'] = float  # 总额.每次close时候计算
    type_dict['win_ratio'] = float  # 胜率
    type_dict['win_count'] = int  # 胜场统计
    type_dict['case_count'] = int  # 喊单总计
    type_dict['invalid'] = bool  # 标记为真的不纳入有效统计范围,trade中也有这个字段.2019-1-12b

    @classmethod
    def instance(cls, **kwargs):
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        # if "show" not in kwargs:
        #     kwargs['show'] = True
        if "name" not in kwargs:
            ms = "name必须"
            raise ValueError(ms)
        if "native" not in kwargs:
            ms = "native必须"
            raise ValueError(ms)
        if "head_img" not in kwargs:
            kwargs['head_img'] = cls.pop_head_image()
        if "win_ratio" not in kwargs:
            kwargs['win_ratio'] = 0
        if "win_count" not in kwargs:
            kwargs['win_count'] = 0
        if "case_count" not in kwargs:
            kwargs['case_count'] = 0
        if "profit_ratio" not in kwargs:
            kwargs['profit_ratio'] = 0
        if "profit_amount" not in kwargs:
            kwargs['profit_amount'] = 0
        if "deposit" not in kwargs:
            kwargs['deposit'] = 0
        if "deposit_amount" not in kwargs:
            kwargs['deposit_amount'] = 0
        if "lots_range" not in kwargs:
            kwargs['lots_range'] = cls.generator_lots_range()
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
            u = os.path.join("/static/images/head_image", name)
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
    def rebuild(cls) -> None:
        """
        这是一个很少使用的函数
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
            cls(**t).save()
            cls(**t1).save()
            cls(**t2).save()
            cls(**t3).save()

    @classmethod
    def follow_count(cls) -> dict:
        """
        按老师分组统计跟随人数。
        :return:
        """
        f = dict()
        p = ["_id", "name", "head_img"]
        ts = cls.find(filter_dict=f, projection=p)
        t_ids = [x['_id'] for x in ts]
        # t_ids = [ObjectId("5bbd3279c5aee8250bbe17d0")]
        ses = mongo_db.get_conn(table_name="wx_user")
        m = {"$match": {"follow": {"$elemMatch": {"$in": t_ids}}}}
        u = {"$unwind": "$follow"}
        g = {"$group": {"_id": "$follow", "total": {"$sum": 1}}}
        pipeline = [m, u, g]
        # pipeline = [m, u]
        r = ses.aggregate(pipeline=pipeline)
        count = {x['_id']: x['total'] for x in r}
        ts = {x['_id']: {"name": x['name'], "head_img": x.get("head_img", "/static/images/head_image/t1.jpg")} for x in
              ts}
        res = dict()
        for k, v in ts.items():
            temp = dict()
            temp['total'] = count.get(k, 0)
            temp['name'] = v['name']
            temp['head_img'] = v["head_img"]
            res[k] = temp
        return res

    @classmethod
    def hold_overflow(cls, teacher_id: ObjectId) -> bool:
        """
        检查老师是否持仓过多?超过5个,超过了就不能开单了.
        :param teacher_id:
        :return:
        """
        f = {"teacher_id": teacher_id, "case_type": "enter"}
        col = mongo_db.get_conn(table_name="trade")
        r = col.count_documents(filter=f)
        return True if r >= 5 else False

    @classmethod
    def index(cls, begin: datetime.datetime = None, end: datetime.datetime = None):
        """
        返回首页所用的信息,一个以胜率排序的列表,元素包含胜率.和跟随人数
        :return:
        """
        """
        查询invalid字段不存在,而且hide不存在的老师. 2019-1-12b
        """
        f = {
            "invalid": {"$exists": False},
            "hide": {"$exists": False}
        }
        data = cls.find(filter_dict=f)
        data = {x["_id"]: x for x in data if not x.get("hide")}
        """查询老师的跟随人数"""
        d = cls.follow_count()
        res = list()
        for t_id, v in data.items():
            temp = v
            temp.update(d.get(t_id))
            temp['_id'] = t_id
            res.append(temp)
        return res

    @classmethod
    def single_info(cls, t_id: (str, ObjectId), begin: (str, datetime.datetime) = None,
                    end: (str, datetime.datetime) = None) -> dict:
        """
        老师的个人页面，有图表，持仓和历史数据
        图表数据改为柱装图 2019-9-17
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
        """
        calculate_win_per_by_week_single和cls.get_hold方法一样,本质上都是调用了hold_info_from_db函数
        """
        data = calculate_win_per_by_week_single(t_id=t_id, begin=begin, end=end)
        t = Teacher.find_by_id(o_id=t_id, can_json=True)
        data.update(t)
        return data

    @classmethod
    def single_info2(cls, t_id: (str, ObjectId), begin: (str, datetime.datetime) = None,
                     end: (str, datetime.datetime) = None) -> dict:
        """
        老师的个人页面，有图表，持仓和历史数据
        本函数是cls.single_info的替代函数，两者的差别是：
        single_info　提供的是按照产品分组，以周切分的胜率统计 2018-11-25
        single_info２　提供的是:
            １.按照周切分的胜率柱状图
            2.按照周切分的收益率柱状图
            3 .按照周切分的收益率线图

        :param t_id:
        :param begin:
        :param end:
        :return:
        """
        data = cls.chart_data(t_id=t_id, begin=begin, end=end)
        t = Teacher.find_by_id(o_id=t_id, can_json=True)
        data = {"chart": data}  # 图表数据
        data.update(cls.history_and_hold(t_id=t_id))  # 历史和持仓
        data.update(t)
        return data

    @classmethod
    def history_and_hold(cls, t_id: (str, ObjectId), prev: int = 60) -> dict:
        """
        获取老师最近的60天持仓和交易历史
        :param t_id:
        :param prev:
        :return:
        """
        now = datetime.datetime.now()
        prev = now - datetime.timedelta(days=prev)
        t_id = ObjectId(t_id) if isinstance(t_id, str) and len(t_id) == 24 else t_id
        f = {"teacher_id": t_id, "enter_time": {"$gte": prev}}
        s = [("enter_time", -1)]
        ses = mongo_db.get_conn(table_name="trade")
        r = ses.find(filter=f, sort=s)
        history = list()
        hold = list()
        [hold.append(x) if x['case_type'] == "enter" else history.append(x) for x in r]
        return {"hold": hold, "history": history}

    @classmethod
    def get_hold(cls, t_id: (str, ObjectId), h_id: (str, ObjectId) = None) -> (None, dict, list):
        """
        获取老师的持仓记录
        相对history_and_hold,这是一个较旧的函数.仅仅为了提供持仓数据
        :param t_id: Teacher._id
        :param h_id: Trade._id
        :return:
        """
        begin = mongo_db.get_datetime_from_str("2018-07-01 17:00:00")
        end = datetime.datetime.now()
        res = hold_info_from_db(t_id=t_id, begin=begin, end=end, h_id=h_id)
        if h_id is None:
            return res
        else:
            if len(res) == 0:
                return None
            else:
                return res[0]

    @classmethod
    def chart_data(cls, t_id: (str, ObjectId), begin: datetime.datetime = None, end: datetime.datetime = None) -> list:
        """
        查询老师个人的图表数据，目前是输出三种：　２０１８－１１－２５
        1. 按照周切分的胜率柱状图
        2. 按照周切分的收益率柱状图
        3. 按照周切分的收益率线图
        :param t_id:
        :param begin:
        :param end:
        :return:
        """
        end = datetime.datetime.now() if end is None else end
        begin = (end + datetime.timedelta(days=182.5)) if begin is None else begin
        t_id = ObjectId(t_id) if isinstance(t_id, str) and len(t_id) == 24 else t_id
        ses = mongo_db.get_conn(table_name="trade")
        pipeline = list()
        match = {"teacher_id": t_id, "case_type": "exit"}
        pipeline.append({"$match": match})
        group = {
            "_id": {"$isoWeek": "$enter_time"},
            "teacher_name": {"$first": "$teacher_name"},
            # "cases": {"$push": "$enter_time"},  # 单子的日期
            "all_case": {"$sum": 1},  # 总单子数
            "win_case": {"$sum": {"$cond": {"if": {"$gte": ["$the_profit", 0]}, "then": 1, "else": 0}}},  # 胜单
            "sum_profit": {"$sum": "$the_profit"},
            "sum_lots": {"$sum": "$lots"}
        }
        pipeline.append({"$group": group})
        add_field = {
            "avg_profit": {"$divide": ["$sum_profit", "$sum_lots"]},
            "win_per": {"$divide": ["$win_case", "$all_case"]}
        }
        pipeline.append({"$addFields": add_field})
        pipeline.append({"$sort": {"_id": 1}})
        res = ses.aggregate(pipeline=pipeline)
        res = [x for x in res]
        return res

    @classmethod
    def direction_map(cls, include_raw: bool = True) -> dict:
        """
        获取以方向为key,老师的doc的list为val的字典.
        用于在生成虚拟信号的时候提供随机特性
        : param include_raw: 是否包含原生的方向.
        :return:
        """
        f = {"create_date": {"$gt": mongo_db.get_datetime_from_str("2018-9-3 0:0:0")}}
        ts = Teacher.find(filter_dict=f)
        t_dict = dict()  # 方向和老师的字典
        for t in ts:
            d = t.get("direction")
            if include_raw:
                if d is not None:
                    if d in t_dict:
                        t_dict[d].append(t)
                    else:
                        t_dict[d] = [t]
            else:
                if d is not None and d != "raw":
                    if d in t_dict:
                        t_dict[d].append(t)
                    else:
                        t_dict[d] = [t]
        return t_dict

    @classmethod
    def trade_history(cls, t_id: ObjectId, filter_dict: dict, page_size: int = 50, can_json: bool = False) -> list:
        """
        分页查询喊单历史(已离场的)
        :param t_id:  老师id
        :param filter_dict:  查询条件字典,
        :param page_size:  一页有多少条记录?
        :param can_json:
        :return:
        """
        filter_dict["teacher_id"] = t_id
        filter_dict["case_type"] = "exit"
        sort_list = [("exit_time", -1)]
        projection = ['_id', 'exit_time', 'product', 'direction', 'enter_price', 'exit_price', 'lots', 'each_profit']
        ses = mongo_db.get_conn(table_name="trade")
        args = {
            "filter": filter_dict,
            "sort": sort_list,  # 可能是None,但是没问题.
            "projection": projection,
            "limit": page_size
        }
        args = {k: v for k, v in args.items() if v is not None}
        """开始查询页面"""
        res = list()
        r = ses.find(**args)
        if r is None:
            pass
        else:
            if r.count() > 0:
                if can_json:
                    res = [mongo_db.to_flat_dict(x) for x in r]
                else:
                    res = [x for x in r]
            else:
                pass
        return res

    @classmethod
    def win_and_bar(cls, t_id: (str, ObjectId) = None) -> list:
        """
        查询老师的,状图表数据并统计获胜场次. 2018-9-17
        分组标志: 月份+老师id
        排序 老师Id正序, 月份正序
        :param t_id:
        :return:
        """
        a_list = win_and_bar(t_id)
        a_list = [{
            't_id': str(x['_id']['t_id']),
            'date': x['_id']['date'].strftime("%y/%m"),
            "win": x['win'],
            "count": x['count'],
            'per': round((x['win'] / x['count']) * 100, 1) if x['count'] else 0
        } for x in a_list]  # 添加每月胜率
        return a_list

    @classmethod
    def selector_data(cls, project: list = None) -> list:
        """
        获取老师的选择器对象,包含虚拟老师
        :return:
        """
        # f = {"native": True, "direction": {"$exists": False}}
        f = {
            "invalid": {"$exists": False},
            # "hide": {"$exists": False}
        }
        p = ["_id", "name"] if project is None else project
        r = cls.find(filter_dict=f, projection=p)
        resp = [x for x in r]
        return resp

    @classmethod
    def re_calculate(cls, ids: list = None) -> dict:
        """
        重新计算老师的胜率,盈利率
        :param ids: 老师的id,ObjectId的数组
        :return:
        """
        if ids is None or len(ids) == 0:
            ids = [x['_id'] for x in Teacher.selector_data(project=['_id'])]
        else:
            pass
        """所有交易的起始时间以此为准"""
        begin = mongo_db.get_datetime_from_str("2018-7-1")
        pipeline = []
        m = {"$match": {
            "teacher_id": {"$in": ids},
            "case_type": {"$exists": True},
            "enter_time": {"$exists": True, "$gt": begin}
        }}
        pipeline.append(m)
        g = {
            "$group":
                {
                    "_id": "$teacher_id",
                    "case_count": {"$sum": 1},
                    "win_count":
                        {
                            "$sum":
                                {
                                    "$cond":
                                        {
                                            "if": {"$gte": ["$the_profit", 0]},
                                            "then": 1,
                                            "else": 0
                                        }
                                }

                        },
                    "profit_amount":
                        {
                            "$sum": "$the_profit"
                        }
                }
        }
        pipeline.append(g)
        col = mongo_db.get_conn(table_name="trade")
        r = col.aggregate(pipeline=pipeline)
        r = [x for x in r]
        resp = {
            x['_id']:
                {
                    "case_count": x.get('case_count', 0),   # 喊单总计
                    "win_count": round(x.get('win_count', 0), 2),       # 胜场统计
                    "profit_amount": x.get('profit_amount', 0),  # 盈利累加
                 }
            for x in r}
        f = {"_id": {"$in": ids}}
        projection = ["_id", "deposit_amount"]
        deposit_amounts = {x['_id']: x['deposit_amount'] for x in cls.find(filter_dict=f, projection=projection)}
        for _id, item in resp.items():
            """计算盈利率"""
            deposit_amount = deposit_amounts.get(_id, 0)
            if deposit_amount == 0:
                profit_ratio = 0
            else:
                profit_ratio = round((item.get("profit_amount", 0) / deposit_amount * 100), 2)
            item['profit_ratio'] = profit_ratio
            """计算胜率"""
            total = item.get("case_count", 0)
            if total == 0:
                win_ratio = 0
            else:
                win_ratio = item.get("win_count", 0) / total
            item['win_ratio'] = win_ratio
            f = {"_id": _id}
            u = {"$set": item}
            cls.find_one_and_update(filter_dict=f, update_dict=u, upsert=False)
        return resp


if __name__ == "__main__":
    """查询单个老师的持仓记录"""
    # print(Teacher.count(filter_dict={}))
    # ids = [ObjectId("5bbd3279c5aee8250bbe17d0")]
    # print(Teacher.single_info2(ObjectId("5b8c5451dbea62189b5c28eb")))
    Teacher.re_calculate()
    # Teacher.index()
    pass
