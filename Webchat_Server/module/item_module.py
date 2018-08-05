# -*- coding: utf-8 -*-
import os
import sys
__project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_path not in sys.path:
    sys.path.append(__project_path)
import mongo_db
import datetime
from log_module import get_logger
from uuid import uuid4
from werkzeug.contrib.cache import SimpleCache
from module.pickle_data import calculate_win_per_by_teacher_mix


ObjectId = mongo_db.ObjectId
logger = get_logger()
simple_cache = SimpleCache()


class RawWebChatMessage(mongo_db.BaseDoc):
    """
    原始微信的记录
    """
    _table_name = "raw_webchat_message"
    type_dict = dict()
    type_dict['_id'] = ObjectId


class TeacherRank(mongo_db.BaseDoc):
    """
    老师排行榜记录
    包括
    1. 按type ， 胜率， 盈利率 （目前只计算胜率）
    2. 按照计算周期  week
    """
    _table_name = "teacher_rank"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['rank'] = list  # 排行榜[{"t_id": _id, "win": win},...]
    type_dict['year'] = int  # 年
    type_dict['week'] = int  # 一年中的第几周
    type_dict['begin'] = datetime.datetime  # 排行开始日期，主要查询条件
    type_dict['end'] = datetime.datetime  # 排行结束日期，主要查询条件
    type_dict['time'] = datetime.datetime  # 创建时间

    @classmethod
    def get_rank(cls, cur_time: datetime.datetime, prev_week: int = 1, re_build: bool = False) -> dict:
        """
        根据日期，返回日期所在的周（或者往前推几周）的排行字典,请调用此函数,有缓存
        :param cur_time:
        :param prev_week:往前提前几周？默认是1,也就是上一周的排行，0就是取本周的排行
        :param re_build:强制重新生成排行榜?
        :return:{t_id: {"rank": rank, "win": win},...}
        """
        y, w, d = cur_time.isocalendar()  # 年, 全年的第几周? 这天是星期几?
        key = "week_rank_{}_{}_{}".format(y, w, prev_week)
        res = simple_cache.get(key)
        if res is None or re_build:
            res = cls._get_rank(cur_time=cur_time, prev_week=prev_week, re_build=re_build)
            simple_cache.set(key=key, value=res, timeout=3600)
        return res

    @classmethod
    def _get_rank(cls, cur_time: datetime.datetime, prev_week: int = 1, re_build: bool = False) -> dict:
        """
        根据日期，返回日期所在的周（或者往前推几周）的排行字典,底层函数,无缓存
        :param cur_time:
        :param prev_week:往前提前几周？默认是1,也就是上一周的排行，0就是取本周的排行
        :param re_build:强制重新生成排行榜?
        :return:{t_id: {"rank": rank, "win": win},...}
        """
        the_time = cur_time - datetime.timedelta(days=7 * prev_week)
        y, w, d = the_time.isocalendar()  # 年, 全年的第几周? 这天是星期几?
        f = {"year": y, "week": w}
        res = cls.find_one_plus(filter_dict=f, instance=False)
        if res is None or re_build:
            """没有查到/强行重新生成,生成一个新的记录"""
            begin = mongo_db.get_datetime_from_str("{}".format((the_time - datetime.timedelta(days=d - 1)).strftime("%F")))
            end = mongo_db.get_datetime_from_str("{} 23:59:59.999999".format((the_time + datetime.timedelta(days=(7 - d))).strftime("%F")))
            rank_dict = calculate_win_per_by_teacher_mix(begin, end)
            """
            {
                ObjectId('5a1e680642f8c1bffc5dbd69'): {'win': 50.0, 'count': 8}, 
                ObjectId('5a1e680642f8c1bffc5dbd6f'): {'win': 75.0, 'count': 16}, 
                ObjectId('5b4c01fffd259807ff92ad65'): {'win': 66.7, 'count': 15}
            }
            """
            rank = [{"t_id": k, "win": v['win']} for k, v in rank_dict.items()]
            rank.sort(key=lambda obj: obj['win'], reverse=True)
            u = {"$set": {"begin": begin, "end": end, "time": datetime.datetime.now(), "rank": rank}}
            res = cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)
        else:
            pass
        return res


