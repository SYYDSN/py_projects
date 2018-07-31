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


ObjectId = mongo_db.ObjectId
logger = get_logger()


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
    type_dict['rank'] = int  # 排位
    type_dict['win'] = float  # 胜率
    type_dict['t_id'] = ObjectId  # 老师id
    type_dict['t_name'] = str  # 老师名字
    type_dict['year'] = int  # 年
    type_dict['week'] = int  # 一年中的第几周
    type_dict['begin'] = datetime.datetime  # 排行开始日期，主要查询条件
    type_dict['end'] = datetime.datetime  # 排行结束日期，主要查询条件
    type_dict['time'] = datetime.datetime  # 创建时间

    @classmethod
    def get_rank(cls, cur_time: datetime.datetime, prev_week: int = 1) -> dict:
        """
        根据日期，返回日期所在的周（或者往前推几周）的排行字典
        :param cur_time:
        :param prev_week:往前提前几周？默认是1,也就是上一周的排行，0就是取本周的排行
        :return:{t_id: {"rank": rank, "win": win},...}
        """
        the_time = cur_time - datetime.timedelta(days=7 * prev_week)
        wd = the_time.weekday()



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
    def calculate(cls, u_id: (str, ObjectId) = None, u_dict: dict = None, re_begin: bool = False) -> int:
        """
        计算用户积分并写入记录。会逐一检查用户的积分记录：
        1. 补齐缺少的积分增减记录
        2. 检查follow积分并追加记录
        3. 返回最后的分值，
        :param u_id:
        :param u_dict:
        :param re_begin:
        :return:
        """
        user_dict = u_dict if isinstance(u_dict, dict) and "_id" in u_dict else \
            WXUser.find_by_id(o_id=u_id, to_dict=True)
        if isinstance(user_dict, dict) and "_id" in user_dict:
            score = user_dict.get("score", None)
            user_id = user_dict['_id']
            need_init = False  # 是否需要从头计算积分？
            if isinstance(score, (int, float)) and not re_begin:
                pass
            else:
                need_init = True
            inserts = list()  # 需要追加的记录
            if need_init:
                """重新计算历史积分"""
                f = {"user_id": user_id}
                s = {"time": -1}
                rs = cls.find_plus(filter_dict=f, sort_dict=s, to_dict=True)
                rd = dict()
                score = 0
                init = False  # 初始化过？
                bind_phone = False  # 绑定手机过？
                for x in rs:
                    score += x.get("num", 0)
                    if x['type'] == "init":
                        init = True
                    elif x['type'] == 'bind_phone':
                        bind_phone = True
                    else:
                        pass
                now = datetime.datetime.now()
                if init:
                    temp = {
                        "type": "init", "num": 0, "user_id": user_id,
                        "desc": "用户初始化", "time": now
                    }
                    inserts.append(temp)
                if bind_phone:
                    temp = {
                        "type": "bind_phone", "num": 100, "user_id": user_id,
                        "desc": "绑定手机", "time": now
                    }
                    inserts.append(temp)
            else:
                pass
            """计算是否需要扣除跟单积分"""


        else:
            ms = "无效的用户! u_id:{}, u_dict: {}".format(u_id, user_dict)
            logger.exception(msg=ms)
            raise ValueError(ms)


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
    def follow(cls, user_id: (str, ObjectId), t_id: (str, ObjectId)) -> bool:
        """
        用户跟单行为。
        1. 如果用户积分不足，那就不能跟单
        2. 如果用户已经跟随了一位老师，那就换人。
        目前还不允许取消跟单。
        :param user_id:
        :param t_id: 老师id
        :return:
        """

    @classmethod
    def check_score(cls, user_id: (str, ObjectId)) -> None:
        """
        检查用户的积分，对其进行计算。
        :param user_id:
        :return:
        """

    @classmethod
    def hold_level(cls, user_id: (str, ObjectId), t_id: (str, ObjectId)) -> int:
        """
        计算某个用户查看指定老师持仓的级别。返回int。
        1. -1 无法查看， 一般是未绑定手机的用户
        2. 0  只能查看是否有持仓和持仓数量。 一般是绑定手机用户查看非follow的老师状态
        3. 1   可以查看持仓详情。 积分满足最低要求的，处于follow状态的老师。
        :param user_id:
        :param t_id:
        :return: 老师id
        """