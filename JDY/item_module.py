#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.realpath(__file__))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
import mongo_db
from log_module import get_logger
from celery_module import to_jiandao_cloud_and_send_mail
from werkzeug.contrib.cache import SimpleCache
import datetime
from browser.firefox_module import to_jiandao_cloud
from module.send_module import send_signal
from module.spread_module import SpreadChannel
from celery_module import send_reg_info_celery
from celery_module import send_reg_info_celery2
# from module.jdy_module import RegisterLog


"""基本模型模块"""


logger = get_logger()
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
cache = SimpleCache()


def transform_time_zone(a_time) -> datetime.datetime:
    """
    转换时区，把时间+8个小时
    :param a_time:
    :return:
    """
    return a_time + datetime.timedelta(hours=8)  # 调整时区


class CsrfError(mongo_db.BaseDoc):
    """csrf错误记录"""
    _table_name = "csrf_error_info"
    type_dict = dict()
    type_dict['_id'] = mongo_db.ObjectId  # id,唯一
    type_dict['page_url'] = str  # 原始注册链接地址
    type_dict['host_url'] = str  # 链接地址
    type_dict['base_url'] = str  # 基础url
    type_dict['referrer'] = str  # referrer
    type_dict['user_agent'] = str  # 浏览器信息
    type_dict['args'] = dict  # 参数字典
    type_dict['client_ip'] = str  # 客户端ip
    type_dict['reason'] = str  # 错误原因
    type_dict['time'] = datetime.datetime  # 时间