class Score(mongo_db.BaseDoc):
    """
    对用户积分的操作(记录）
    对用户的积分操作类型分多种：
    1. init  初始化 初始化用户积分 0
    2. bind_phone  绑定手机  +100
    3. add  增加积分 增加积分有多种原因 ，比如加金，或者交易
    4. follow 跟单  减少积分 跟单减少积分的规则如下：
        1. 以周为计量单位
        2. 周第一 -500, 第二 -300, 第三-200, 第四第五-100， >6 -50
    5. reduce 减少积分    减少积分有多种原因 ，一般是手动操作。
    """
    _table_name = "score_record"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_id'] = ObjectId
    type_dict['type'] = str  # init/bind_phone/add/follow/reduce 查询时用来区别类型
    type_dict['num'] = int  # 增减积分的数量，有单位
    type_dict['desc'] = str  # 增减积分的原因/备注
    type_dict['time'] = datetime.datetime

    @classmethod
    def instance(cls, **kwargs):
        """
        推荐的从参数获取实例的方法
        :param kwargs:
        :return:
        """
        num = kwargs['num']
        if isinstance(num, int):
            pass
        elif isinstance(num, float):
            kwargs['num'] = int(num)
        elif isinstance(num, str) and num.isdigit():
            kwargs['num'] = int(num)
        else:
            ms = "错误的num:{}".format(num)
            logger.exception(msg=ms)
            raise ValueError(ms)
        user_id = kwargs.get('user_id')
        if isinstance(user_id, ObjectId):
            pass
        elif isinstance(user_id, str) and len(user_id) == 24:
            kwargs['user_id'] = ObjectId(user_id)
        else:
            ms = "错误的user_id:{}".format(user_id)
            logger.exception(msg=ms)
            raise ValueError(ms)
        t = kwargs.get('time')
        if t is None:
            kwargs['time'] = datetime.datetime.now()
        elif isinstance(t, str):
            t = mongo_db.get_datetime_from_str(t)
            kwargs['time'] = t if t else datetime.datetime.now()
        else:
            ms = "错误的time:{}".format(t)
            logger.exception(msg=ms)
            raise ValueError(ms)
        return cls(**kwargs)

    @classmethod
    def add_num(cls, u_id: (str, ObjectId), num: int) -> bool:
        """
        加分 未完成
        :param u_id:
        :param num:
        :return:
        """
        user = WXUser.find_by_id(o_id=u_id, to_dict=True)


    @classmethod
    def re_calculate(cls, u_id: (str, ObjectId) = None, u_dict: dict = None) -> int:
        """
        重新计算用户积分并写入记录。会逐一检查用户的积分记录,重新初始化用户积分的时候使用
        1. 补齐缺少的积分增减记录
        2. 计算相关的的记录的积分
        3. 返回最后的分值，
        :param u_id:
        :param u_dict:
        :return:
        """
        user_dict = u_dict if isinstance(u_dict, dict) and "_id" in u_dict else \
            WXUser.find_by_id(o_id=u_id, to_dict=True)
        if isinstance(user_dict, dict) and "_id" in user_dict:
            user_id = user_dict['_id']
            """重新计算历史积分"""
            f = {"user_id": user_id}
            s = {"time": -1}
            rs = cls.find_plus(filter_dict=f, sort_dict=s, to_dict=True)
            score = 0
            inserts = list()
            init = False  # 初始化过？
            bind_phone = False  # 绑定手机过？
            for x in rs:
                score += x.get("num", 0)
                if x['type'] == "init":
                    init = True
                elif x['type'] == 'bind_phone':
                    bind_phone = True
                else:
                    score += x['num']
            now = datetime.datetime.now()
            if not init:
                temp = {
                    "type": "init", "num": 0, "user_id": user_id,
                    "desc": "用户初始化", "time": now
                }
                inserts.append(temp)
            if not bind_phone:
                score += 1000
                temp = {
                    "type": "bind_phone", "num": 100, "user_id": user_id,
                    "desc": "绑定手机", "time": now
                }
                inserts.append(temp)
            else:
                pass
            """事务,开始添加扣分记录和更新用户积分"""
            client = mongo_db.get_client()
            t1 = client[mongo_db.db_name][cls.get_table_name()]
            t2 = client[mongo_db.db_name][WXUser.get_table_name()]
            with client.start_session(causal_consistency=True) as ses:
                with ses.start_transaction():
                    t1.insert_many(documents=inserts, session=ses)
                    f = {"_id": user_id}
                    u = {"$set": {"score": score}}
                    t2.find_one_and_update(filter=f, update=u, upsert=False, session=ses)
            return score
        else:
            ms = "无效的用户! u_id:{}, u_dict: {}".format(u_id, user_dict)
            logger.exception(msg=ms)
            raise ValueError(ms)

    @classmethod
    def every_week_mon_check(cls) -> list:
        """
        每个星期一,对本周还在关注老师的用户进行扣分.(先扣分),生产环境下,这是给celery的定时任务使用的
        :return: 操作情况的数组  [{"_id": user_id, "num":-500, "follow": True },...]
        """
        res = list()
        f = {"follow.0": {"$exists": True}}  # 有关注老师的用户
        p = ['_id', "follow", 'score']
        us = WXUser.find_plus(filter_dict=f, projection=p, to_dict=True)
        now = datetime.datetime.now()
        rank = TeacherRank.get_rank(cur_time=now)
        """扣分:上周排行第一 -500, 第二 -300, 第三-200, 第四第五-100， >6 -50"""
        num_dict = {0: -500, 1: -300, 2: -200, 3: -100, 4: -100}
        rank_dict = dict()
        for i, x in enumerate(rank):
            rank_dict[x['_id']] = {"index": i, "num": num_dict[i]}
        for x in us:
            u_id = x['_id']
            f_id = x.get("follow", list())
            f_id = None if len(f_id) == 0 else f_id[0]
            score = x.get("score")
            if score is None:
                score = cls.re_calculate(u_dict=x)
            if f_id in rank:
                """关注的老师在上周的排行榜内"""
                s = rank_dict[f_id]
                num = s['num']
                if score >= abs(num):
                    """积分够本周扣分"""
                    score += num
                    temp = {
                        "type": "follow", "num": num, "user_id": u_id,
                        "desc": "跟随老师 {}, 排名: {}".format(f_id, s['index'] + 1),
                        "time": now
                    }
                    """事务,添加一条扣分记录,并修改用户积分"""
                    client = mongo_db.get_client()
                    t1 = client[mongo_db.db_name][cls.get_table_name()]
                    t2 = client[mongo_db.db_name][WXUser.get_table_name()]
                    with client.start_session(causal_consistency=True) as ses:
                        with ses.start_transaction():
                            t1.insert_one(document=temp, session=ses)
                            f = {"_id": u_id}
                            u = {"$set": {"score": score}}
                            r = t2.find_one_and_update(filter=f, update=u, upsert=False, session=ses)
                            if r is None:
                                ms = "用户:{} 关注扣分失败".format(u_id)
                                print(ms)
                                logger.exception(msg=ms)
                                res.append({"_id": u_id, "error": ms})
                            else:
                                res.append({"_id": u_id, "num": num, "follow": True})
                else:
                    """积分不够扣分的,直接解除关注就行了"""
                    f = {"_id": u_id}
                    u = {"$set": {"follow": []}}
                    r = WXUser.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=False)
                    if r is None:
                        ms = "用户:{} 解除关注失败".format(u_id)
                        print(ms)
                        logger.exception(msg=ms)
                        res.append({"_id": u_id, "error": ms})
                    else:
                        res.append({"_id": u_id, "num": 0, "follow": False})
        return res


class WXUser(mongo_db.BaseDoc):
    """从微信接口获取的用户身份信息,目前的用户是测试"""
    _table_name = "wx_user"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['nick_name'] = str
    type_dict['phone'] = str
    type_dict['mt4_account'] = str
    type_dict['sex'] = int
    type_dict['score'] = float  # 积分
    type_dict['follow'] = list  # 关注的老师，是ObjectId的列表，不用DBRef的目的是简化$nslookup查询
    type_dict['openid'] = str
    type_dict['unionid'] = str
    type_dict['country'] = str  # 国家
    type_dict['province'] = str  # 省份
    type_dict['city'] = str
    type_dict['head_img_url'] = str  # 头像地址
    type_dict['subscribe'] = int   # 是否已关注本微信号
    type_dict['subscribe_scene'] = str   # 用户关注的渠道来源
    type_dict['subscribe_time'] = datetime.datetime   # 用户关注的时间
    type_dict['access_token'] = str  # 访问access_token
    type_dict['expires_in'] = int  # access_token的过期时间
    type_dict['time'] = datetime.datetime  # access_token的获取时间
    type_dict['refresh_token'] = str  # access_token的refresh_token

    def __init__(self, **kwargs):
        nick_name = kwargs.pop("nickname", "")
        if nick_name != "":
            kwargs['nick_name'] = nick_name
        head_img_url = kwargs.pop("headimgurl", "")
        if head_img_url != "":
            kwargs['head_img_url'] = head_img_url
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(WXUser, self).__init__(**kwargs)

    @classmethod
    def instance(cls, **raw_dict):
        """
        当微信用户登录时,获取用户信息的字典并创建一个对象.
        :param raw_dict:
        :return:
        """
        subscribe_time = raw_dict.pop("subscribe_time", None)
        if isinstance(subscribe_time, (int, float)):
            raw_dict['subscribe_time'] = datetime.datetime.fromtimestamp(subscribe_time)
        elif isinstance(subscribe_time, str) and subscribe_time.isdigit():
            raw_dict['subscribe_time'] = datetime.datetime.fromtimestamp(int(subscribe_time))
        else:
            pass
        return cls(**raw_dict)

    @classmethod
    def wx_login(cls, **info_dict: dict) -> dict:
        """
        微信用户登录,如果是新用户,那就创建,否则,那就修改.
        :param info_dict:
        :return:
        """
        openid = info_dict.pop("openid")
        res = None
        if openid is None:
            pass
        else:
            f = {"openid": openid}
            init = cls.instance(**info_dict)
            init = init.get_dict(ignore=['_id', "openid"])
            u = {"$set": init}
            res = cls.find_one_and_update_plus(filter_dict=f, update_dict=u, upsert=True)
        return res

    @classmethod
    def un_follow(cls, user_id: (str, ObjectId)) -> dict:
        """
        取消跟踪老师
        :param user_id:
        :return:
        """
        mes = {"message": "取消跟踪失败"}
        user = cls.find_by_id(o_id=user_id, to_dict=True)
        if isinstance(user, dict):
            f = {"_id": user['_id']}
            u = {"$set": {"follow": []}}
            r = cls.find_one_and_update_plus(filter_dict=f, upsert=False, update_dict=u)
            if r is None:
                mes['message'] = "保存数据失败"
            else:
                mes['message'] = "success"
        else:
            ms = "错误的用户id: {}".format(user_id)
            logger.exception(msg=ms)
            print(ms)
            mes['message'] = "用户id错误"

    @classmethod
    def follow(cls, user_id: (str, ObjectId), t_id: (str, ObjectId)) -> dict:
        """
        用户跟单行为。
        1. 如果用户积分不足，那就不能跟单
        2. 如果用户已经跟随了一位老师，那就换人。同时扣分
        :param user_id:
        :param t_id: 老师id
        :return:
        """
        """计算是否需要扣除跟单积分"""
        user = cls.find_by_id(o_id=user_id, to_dict=True)
        if isinstance(user, dict):
            user_id = user['_id']
            score = user.get("score", None)
            if score is None:
                score = Score.re_calculate(u_dict=user)
            f_id = ObjectId(t_id) if isinstance(t_id, str) and len(t_id) == 24 else t_id
            now = datetime.datetime.now()
            res = {"message": "关注失败"}
            """
            跟单扣分制度:
            参考上一周的老师胜率排行榜
            第一 -500, 第二 -300, 第三-200, 第四第五-100， >6 -50
            """
            num_dict = {0: -500, 1: -300, 2: -200, 3: -100, 4: -100}
            ses = mongo_db.get_conn(table_name="teacher")
            f = dict()
            s = [("win_ratio", -1)]
            p = ['_id', "win_ratio"]
            rank = ses.find(filter=f, sort=s, projection=p)
            rank = {x['_id']: {"index": i + 1, "num": num_dict.get(i, -50)} for i, x in enumerate(rank)}
            x = rank[f_id]
            num = x['num']
            i = x['index']
            if score >= abs(num):
                score += num
                temp = {
                    "type": "follow", "num": num, "user_id": user_id,
                    "desc": "跟随老师 {}, 排名: {}".format(t_id, i),
                    "time": now
                }
                """事务,开始添加扣分记录和更新用户积分"""
                client = mongo_db.get_client()
                t1 = client[mongo_db.db_name][Score.get_table_name()]
                t2 = client[mongo_db.db_name][WXUser.get_table_name()]
                t3 = client[mongo_db.db_name][FollowRecord.get_table_name()]
                with client.start_session(causal_consistency=True) as ses:
                    with ses.start_transaction():
                        t1.insert_one(document=temp, session=ses)
                        f = {"_id": user_id}
                        u = {"$set": {"score": score, "follow": [f_id]}}
                        t2.find_one_and_update(filter=f, update=u, upsert=False, session=ses)
                        """
                        检查用户以前是否有跟踪老师？
                        检查的方式是：检查用户的follow记录。如果有，更新再新建。没有，新建。
                        """
                        follow = user.get("follow", dict())
                        if len(follow) == 0:
                            """没有跟随过老师"""
                            pass
                        else:
                            """有跟随过老师，需要先终结以前的跟随关系。"""
                            f2 = {"user_id": user_id, "t_id": f_id}
                            u2 = {"$set": {"end": now}}
                            t3.find_one_and_update(filter=f2, update=u2, upsert=False, session=ses)
                        """添加一条跟随老师的记录"""
                        temp = {
                            "_id": ObjectId(),
                            "user_id": user_id,
                            "t_id": f_id,
                            "begin": now
                        }
                        t3.insert_one(document=temp, session=ses)
                        res['message'] = "success"
            else:
                res['message'] = "积分不足"
            return res
        else:
            ms = "错误的user_id: {}".format(user_id)
            logger.exception(msg=ms)
            raise ValueError(ms)

    @classmethod
    def check_score(cls, user_id: (str, ObjectId)) -> int:
        """
        检查用户的积分，对其进行重新计算。
        :param user_id:
        :return: 返回积分
        """
        return Score.re_calculate(u_id=user_id)

    @classmethod
    def hold_level(cls, user_id: (str, ObjectId), t_id: (str, ObjectId) = None) -> dict:
        """
        计算某个用户查看指定老师持仓的级别。返回int。
        1. -1 无法查看， 一般是未绑定手机的用户
        2. 0  只能查看是否有持仓和持仓数量。 一般是绑定手机用户查看非follow的老师状态
        3. 1   可以查看持仓详情。 处于follow状态的老师。
        :param user_id:
        :param t_id:
        :return:
        """
        mes = {"message": "未知的错误", "level": -1}
        user = cls.find_by_id(o_id=user_id, to_dict=True)
        if isinstance(user, dict):
            phone = user['phone']
            mes['message'] = "success"
            if isinstance(phone, str) and len(phone) == 11:
                mes['level'] = 0
                follow = user.get("follow", list())
                if len(follow) == 0:
                    pass
                else:
                    f_id = follow[0]
                    t_id = ObjectId(t_id)if isinstance(t_id, str) and len(t_id) == 24 else t_id
                    if f_id == t_id:
                        mes['level'] = 1
                    else:
                        pass
            else:
                mes['level'] = -1
        else:
            ms = "错误的user_id: {}".format(user_id)
            mes['message'] = ms
            logger.exception(msg=ms)
            print(ms)
        return mes


class FollowRecord(mongo_db.BaseDoc):
    """
    用户跟踪老师的记录
    """
    _table_name = "follow_record"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['user_id'] = ObjectId
    type_dict['t_id'] = ObjectId
    type_dict['begin'] = datetime.datetime
    type_dict['end'] = datetime.datetime



if __name__ == "__main__":
    # Score.every_week_mon_check()
    WXUser.follow(ObjectId("5b57a770f313841fc0effef7"), "5b65f2d9dbea625d78469f1b")
    pass