class Customer(mongo_db.BaseDoc):
    """客户表"""
    _table_name = "customer_info"
    type_dict = dict()
    type_dict["_id"] = mongo_db.ObjectId  # id 唯一
    type_dict['user_name'] = str    # 用户名 ,为空的话,默认手机号码
    type_dict['nick_name'] = str    # 昵称
    type_dict['real_name'] = str    # 真实姓名
    type_dict['phone'] = list    # 手机,用户可能有多个手机 CustomerExtendInfo实例的数组
    type_dict['qq'] = list    # qq ,CustomerExtendInfo实例的数组
    type_dict['wx'] = list    # wx  CustomerExtendInfo实例的数组
    type_dict['email'] = list    # email  CustomerExtendInfo实例的数组
    type_dict['description'] = str    # 注册时的备注
    type_dict['search_keyword'] = str    # 注册时的搜索关键词
    type_dict['host_url'] = str    # 注册地址,不包含参数
    type_dict['base_url'] = str    # 注册地址,包含参数
    type_dict['referrer'] = str    # referrer
    type_dict['user_agent'] = str    # user_agent
    type_dict['time'] = datetime.datetime  # 注册时间
    type_dict['group_by'] = str        # 分组标志位
    type_dict['group_count'] = int        # 当前分组标志的下分配的第几个分组资源？

    @classmethod
    def reg(cls, **kwargs):
        """注册用户,
        1.保存到mongo数据库.
        2.保存到简道云
        """
        message = {"message": "success"}
        reg_dict = kwargs.copy()
        try:
            if "phone" in kwargs:
                phone = kwargs.pop('phone')
                filter_dict = {"phone": {"$all": [phone]}}
                if cls.find_one_plus(filter_dict=filter_dict):
                    raise ValueError("重复的手机号码:{}".format(phone))
                    # kwargs['phone'] = [phone]
                else:
                    kwargs['phone'] = [phone]
            if "qq" in kwargs:
                qq = [kwargs.pop('qq')]
                filter_dict = {"qq": {"$all": [qq]}}
                if cls.find_one_plus(filter_dict=filter_dict):
                    raise ValueError("重复的qq号码:{}".format(qq))
                else:
                    kwargs['qq'] = [qq]
            if "wx" in kwargs:
                wx = [kwargs.pop('wx')]
                filter_dict = {"wx": {"$all": [wx]}}
                if cls.find_one_plus(filter_dict=filter_dict):
                    raise ValueError("重复的微信号码:{}".format(wx))
                else:
                    kwargs['wx'] = [wx]
            if "email" in kwargs:
                email = [kwargs.pop('email')]
                filter_dict = {"email": {"$all": [email]}}
                if cls.find_one_plus(filter_dict=filter_dict):
                    raise ValueError("重复的邮件地址:{}".format(email))
                else:
                    kwargs['email'] = [email]
        except ValueError as e:
            message['message'] = str(e)
            print(e)
        except Exception as e:
            message['message'] = str(e)
            print(e)
            logger.exception(exc_info=True, stack_info=True)
        finally:
            if message['message'] == "success":
                group_by_dict = DistributionScheme.next_group()  # 获取分组标志
                if isinstance(group_by_dict, dict) and "group" in group_by_dict and "count" in group_by_dict:
                    group_by = group_by_dict['group']
                    group_count = group_by_dict['count']
                    kwargs['group_by'] = group_by
                    kwargs['group_count'] = group_count
                    reg_dict['group_by'] = group_by
                    reg_dict['group_count'] = group_count
                else:
                    group_by = ''
                # customer = cls(**kwargs)
                save = None
                try:
                    ses = cls.get_collection()
                    save = ses.insert_one(document=kwargs)  # 调试请关闭
                    # save = ObjectId()  # 调试请开打
                except Exception as e:
                    print(e)
                    ms = str(e)
                    message['message'] = ms
                    logger.exception(exc_info=True, stack_info=True, msg=ms)
                finally:
                    if isinstance(save, ObjectId):
                        """這是應對調試"""
                        inserted_id = save
                    elif hasattr(save, "inserted_id"):
                        inserted_id = save.inserted_id
                    else:
                        inserted_id = None
                    if isinstance(inserted_id, mongo_db.ObjectId):
                        message['user_id'] = str(inserted_id)
                        today_count = cls.today_register_count()
                        reg_dict['today_count'] = today_count
                        """发送到简道云接口"""
                        # RegisterLog.send_reg_info(**reg_dict)
                        send_reg_info_celery2.delay(send_data=reg_dict)
                        """发送到钉钉机器人"""
                        send_data = cls.package_info(reg_dict)
                        ms = "送注册信息到大群, arg={}".format(send_data)
                        logger.info(ms)
                        # cls.send_signal(send_data)   # 发送注册信息到大群. 调试请关闭
                        # send_reg_info_celery.delay(group_by, send_data)  #发送消息到钉钉群,包含分组消息
                        """转发到简道云,2018-10-21暂时停止写简道云,将来使用api代替"""
                        # ms = "用户已保存,开始调用to_jiandao_cloud_and_send_mail, arg={}".format(reg_dict)
                        # logger.info(ms)
                        # to_jiandao_cloud(**reg_dict)  # 调试请开打
                        # to_jiandao_cloud_and_send_mail.delay(**reg_dict)  # 调试请关闭
                        # ms = "用户已发送到简道云, arg={}".format(reg_dict)
                        # logger.info(ms)
                    else:
                        pass
            else:
                pass
        return message

    @classmethod
    def package_info(cls, reg_info: dict) -> dict:
        """
        封装钉钉消息
        :param reg_info:
        :return:
        """
        out_put = dict()
        markdown = dict()
        out_put['msgtype'] = 'markdown'
        markdown['title'] = "注册信息"
        channel_info = SpreadChannel.analysis_url(reg_info.get('page_url'))
        channel_str = ",".join(channel_info)
        d = datetime.datetime.now().strftime(
            "%Y年%m月%d日 %H:%M:%S")
        n = "" if reg_info.get("user_name") is None else reg_info.get("user_name")
        p = "" if reg_info.get("phone") is None else reg_info.get("phone")
        c = 0 if reg_info.get("today_count") is None else reg_info.get("today_count")
        keywords = reg_info.get("search_keyword", "")
        title = "用户注册"
        markdown['title'] = title
        markdown[
            'text'] = "#### {}  \n > {}  \n > 注册通道：{}  \n > 搜索关键词： {}  \n > 用户姓名：{}  \n > 手机号码:{}  \n > 分组：{}  \n > 计数：{}/{}". \
            format(title, d, channel_str, keywords, n, p, reg_info['group_by'], reg_info['group_count'] + 1, c)
        out_put['markdown'] = markdown
        out_put['at'] = {'atMobiles': [], 'isAtAll': False}
        return out_put

    @classmethod
    def send_signal(cls, send_data: dict):
        """
        发送注册信息到钉钉机器人的消息服务器, 大群
        :param send_data: 包装好的钉钉消息字典
        :return:
        """
        token_name = "推广助手"
        # out_put = dict()
        # markdown = dict()
        # out_put['msgtype'] = 'markdown'
        # markdown['title'] = "注册信息"
        # channel_info = SpreadChannel.analysis_url(reg_info.get('page_url'))
        # channel_str = ",".join(channel_info)
        # d = datetime.datetime.now().strftime(
        #     "%Y年%m月%d日 %H:%M:%S")
        # n = "" if reg_info.get("user_name") is None else reg_info.get("user_name")
        # p = "" if reg_info.get("phone") is None else reg_info.get("phone")
        # c = 0 if reg_info.get("today_count") is None else reg_info.get("today_count")
        # keywords = reg_info.get("search_keyword", "")
        # title = "用户注册"
        # markdown['title'] = title
        # markdown['text'] = "#### {}  \n > {}  \n > 注册通道：{}  \n > 搜索关键词： {}  \n > 用户姓名：{}  \n > 手机号码:{}  \n > 分组：{}  \n > 计数：{}/{}".\
        #     format(title, d, channel_str, keywords, n, p, reg_info['group_by'], reg_info['group_count'] + 1, c)
        # out_put['markdown'] = markdown
        # out_put['at'] = {'atMobiles': [], 'isAtAll': False}
        res = send_signal(send_data, token_name=token_name)
        print(res)

    @classmethod
    def page(cls, _id: str = None,
             begin_date: (str, datetime.datetime) = None, end_date: (str, datetime.datetime) = None,
             index: int = 1, num: int = 20, can_json: bool = True, reverse: bool = True) -> dict:
        """
        分页注册客户记录
        :param _id: 客户id,为空表示所有
        :param begin_date:   开始时间
        :param end_date:   截至时间
        :param index:  页码
        :param can_json:   是否进行can json转换
        :param num:   每页多少条记录
        :param reverse:   是否倒序排列?
        :return: 事件记录的列表和统计组成的dict
        """
        filter_dict = dict()
        if _id is not None:
            filter_dict['_id'] = mongo_db.get_obj_id(_id)
        end_date = datetime.datetime.now() if mongo_db.get_datetime_from_str(end_date) is None else \
            mongo_db.get_datetime_from_str(end_date)
        begin_date = mongo_db.get_datetime_from_str("2010-1-1 0:0:0") if \
            mongo_db.get_datetime_from_str(begin_date) is None else mongo_db.get_datetime_from_str(begin_date)
        filter_dict['time'] = {"$lte": end_date, "$gte": begin_date}
        index = 1 if index is None else index
        skip = (index - 1) * num
        sort_dict = {"time": -1 if reverse else 1}
        count = cls.count(filter_dict=filter_dict)
        res = cls.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, skip=skip, limit=num, to_dict=True)
        if can_json:
            res = [mongo_db.to_flat_dict(x) for x in res]
        data = {"count": count, "data": res}
        return data

    @classmethod
    def today_register_count(cls) -> int:
        """
        以每日早上6点计算，当前的注册用户是本日的第几个用户 ？ 以1开始基数，
        :return:
        """
        key = "today_register_count"
        count_dict = cache.get(key=key)
        """计算查询条件"""
        now = datetime.datetime.now()
        current_hour = now.hour
        if current_hour >= 6:
            days = 0
        else:
            days = 1
        day_str = (now - datetime.timedelta(days=days)).strftime("%F")
        need_query = True
        if count_dict is None:
            pass
        else:
            prev_day_str = count_dict.get("day_str")
            if prev_day_str != day_str:
                pass
            else:
                count = count_dict.get("count")
                if isinstance(count, int):
                    need_query = False
                else:
                    pass
        if need_query:
            begin_str = "{} 06:00:00".format(day_str)
            begin = mongo_db.get_datetime_from_str(begin_str)
            f = {"time": {"$gte": begin}}
            """从数据库查询"""
            r = cls.count(filter_dict=f)
            count = r - 1  # -1 是应为cls.reg方法先保存了用户信息
        else:
            count = count_dict['count']

        count += 1
        new_dict = dict()
        new_dict['day_str'] = day_str
        new_dict['count'] = count
        cache.set(key=key, value=new_dict, timeout=86400)
        return count


class RawSignal(mongo_db.BaseDoc):
    """
    原始信号的记录
    """
    _table_name = "raw_signal_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId


class DistributionScheme(mongo_db.BaseDoc):
        """用户资源分配方案"""
        _table_name = "distribution_scheme_info"
        type_dict = dict()
        type_dict['_id'] = ObjectId  # 这个id使用客户端发过来的id"
        type_dict['groups'] = list   # 分组标志
        """创建时间，也是分配时，计算已分配数量的起点标志"""
        type_dict['create_date'] = datetime.datetime

        @classmethod
        def instance(cls, **kwargs):
            """
            接受信号并生成实例， 这个在接受信号时替代init方法。
            会提前把数据整理成适合init的方式。
            :param kwargs:
            :return:
            """
            pass

        @classmethod
        def next_group(cls) -> (None, str, int):
            """
            获取下一个分配的标志位
            :return:
            """
            gs = cls.last_groups()
            res = None
            if gs is None:
                pass
            else:
                groups = gs['groups']
                the_time = gs['create_date']
                if len(groups) == 0:
                    pass
                else:
                    allotted = cls.get_allotted(the_groups=groups, the_time=the_time)
                    if len(allotted) > 0:
                        temp = list()
                        for x in groups:
                            c = allotted.get(x, 0)
                            temp.append({"group": x, "count": c})
                        temp.sort(key=lambda obj: obj['count'], reverse=False)
                        res = temp[0]
                    else:
                        res = {"group": groups[0], "count": 0}
            return res

        @classmethod
        def last_groups(cls) -> (None, dict):
            """
            获取最新的groups
            :return:
            """
            f = {"groups": {"$exists": True}}
            s = {"create_date": -1}
            r = cls.find_one_plus(filter_dict=f, sort_dict=s, instance=False)
            if r is None:
                return r
            else:
                res = dict()
                res['create_date'] = r['create_date']
                res['groups'] = r['groups']
                return res

        @classmethod
        def get_allotted(cls, the_time: datetime.datetime, the_groups: list) -> dict:
            """
            获取已分配用户的分布情况，。
            返回一个由group,用户计数组成的字典组成的数据，
            :param the_time:
            :param the_groups:
            :return:

            {
             group1: count1,
            group2: count2,
            group3: count3,
            ....
            }
            """
            """
            聚合查询示范
            ses = mongo_db.get_conn(Customer.get_table_name())
            the_groups = [
                '页面标题:MT4交易管家'
            ]
            the_time = datetime.datetime.now()
            pipeline = [
                {"$match": {"description": {"$in": the_groups}, "time": {"$lte": the_time}}},  # 匹配
                {"$group": {"_id": "$description", "count": {"$sum": 1}}}  # 分组统计
            ]
            res = ses.aggregate(pipeline=pipeline)
            res = [{"group": x['_id'], "count": x['count']} for x in res]
            """
            ses = mongo_db.get_conn(Customer.get_table_name())
            pipeline = [
                {"$match": {"group_by": {"$in": the_groups}, "time": {"$gte": the_time}}},  # 匹配
                {"$group": {"_id": "$group_by", "count": {"$sum": 1}}}  # 分组统计
            ]
            res = ses.aggregate(pipeline=pipeline)
            res = {x['_id']: x['count'] for x in res}
            return res


if __name__ == "__main__":
    """注册测试"""
    # for i in range(2):
    #     args = {
    #         "phone": "3{}665103177".format(i)
    #         ,
    #         "user_agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 LBBROWSER",
    #         "description": "页面标题:智能行情交易系统",
    #         "search_keyword": "",
    #         "page_url": "http://touzi.jyschaxun.com/20180314jiaoyi/index.html?channel=bd-pc-qhrj-015848",
    #         "referrer": "https://www.baidu.com/baidu.php?sc.K000000fJeHuq9k1805tenXpjI-L9X01DZ9Gb7mvaucTyhluRm0aVNCfp9KV32wkz2gBOrMZELcrXrWfyZNoXB_pplwGqQqRnKVFuVZ6UNSp84r17q5gSjeLCFYlPO2v4EaHufRdhr58uLhUwKw8dAzH1OpIL10_bavezPY4SPxufMkYi0.7b_iRZmr7O--YwsdnqAaFDAizEuukoenovgpZsUXxXAGh2FP7BSe5W91SzJUQM_oLUr1m_HAeG_lUQr1uzqMQWdQjPakk3tUrkf.U1Y10ZDq1_ieJoQAEJY-nWjQ4_MVYP00TA-W5HD0IjLrkQ8JzSUFeIjf1tQRv0KGUHYznWR0u1ddugK1nfKdpHdBmy-bIykV0ZKGujYY0APGujY3P0KVIjYknjD4g1DsnHIxnW0vn-t1PW0k0AVG5H00TMfqPH630ANGujYkPjnsg1cknjbd0AFG5HcsP7tkPHR0UynqP1c3nWnknWfYg1TzrjTdrjmsn7tzPWb3rjnzP1mvg100TgKGujYs0Z7Wpyfqn0KzuLw9u1Ys0A7B5HKxn0K-ThTqn0KsTjYkPWTLnW6kn1fY0A4vTjYsQW0snj0snj0s0AdYTjYs0AwbUL0qn0KzpWYs0Aw-IWdsmsKhIjYs0ZKC5H00ULnqn0KBI1Yv0A4Y5H00TLCq0ZwdT1Ykn16knjmdP1TknW6knWcYPjDsrfKzug7Y5HDdnWDkrjT3Pj0vP1D0Tv-b5yf4nHTYnW99nj0snHwBmHT0mLPV5HPDnWmdfWfzPWcvrH0vfWT0mynqnfKsUWYs0Z7VIjYs0Z7VT1Ys0ZGY5H00UyPxuMFEUHYsg1Kxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7tsg100TA7Ygvu_myTqn0Kbmv-b5H00ugwGujYVnfK9TLKWm1Ys0ZNspy4Wm1Ys0Z7VuWYkP6KhmLNY5H00uMGC5H00uh7Y5H00XMK_Ignqn0K9uAu_myTqnfK_uhnqn0KWThnqPHbzPs&ck=2223.13.131.233.208.535.523.133&shh=www.baidu.com&sht=56060048_4_pg&us=2.139972.2.0.2.810.0&ie=utf-8&f=1&ch=4&tn=56060048_4_pg&wd=%E6%96%87%E5%8D%8E%E8%B4%A2%E7%BB%8F%20%E9%9A%8F%E8%BA%AB%E8%A1%8C&oq=%E6%96%87%E5%8D%8E%E8%B4%A2%E7%BB%8F&rqlang=cn&rsf=9&rsp=0&usm=1&rs_src=0&bc=110101",
    #         "user_name": "测试人员{}".format(i + 1),
    #         "time": datetime.datetime.now()
    #     }
    #     customer = Customer.reg(**args)
    # do_jobs()
    """测试发送注册信号给机器人服务器"""
    # Customer.send_signal(args)
    """测试注册人数计数系统"""
    # Customer.today_register_count()
    """新建一个分组标准"""
    # scheme_init = {
    #     "_id": "5ac49e8309d20f5e28015c69",
    #     "create_date": datetime.datetime.now(),
    #     "groups": ["1", '2', '3', '6']
    # }
    # scheme = DistributionScheme(**scheme_init)
    # scheme.save_plus()
    """测试分组统计方法"""
    # r = DistributionScheme.next_group()
    # print(r)
    args = {
        # "_id" : ObjectId("5b554a76451353150ce742b6"),
        "search_keyword" : "迅迭 测试",
        "user_name" : "王满石",
        "group_count" : 0,
        "page_url" : "http://qhrj.sxzctec015.cn/20180719gjs/index.html?channel=360A-pc-hqrj-byds",
        "description" : "页面标题:",
        "referrer" : "https://www.so.com/s?ie=utf-8&src=hao_360so_suggest_b&shb=1&hsid=fc569f7380160a98&eci=407b847fad15303c&nlpv=suggest_3.2.2&q=%E5%8D%9A%E5%BC%88%E5%A4%A7%E5%B8%88%E5%AE%98%E7%BD%91%E4%B8%8B%E8%BD%BD",
        "group_by" : "0",
        "phone" :
            "199814237061"
        ,
        "user_agent" : "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
        "time" : "2018-12-12 0:0:0"
    }
    Customer.reg(**args)
    # print(DistributionScheme.next_group())
    pass