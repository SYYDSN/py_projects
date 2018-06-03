#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from log_module import get_logger
from log_module import recode
import re
import time
import datetime
import mongo_db
from module import send_moudle
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver import FirefoxProfile
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import Firefox
from selenium.webdriver import ChromeOptions
from selenium.webdriver import Chrome
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import By
from selenium.webdriver.support.ui import Select
from pyquery import PyQuery
from mongo_db import get_datetime_from_str
from werkzeug.contrib.cache import RedisCache
from module.transaction_module import Transaction
from module.transaction_module import Withdraw
from gevent.queue import JoinableQueue
from mail_module import send_mail


send_signal = send_moudle.send_signal
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
logger = get_logger()
cache = RedisCache()


"""爬虫模块,针对新的平台"""


class IgnoreInvalidRelationCustomer(mongo_db.BaseDoc):
    """被忽略的无效关系的用户,在本类中的对象,无需再发送无效总监归属的警告"""
    _table_name = "ignore_invalid_relation_customer_info"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['mt4_account'] = str
    type_dict['customer_name'] = str
    type_dict['create_date'] = datetime.datetime

    def __init__(self, **kwargs):
        if 'mt4_account' in kwargs:
            mt4_account = kwargs['mt4_account']
            if not isinstance(mt4_account, str):
                mt4_account = str(mt4_account)
                kwargs['mt4_account'] = mt4_account
            else:
                pass
        if "create_date" not in kwargs:
            kwargs['create_date'] = datetime.datetime.now()
        super(IgnoreInvalidRelationCustomer, self).__init__(**kwargs)

    @classmethod
    def include(cls, mt4_account: str, customer_name: str, send_warning: bool = False, auto_insert: bool = False) -> bool:
        """
        检测一个账户是否处于本类的表中.如果存在,表示属于被忽视的用户.
        :param mt4_account:
        :param customer_name:
        :param send_warning: 如果是被忽视的用户,是否发送警告信息?默认不发送
        :param auto_insert: 是否自动把不在表中的被检测的mt4_account加入到表中?默认不加.
        :return: 是否是被忽视的用户? 是被忽视的返回True/不是返回False
        """
        f = dict()
        rs = cls.find_plus(filter_dict=f, projection=['mt4_account'], to_dict=True)
        if len(rs) > 0:
            rs = [x['mt4_account'] for x in rs]
        if mt4_account in rs:
            """是被忽视的用户"""
            res = True
        else:
            res = False
            """检查是否发送警告消息?"""
            if send_warning:
                cls.send_mes(mt4_account, customer_name)  # 这个方法会抛出异常
            else:
                pass
            """检查是否自动加入?"""
            if auto_insert:
                init = {
                    "mt4_account": mt4_account,
                    "customer_name": customer_name
                }
                r = cls.insert_one(**init)
                if isinstance(r, ObjectId):
                    pass
                else:
                    ms = "插入IgnoreInvalidRelationCustomer实例失败,init={}".format(init)
                    logger.exception(ms)
                    raise ValueError(ms)
        return res

    @staticmethod
    def send_mes(mt4_account: str, customer_name: str) -> bool:
        """
        发送无总监归属警告信息
        :param mt4_account:
        :param customer_name:
        :return: 是否发送成功
        """
        mt4_account = str(mt4_account) if not isinstance(mt4_account, str) else mt4_account
        out_put = dict()
        markdown = dict()
        token_name = "财务群钉钉小助手"
        out_put['msgtype'] = 'markdown'
        title = "客户{}没有归属的总监".format(customer_name)
        markdown['title'] = title
        a_time = datetime.datetime.now().strftime("%y年%m月%d日 %H:%M:%S")

        markdown['text'] = "#### {}  \n > MT4帐号：{}   \n > 客户名：{}  \n > 时间： {}".format(
            title, mt4_account, customer_name, a_time
        )
        out_put['markdown'] = markdown
        out_put['at'] = {'atMobiles': [], 'isAtAll': False}
        res = send_signal(out_put, token_name=token_name)
        return res


class CustomerManagerRelation(mongo_db.BaseDoc):
    """客户和客户经理/总监的对应关系类，用来确认客户归属"""
    _table_name = 'customer_manager_relation'
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['record_id'] = str  # 简道云提交过来的_id，仅仅在删除信息的时候做对应的判断。
    type_dict['customer_sn'] = int  # 新平台id
    type_dict['create_date'] = datetime.datetime  # 记录的创建时间
    type_dict['update_date'] = datetime.datetime  # 记录的最近一次修改时间
    type_dict['delete_date'] = datetime.datetime  # 记录的删除时间
    type_dict['mt4_account'] = str         # 唯一，但不建立对应的索引，目的是容错。
    type_dict['platform'] = str   # 平台名称
    type_dict['customer_name'] = str
    type_dict['sales_name'] = str
    type_dict['manager_name'] = str
    type_dict['director_name'] = str  # 总监

    @classmethod
    def get_relation_by_sn(cls, customer_sn: int, customer_name: str) -> dict:
        """
        以新平台sn获取用户关系
        :param customer_sn:
        :param customer_name:
        :return:
        """
        f = {"customer_sn": customer_sn}
        res = dict()
        rs = cls.find_plus(filter_dict=f, to_dict=True)
        if len(rs) == 0:
            f = {"customer_name": customer_name}
            one = cls.find_one_plus(filter_dict=f, instance=False)
            if one is None:
                res['customer_sn'] = customer_sn
                res['customer_name'] = customer_name
                res['mt4_account'] = ''
                res['sales_name'] = ''
                res['manager_name'] = ''
                res['director_name'] = ''
                warn_flag = True  # 是否发送客户无归属信号？
            else:
                res['customer_sn'] = customer_sn
                res['customer_name'] = customer_name
                res['customer_name'] = one['mt4_account']
                res['sales_name'] = '' if one.get('sales_name') is None else one['sales_name']
                res['manager_name'] = '' if one.get('manager_name') is None else one['manager_name']
                director_name = '' if one.get('director_name') is None else one['director_name']
                res['director_name'] = director_name
                warn_flag = True if director_name == "" else False  # 是否发送客户无归属信号？
        else:
            one = rs[0]
            res['customer_sn'] = customer_sn
            res['customer_name'] = customer_name
            res['customer_name'] = one['mt4_account']
            res['sales_name'] = '' if one.get('sales_name') is None else one['sales_name']
            res['manager_name'] = '' if one.get('manager_name') is None else one['manager_name']
            director_name = '' if one.get('director_name') is None else one['director_name']
            res['director_name'] = director_name
            warn_flag = True if director_name == "" else False  # 是否发送客户无归属信号？
        """检查是否有重复的用户"""
        if len(rs) > 1:
            repeat = True
        else:
            repeat = False
        mt4_account = res.get('mt4_account', "")
        if warn_flag and mt4_account != "":
            """本方法检测没有获取到对应的关系,下一步交给IgnoreInvalidRelationCustomer检查是否有必要发送警告信息"""
            sent_flag = IgnoreInvalidRelationCustomer.include(mt4_account=mt4_account, customer_name=customer_name,
                                                              auto_insert=True, send_warning=True)
            if not sent_flag:
                """不是被忽视的用户,已经发送了无归属警告消息"""
                if repeat:
                    """是否发现了多重用户?"""
                    repeat_list = [{"mt4_account": x.get('mt4_account'), "customer_name": x.get("customer_name")} for x
                                   in rs]
                    title = "customer_manager_relation表中有重复的用户"
                    content = "{}".format(repeat_list)
                    send_mail(title=title, content=content)
                else:
                    pass
            else:
                """被忽略的用户"""
                pass
        return res

    @classmethod
    def get_relation(cls, mt4_account: str, customer_name: str) -> dict:
        """
        根据用户的mt4帐号,查询用户的归属关系,
        1. 如果查询到,返回用户的归属字典.
        2. 如果查询不到,返回一个值都为空字符的归属字典,并且.
            1. 如果客户的账户在IgnoreInvalidRelationCustomer对象中,那就不用发送警告消息.
            2. 如果客户的账户不在IgnoreInvalidRelationCustomer对象中,那就发送警告消息
        :param mt4_account:
        :param customer_name:
        :return:
        """
        mt4_account = mt4_account if isinstance(mt4_account, str) else str(mt4_account)
        res = dict()
        res['director_name'] = ''
        res['sales_name'] = ''
        res['manager_name'] = ''
        res['customer_name'] = ''
        f = {
            "mt4_account": mt4_account,
            "delete_date": {"$exists": False}
        }
        s = {"update_date": -1}   # 可能有重复的对象，所以要排序
        rs = cls.find_plus(filter_dict=f, sort_dict=s, to_dict=True, can_json=False)
        if len(rs) == 0:
            warn_flag = True  # 是否发送客户无归属信号？
        else:
            r = rs[0]
            res['customer_name'] = customer_name
            res['sales_name'] = '' if r.get('sales_name') is None else r['sales_name']
            res['manager_name'] = '' if r.get('manager_name') is None else r['manager_name']
            director_name = '' if r.get('director_name') is None else r['director_name']
            res['director_name'] = director_name
            warn_flag = True if director_name == "" else False   # 是否发送客户无归属信号？
        """检查是否有重复的用户"""
        if len(rs) > 1:
            repeat = True
        else:
            repeat = False
        if warn_flag:
            """本方法检测没有获取到对应的关系,下一步交给IgnoreInvalidRelationCustomer检查是否有必要发送警告信息"""
            sent_flag = IgnoreInvalidRelationCustomer.include(mt4_account=mt4_account, customer_name=customer_name,
                                                              auto_insert=True, send_warning=True)
            if not sent_flag:
                """不是被忽视的用户,已经发送了无归属警告消息"""
                if repeat:
                    """是否发现了多重用户?"""
                    repeat_list = [{"mt4_account": x.get('mt4_account'), "customer_name": x.get("customer_name")} for x
                                   in rs]
                    title = "customer_manager_relation表中有重复的用户"
                    content = "{}".format(repeat_list)
                    send_mail(title=title, content=content)
                else:
                    pass
            else:
                """被忽略的用户"""
                pass
        return res


class DrawRecord(mongo_db.BaseDoc):
    """
    批量抓取的记录，每一次正常的批量爬取完数据后，都会写入此记录
    """
    _table_name = "draw_record"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['type'] = str
    type_dict['last_sn'] = int
    type_dict['save_time'] = datetime.datetime

    def __init__(self, **kwargs):
        if "save_time" not in kwargs:
            kwargs['save_time'] = datetime.datetime.now()
        super(DrawRecord, self).__init__(**kwargs)

    @classmethod
    def last_sn(cls, type_str: str) -> dict:
        """
        :param type_str: 爬取类型
        :return:
        """
        """先取本类型的最后一个sn"""
        key = "last_sn_{}".format(type_str)
        prev_last_sn = cache.get(key)
        if prev_last_sn is None:
            """从数据库查询"""
            f = {"type": type_str}
            s = {"last_sn": -1}
            last = cls.find_one_plus(filter_dict=f, sort_dict=s, instance=False)
            if last is None:
                pass
            else:
                prev_last_sn = last['last_sn']
                cache.set(key, prev_last_sn, timeout=1200)
        else:
            pass
        return prev_last_sn

    @classmethod
    def need_stop(cls, type_str: str, draw_data: dict) -> dict:
        """
        在每次爬取完一页后，调用此函数，看看是否需要停下来？
        :param type_str: 爬取类型
        :param draw_data: 爬取的数据
        :return:
        """
        """先取本类型的最后一个sn"""
        prev_last_sn = cls.last_sn(type_str)
        """检查是否需要停下来？"""
        data = None
        if draw_data['end']:
            """解析器发现是最后一页，确认可以停下"""
            stop = True
        else:
            stop = False
            if prev_last_sn is None:
                data = list()
                """数据库没有记录，那就给一时间最为截至日期"""
                the_date = mongo_db.get_datetime_from_str("2018-5-15 0:0:0")
                for x in draw_data['data']:
                    if type_str == "入金信息":
                        cur_time = x.get_attr("pay_time")
                    elif type_str == "出金申请":
                        cur_time = x.get_attr("apply_time")
                    elif type_str == "开户申请":
                        cur_time = x.get_attr("reg_time")
                    else:
                        """正式用户或者其他,全部写入"""
                        cur_time = get_datetime_from_str("2020-12-12 0:0:0")
                    if cur_time > the_date:
                        data.append(x)
                    else:
                        stop = True
                        break
            else:
                pass
        """筛选返回的数据"""
        if isinstance(data, list):
            """prev_last_sn is None的情况，已经筛选过了"""
            pass
        else:
            data = list()
            prev_last_sn = 0 if prev_last_sn is None else prev_last_sn
            for x in draw_data['data']:
                sn = x.get_attr("sn")
                if sn > prev_last_sn:
                    data.append(x)
                else:
                    stop = True
                    break
        return {"stop": stop, "data": data}


class CreateAccountApply(mongo_db.BaseDoc):
    """
    开户申请
    """
    _table_name = "create_account_apply"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['customer_id'] = int  # 客户id，唯一
    type_dict['sn'] = int  # 和customer_id相同，存在是为了兼容性
    type_dict['customer_name'] = str
    type_dict['phone'] = str
    type_dict['email'] = str
    type_dict['proxy'] = str
    type_dict['reg_time'] = datetime.datetime
    type_dict['sent_time'] = datetime.datetime  # 发送时间，已发送过消息的才有

    def send(self) -> None:
        """
        发送信号
        :return:
        """
        out_put = dict()
        markdown = dict()
        out_put['msgtype'] = 'markdown'
        title = "开户申请"
        reg_time = self.get_attr("reg_time")
        reg_time = reg_time.strftime("%y年%m月%d日 %H:%M:%S")
        customer_name = self.get_attr("user_name")
        manager_name = self.get_attr("manager")

        """换行必须在一行后面有2个以上空格然后在\n"""
        text = "> ##### {}  \n {}-客户{},申请开户  \n > 申请时间:{}".format(title, manager_name, customer_name,
                                                                      reg_time)
        markdown["title"] = title
        markdown["text"] = text
        out_put['markdown'] = markdown
        out_put['at'] = {'atMobiles': [], 'isAtAll': False}
        # 发送开户申请
        res = send_signal(out_put, token_name="财务群钉钉小助手")
        if not res:
            ms = "发送消息到 财务群钉钉小助手 失败,消息:{}".format(markdown)
            logger.exception(ms)
        print(res)


class FinanceOutApply(mongo_db.BaseDoc):
    """
    出金申请
    """
    _table_name = "finance_out_apply"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['sn'] = int  # 入金单号
    type_dict['user_name'] = str  # 用户名
    type_dict['user_id'] = int
    type_dict['payee'] = str  # 收款人
    type_dict['account_payee'] = str  # 收款人账户
    type_dict['money'] = float  # 金额
    type_dict['status'] = str  # 状态
    type_dict['submit_ip'] = str  # ip
    type_dict['apply_time'] = datetime.datetime  # 申请时间
    # type_dict['process_time_time'] = datetime.datetime  # 处理时间
    type_dict['save_time'] = datetime.datetime  # 保存时间，用来比较先后
    type_dict['sent_time'] = datetime.datetime  # 发送时间，已发送过消息的才有

    def __init__(self, **kwargs):
        if "save_time" not in kwargs:
            kwargs['save_time'] = datetime.datetime.now()
        super(FinanceOutApply, self).__init__(**kwargs)

    def send(self) -> None:
        """
        发送信号
        :return:
        """
        out_put = dict()
        markdown = dict()
        out_put['msgtype'] = 'markdown'
        title = "出金申请"
        apply_time = self.get_attr("apply_time")
        apply_time = apply_time.strftime("%y年%m月%d日 %H:%M:%S")
        customer_name = self.get_attr("user_name")
        customer_id = self.get_attr("user_id")
        relation = CustomerManagerRelation.get_relation_by_sn(customer_id, customer_name)
        mt4_account = relation.get('mt4_account')
        manager_name = relation['manager_name']
        sales_name = relation['sales_name']
        director_name = relation['director_name']
        amount_usd = self.get_attr("money")

        """换行必须在一行后面有2个以上空格然后在\n"""
        text = "> ##### {}  \n 客户:{}  \n > 申请出金: {}美元  \n > 申请时间:{}  \n > MT4账户:{}  \n > 所属销售: {}  \n > " \
               "所属经理：{}  \n > 所属总监：{}".format(title, customer_name, amount_usd, apply_time, mt4_account,
                                              sales_name, manager_name, director_name)
        markdown["title"] = title
        markdown["text"] = text
        out_put['markdown'] = markdown
        out_put['at'] = {'atMobiles': [], 'isAtAll': False}
        # 发送出金申请提醒
        res = send_signal(out_put, token_name="财务群钉钉小助手")
        if not res:
            ms = "发送消息到 财务群钉钉小助手 失败,消息:{}".format(markdown)
            logger.exception(ms)
        print(res)


class CashInRecord(mongo_db.BaseDoc):
    """
    入金记录
    """
    _table_name = "cash_in_record"
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['sn'] = int  # 入金单号
    type_dict['user_id'] = int  # 用户ｉｄ
    type_dict['user_name'] = str  # 用户名
    type_dict['ticket'] = str  # 订单号，一般到帐了才会有这个．／
    type_dict['money'] = float  # 金额
    type_dict['status'] = str  # 状态
    type_dict['pay_time'] = datetime.datetime  # 支付时间
    type_dict['process_time'] = datetime.datetime  # 处理时间
    type_dict['submit_ip'] = str  # 提交ｉｐ
    type_dict['save_time'] = datetime.datetime  # 保存时间，用来比较先后
    type_dict['sent_time'] = datetime.datetime  # 发送时间，已发送过消息的才有

    def __init__(self, **kwargs):
        if "save_time" not in kwargs:
            kwargs['save_time'] = datetime.datetime.now()
        super(CashInRecord, self).__init__(**kwargs)

    def send(self) -> None:
        """
        发送信号
        :return:
        """
        out_put = dict()
        markdown = dict()
        out_put['msgtype'] = 'markdown'
        title = "入金提醒"
        pay_time = self.get_attr("pay_time")
        pay_time = pay_time.strftime("%y年%m月%d日 %H:%M:%S")
        customer_name = self.get_attr("user_name")
        customer_id = self.get_attr("user_id")
        relation = CustomerManagerRelation.get_relation_by_sn(customer_id, customer_name)
        mt4_account = relation.get('mt4_account', "")
        manager_name = relation['manager_name']
        sales_name = relation['sales_name']
        director_name = relation['director_name']
        amount_usd = self.get_attr("money")

        """换行必须在一行后面有2个以上空格然后在\n"""
        text = "> ##### {}  \n 客户:{}  \n > 入金: {}美元  \n > 支付时间:{}  \n > MT4账户:{}  \n > 所属销售: {}  \n > " \
               "所属经理：{}  \n > 所属总监：{}".format(title, customer_name, amount_usd, pay_time, mt4_account,
                                              sales_name, manager_name, director_name)
        markdown["title"] = title
        markdown["text"] = text
        out_put['markdown'] = markdown
        out_put['at'] = {'atMobiles': [], 'isAtAll': False}
        # 发送入金提醒
        res = send_signal(out_put, token_name="财务群钉钉小助手")
        if not res:
            ms = "发送消息到 财务群钉钉小助手 失败,消息:{}".format(markdown)
            logger.exception(ms)
        if amount_usd > 1000:
            """发送战报"""
            title = "战报"
            markdown['title'] = title
            first_name = customer_name[0:1]
            text = "> ##### {}  \n 恭喜-{}-客户{}xx,入金{}美元![胜利][胜利][胜利],继续加油[加油][加油][加油]".format(title,
                                                                                             sales_name, first_name,
                                                                                             amount_usd)
            markdown['text'] = text
            out_put['markdown'] = markdown
            res = send_signal(out_put, token_name="战报")
            if not res:
                ms = "发送消息到战报失败,消息:{}".format(markdown)
                logger.exception(ms)
        print(res)


chrome_driver = "/opt/google/chrome/chromedriver"  # chromedriver的路径
os.environ["ChromeDriver"] = chrome_driver  # 必须配置,否则会在execute_script的时候报错.
user_name = "xx627265614@tom.com"
user_password = "XD123456"
login_url = "http://user.shengfxchina.com/v2.0/common/login.html"
domain = "user.shengfxchina.com"
url_dict = {
    "出金申请": "http://user.shengfxchina.com/v2.0/common/index.html#http://"
            "user.shengfxchina.com/v2.0/admin/finance_waiting.html",
    "入金信息": "http://user.shengfxchina.com/v2.0/common/index.html#http://"
            "user.shengfxchina.com/v2.0/admin/finance_index.html",
    "开户申请": "http://user.shengfxchina.com/v2.0/common/index.html#http://"
            "user.shengfxchina.com/v2.0/admin/user_index.html"
}


def month_str(month_int: int) -> str:
    l = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
    return l[month_int - 1]


def get_browser(headless: bool = True, browser_class: int = 1) -> Firefox:
    """
    获取一个浏览器
    :param headless:
    :param browser_class: 浏览器种类,0是谷歌, 1 是火狐,
    :return:
    """
    """
    firefox的headless浏览器
    因为headless的浏览器的语言跟随操作系统,为了保证爬回来的数据是正确的语言,
    这里必须设置浏览器的初始化参数,
    注意，使用headless必须先安装对应浏览器正常的版本,然后再安装headless版本
    比如火狐的headless
    下载火狐的geckodriver驱动。(当前文件夹下已经有一个了)地址是：
    https://github.com/mozilla/geckodriver/releases
    下载后解压是一个geckodriver 文件。拷贝到/usr/local/bin目录下，然后加上可执行的权限
    sudo chmod +x /usr/local/bin/geckodriver
    chrome的headless浏览器
    https://chromedriver.storage.googleapis.com/index.html?path=2.35/
    你也可以自行搜索chromedriver的下载地址,解压是个可执行文件,放到chrome的目录即可.
    一般ubuntu下面,chrome的目录是/opt/google/chrome/
    据说使用root权限运行的话,chrome的headless浏览器会报异常.而firefox的headless浏览器不会!
    附录:
    安装火狐浏览器标准版的方法:
    1. sudo add-apt-repository ppa:mozillateam/firefox-next  出现提示后回车继续
       如果你提示 add-apt-repository: command not found ,那就是缺少命令,请用如下方式安装:
       sudo apt-get install software-properties-common python-software-properties  
    2. sudo apt update
    3. sudo apt install firefox
    """
    if browser_class == 1:
        profile = FirefoxProfile()
        profile.set_preference("intl.accept_languages", "zh-cn")
        """设置代理"""
        # profile.set_preference("signon.autologin.proxy", False)
        # profile.set_preference("network.proxy.type", 1)
        # profile.set_preference("network.proxy.http", "121.236.77.190")
        # profile.set_preference("network.proxy.http_port", 8118)
        # profile.set_preference("network.proxy.share_proxy_settings", True)

        options = FirefoxOptions()
        options.add_argument("--headless")
        if headless:
            try:
                browser = Firefox(firefox_profile=profile, firefox_options=options)
            except Exception as e:
                title = "{} Firefox headless浏览器打开失败".format(datetime.datetime.now())
                content = "错误原因是：{}".format(e)
                send_mail(title=title, content=content)
                recode(e)
                logger.exception(e)
                raise e
        else:
            try:
                browser = Firefox(firefox_profile=profile)
            except Exception as e:
                title = "{} Firefox headless浏览器打开失败".format(datetime.datetime.now())
                content = "错误原因是：{}".format(e)
                send_mail(title=title, content=content)
                recode(e)
                logger.exception(e)
                raise e
    else:
        options = ChromeOptions()
        options.add_argument("--headless")
        if headless:
            try:
                browser = Chrome(executable_path=chrome_driver, chrome_options=options)
            except Exception as e:
                title = "{} Chrome headless浏览器打开失败".format(datetime.datetime.now())
                content = "错误原因是：{}".format(e)
                send_mail(title=title, content=content)
                recode(e)
                logger.exception(e)
                raise e
        else:
            try:
                browser = Chrome(executable_path=chrome_driver)
            except Exception as e:
                title = "{} Chrome headless浏览器打开失败".format(datetime.datetime.now())
                content = "错误原因是：{}".format(e)
                send_mail(title=title, content=content)
                recode(e)
                logger.exception(e)
                raise e
    return browser


def login_platform(browser):
    """
    登录平台
    :param browser:
    :return:requests.Session
    """
    browser.get(url=login_url)
    # recode("html= {}".format(browser.page_source))
    flag = True
    """防止元素被遮住"""
    while flag:
        try:
            # 用户名输入
            select_email = WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "tab_emial")))
            select_email.click()
            input_user_name = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "#account")))
            input_user_name.send_keys(user_name)  # 输入用户名
            # 用户密码输入
            input_user_password = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "#password")))
            input_user_password.send_keys(user_password)  # 输入用户密码
            # 点击登录按钮
            button_login = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, ".login_content .btn_login")))
            button_login.click()  # 登录
            flag = False
        except ElementClickInterceptedException as e:
            print(e)
            time.sleep(0.1)
        finally:
            pass
    logo = None
    try:
        logo = WebDriverWait(browser, 10).until(ec.presence_of_element_located((By.ID, "a_hrefto_domain")))
    except TimeoutException as e:
        title = "login_platform 后台登录失败.{}".format(datetime.datetime.now())
        send_mail(title=title)
        raise e
    finally:
        if isinstance(logo, FirefoxWebElement):
            del logo
            return True


def need_login_platform(browser) -> bool:
    """
    平台是否需要登录？
    :param browser:
    :return: True需要登录，False，不需要登录
    """
    if browser.current_url.startswith(login_url):
        print("current url is {}".format(browser.current_url))
        return True
    else:
        return False


def open_platform(browser) -> bool:
    """
    打开平台站点,如果已经登录,返回True,否则尝试重新login,三次失败后,返回False
    :param browser:
    :return: 布尔值 True开打成功，False，打开失败，请检查程序
    """
    about_url = "http://user.shengfxchina.com/v2.0/common/index.html#http://user.shengfxchina.com/v2.0/" \
          "admin/manager_index.html"
    try:
        browser.get(about_url)
    except Exception as e:
        print(e)
        recode(e)
        logger.exception(e)
    finally:
        open_count = 0
        while need_login_platform(browser) and open_count < 3:
            if open_count > 1:
                """第一次登录失败，要等五分钟"""
                time.sleep(60 * 5)
            else:
                pass
            open_count += 1
            login_platform(browser=browser)

        browser.get(about_url)
        return not need_login_platform(browser)


def redirect(browser, page_name: str) -> None:
    """
    转到指定的页面,注意，此平台页面使用frame嵌套的．
    本函数执行后，browser会被切换到内层的frame中．
    :param browser:
    :param page_name: 出金申请/入金信息/开户申请
    :return:
    """
    """先切换到默认文档，保证接下来的操作从正确的文档开始"""
    browser.switch_to_default_content()
    # browser.switch_to.parent_frame()  # 两种方法都切换回主文档
    # browser.switch_to_default_content() # 两种方法都可以切换回主文档
    """导航第一级的按钮"""
    """用户"""
    btn_user = WebDriverWait(browser, 10).until(ec.element_to_be_clickable((By.CSS_SELECTOR,
                                                                               ".frist-menu dd[data-module='user']")))
    """财务"""
    btn_finance = WebDriverWait(browser, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, ".frist-menu dd[data-module='finance']")))

    if page_name == '入金信息':
        """
        导航第二级的按钮,必须要在第一级的导航按钮按下以后才会出现.
        所有入金记录按钮
        """
        btn_finance.click()
        browser.switch_to.frame(browser.find_element_by_id("show_content"))  # 切换进内层frame
        flag = True
        """防止元素被遮住"""
        while flag:
            try:
                """获取所入金记录二级导航按钮"""
                btn_finance_in = WebDriverWait(browser, 10).until(
                    ec.element_to_be_clickable((By.CSS_SELECTOR, ".btn-d[href='finance_index.html']")))
                btn_finance_in.click()  # 点击所入金记录二级导航按钮
                """获取入金状态选择按钮"""
                select_status = Select(browser.find_element_by_id("state1"))
                select_status.select_by_value("DEPOSITED")  # 选择＂已到帐＂
                flag = False
            except ElementClickInterceptedException as e:
                print(e)
                time.sleep(0.1)
            finally:
                pass
    elif page_name == "出金申请":
        """按下财务按钮"""
        btn_finance.click()
        """
        以１０秒为限等待＇出金处理＇按钮出现，然后点击
        注意，二级页面是在ｉｆｒａｍｅ里面
        """
        browser.switch_to.frame(browser.find_element_by_id("show_content"))  # 切换进内层frame
        flag = True
        """防止元素被遮住"""
        while flag:
            try:
                """获取所有出金记录二级导航按钮"""
                btn_finance_out = WebDriverWait(browser, 10).until(
                    ec.element_to_be_clickable((By.CSS_SELECTOR, "a[href='finance_check_record.html']")))
                btn_finance_out.click()  # 按下所有出金记录二级导航按钮
                """获取入金状态选择按钮"""
                select_status = Select(browser.find_element_by_id("state1"))
                select_status.select_by_value("WAITING")  # 选择＂待合规审核＂
                flag = False
            except ElementClickInterceptedException as e:
                print(e)
                time.sleep(0.1)
            finally:
                pass
    elif page_name == "开户申请":
        btn_user.click()
        browser.switch_to.frame(browser.find_element_by_id("show_content"))  # 切换进内层frame
        flag = True
        """防止元素被遮住"""
        while flag:
            try:
                """获取所有用户二级导航按钮"""
                btn_user_all = WebDriverWait(browser, 10).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, ".load_user_header a[href='user_index.html']")))
                btn_user_all.click()  # 所有用户二级导航按钮
                """获取用户状态选择按钮"""
                select_status = Select(browser.find_element_by_id("state1"))
                select_status.select_by_value("auditing")  # 选择＂待审核＂
                flag = False
            except ElementClickInterceptedException as e:
                print(e)
                time.sleep(0.1)
            finally:
                pass
    else:
        """去所有用户的页面,这种情况是为了测试,实际中不会用到"""
        pass


def create_account_formater(browser) -> dict:
    """
    开户申请解析器
    :param browser:
    :return:
    """
    content = browser.page_source
    content = PyQuery(content)
    trs = content.find("#result_list1 tr")  # 表格的tr集合
    """
    注意，这个表格是内容和翻页部分混合在一起的。都是tr元素
    1. 页码tr位于table的tbody的最后一行
    2. 如果只有一页，那就没有页码tr
    3. 非页码tr有style属性。
    4. 页码tr只有一个tr，而且这个tr有colspan属性。
    """
    """确认当前页和下一页。检查是否有页码区？"""
    result = dict()
    if len(trs) == 0:
        result['end'] = True
        result['data'] = list()
    else:
        delay = 0.1
        while PyQuery(trs[0]).find("td")[0].text == "正在搜索...":
            """检查是否获取html成功，如果不成功，再次获取"""
            content = browser.page_source
            content = PyQuery(content)
            trs = content.find("#result_list1 tr")  # 表格的tr集合
            if delay > 5:
                """超时太久，放弃"""
                ms = "开户申请解析器因超时出错。{}".format(datetime.datetime.now())
                send_mail(title=ms)
                logger.exception(ms)
                raise RuntimeError(ms)
            time.sleep(delay)
            delay += 0.1
        page_tr = PyQuery(trs[-1])
        if len(page_tr.find("td")) == 1:
            """这是页码tr"""
            cur_page_element = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, ".pagelist .disabled")))
            cur_page = int(cur_page_element.text)
            next_element = WebDriverWait(browser, 10).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".pagelist a")))[-1]
            href = next_element.get_attribute("href")
            next_page = int(re.search(r'\d+', href.split("(")[-1]).group())
            trs.pop(-1)
        else:
            cur_page = 1  # 当前页码
            next_page = -1  # 下一页 如果下一页小于当前页，那当前就是最后一页
        """解析数据区域"""
        res = list()
        for tr in trs:
            tds = PyQuery(tr).find("td")
            tds = [PyQuery(td).text().strip() for td in tds]
            temp = dict()
            a = tds[0].split("]")
            user_id = int(re.search(r'\d+', a[0]).group())
            temp['user_id'] = user_id
            # print(tds)
            temp['user_name'] = a[1]
            temp['sn'] = user_id
            temp['status'] = tds[1]
            temp['reg_time'] = mongo_db.get_datetime_from_str(tds[2])
            temp['proxy'] = tds[4].split("[")[0]
            temp['email'] = tds[5]
            temp['phone'] = tds[6]
            res.append(CreateAccountApply(**temp))
        result['data'] = res
        end = False if next_page > cur_page else True
        result['end'] = end
        if not end:
            """还不是末页，再点击一下“下一页”按钮"""
            btn_list = WebDriverWait(browser, 10).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".pagelist a")))
            next_btn = btn_list[-1]
            next_btn.click()
    return result


def cash_in_formater(browser) -> dict:
    """
    入金信息解析器
    :param browser:
    :return:
    """
    content = browser.page_source
    content = PyQuery(content)
    trs = content.find("#result_list1 tr")  # 表格的tr集合
    """
    注意，这个表格是内容和翻页部分混合在一起的。都是tr元素
    1. 页码tr位于table的tbody的最后一行
    2. 如果只有一页，那就没有页码tr
    3. 非页码tr有style属性。
    4. 页码tr只有一个tr，而且这个tr有colspan属性。
    """
    """确认当前页和下一页。检查是否有页码区？"""
    result = dict()
    if len(trs) == 0:
        result['end'] = True
        result['data'] = list()
    else:
        delay = 0.1
        while PyQuery(trs[0]).find("td")[0].text == "正在搜索...":
            """检查是否获取html成功，如果不成功，再次获取"""
            content = browser.page_source
            content = PyQuery(content)
            trs = content.find("#result_list1 tr")  # 表格的tr集合
            if delay > 5:
                """超时太久，放弃"""
                ms = "入金信息解析器因超时出错。{}".format(datetime.datetime.now())
                send_mail(title=ms)
                logger.exception(ms)
                raise RuntimeError(ms)
            time.sleep(delay)
            delay += 0.1
        page_tr = PyQuery(trs[-1])
        if len(page_tr.find("td")) == 1:
            """这是页码tr"""
            cur_page_element = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, ".pagelist .disabled")))
            cur_page = int(cur_page_element.text)
            next_element = WebDriverWait(browser, 10).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".pagelist a")))[-1]
            href = next_element.get_attribute("href")
            next_page = int(re.search(r'\d+', href.split("(")[-1]).group())
            trs.pop(-1)
        else:
            cur_page = 1  # 当前页码
            next_page = -1  # 下一页 如果下一页小于当前页，那当前就是最后一页
        """解析数据区域"""
        res = list()
        for tr in trs:
            tds = PyQuery(tr).find("td")
            tds = [PyQuery(td).text().strip() for td in tds]
            temp = dict()
            temp['sn'] = tds[0].strip("#")
            # print(tds)
            temp['status'] = tds[1]
            a = tds[2].split("]")
            temp['user_id'] = int(re.search(r'\d+', a[0]).group())
            temp['user_name'] = a[1]
            temp['ticket'] = tds[3]
            temp['money'] = float(tds[4].replace(",", ""))
            temp['pay_time'] = mongo_db.get_datetime_from_str(tds[5])
            temp['process_time'] = mongo_db.get_datetime_from_str(tds[6])
            temp['submit_ip'] = tds[7]
            res.append(CashInRecord(**temp))
        result['data'] = res
        end = False if next_page > cur_page else True
        result['end'] = end
        if not end:
            """还不是末页，再点击一下“下一页”按钮"""
            btn_list = WebDriverWait(browser, 10).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".pagelist a")))
            next_btn = btn_list[-1]
            next_btn.click()
    return result


def finance_out_formater(browser) -> dict:
    """
    出金申请解析器
    :param browser:
    :return:
    """
    content = browser.page_source
    content = PyQuery(content)
    trs = content.find("#result_list1 tr")  # 表格的tr集合
    """
    注意，这个表格是内容和翻页部分混合在一起的。都是tr元素
    1. 页码tr位于table的tbody的最后一行
    2. 如果只有一页，那就没有页码tr
    3. 非页码tr有style属性。
    4. 页码tr只有一个tr，而且这个tr有colspan属性。
    """
    """确认当前页和下一页。检查是否有页码区？"""
    result = dict()
    if len(trs) == 0:
        result['end'] = True
        result['data'] = list()
    else:
        delay = 0.1
        while PyQuery(trs[0]).find("td")[0].text == "正在搜索...":
            """检查是否获取html成功，如果不成功，再次获取"""
            content = browser.page_source
            content = PyQuery(content)
            trs = content.find("#result_list1 tr")  # 表格的tr集合
            if delay > 5:
                """超时太久，放弃"""
                ms = "出金申请解析器因超时出错。{}".format(datetime.datetime.now())
                send_mail(title=ms)
                logger.exception(ms)
                raise RuntimeError(ms)
            time.sleep(delay)
            delay += 0.1
        page_tr = PyQuery(trs[-1])
        if len(page_tr.find("td")) == 1:
            """这是页码tr"""
            cur_page_element = WebDriverWait(browser, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, ".pagelist .disabled")))
            cur_page = int(cur_page_element.text)
            next_element = WebDriverWait(browser, 10).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".pagelist a")))[-1]
            href = next_element.get_attribute("href")
            next_page = int(re.search(r'\d+', href.split("(")[-1]).group())
            trs.pop(-1)
        else:
            cur_page = 1  # 当前页码
            next_page = -1  # 下一页 如果下一页小于当前页，那当前就是最后一页
        """解析数据区域"""
        res = list()
        for tr in trs:
            tds = PyQuery(tr).find("td")
            tds = [PyQuery(td).text().strip() for td in tds]
            temp = dict()
            temp['sn'] = tds[0].strip("#")
            # print(tds)
            temp['status'] = tds[1]
            a = tds[2].split("]")
            temp['user_id'] = int(re.search(r'\d+', a[0]).group())
            temp['user_name'] = a[1]
            temp['payee'] = tds[3]
            temp['account_payee'] = tds[4]
            temp['money'] = float(tds[5].replace(",", ""))
            temp['apply_time'] = mongo_db.get_datetime_from_str(tds[6])
            temp['submit_ip'] = tds[8]
            res.append(FinanceOutApply(**temp))
        result['data'] = res
        end = False if next_page > cur_page else True
        result['end'] = end
        if not end:
            """还不是末页，再点击一下“下一页”按钮"""
            btn_list = WebDriverWait(browser, 10).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".pagelist a")))
            next_btn = btn_list[-1]
            next_btn.click()
    return result


formater_dict = dict()
formater_dict['入金信息'] = cash_in_formater
formater_dict['出金申请'] = finance_out_formater
formater_dict['开户申请'] = create_account_formater


def sent_instance(type_name: str, last_sn: int) -> list:
    """
    返回已发送过的记录的sn的集合
    :param type_name:
    :param last_sn:
    :return:
    """
    a_dict = {
        "入金信息": CashInRecord,
        "出金申请": FinanceOutApply,
        "开户申请": CreateAccountApply
    }
    f = {"sn": {"$gt": last_sn}, "sent_time": {"$exists": True}}
    pro = ['sn']
    cls = a_dict[type_name]
    rs = cls.find_plus(filter_dict=f, projection=pro, to_dict=True)
    if len(rs) == 0:
        return list()
    else:
        return [x['sn'] for x in rs]


def parse_content(browser, type_name) -> None:
    """
    解析一页frame的内容，注意，这时候browser必须已经切换到内层的frame上了．
    :param browser: 已经切换到内层的browser
    :param type_name: l类型
    :return:
    """
    stop = False
    last_sn = DrawRecord.last_sn(type_name)
    last_sn = 0 if last_sn is None else last_sn
    while not stop:
        formater = formater_dict[type_name]  # 解析器
        parse_result = formater(browser)
        parse_result = DrawRecord.need_stop(type_name, parse_result)
        stop = parse_result['stop']
        data = parse_result['data']
        now = datetime.datetime.now()
        sent_list = sent_instance(type_name, last_sn)
        for x in data:
            sn = x.get_attr("sn")
            if sn not in sent_list and sn > last_sn:
                x.send()  # 发送信号
                ms = "sent!!! {}信号已发送.sn:{}, time:{}".format(type_name, x.get_attr("sn", ""), now)
                logger.info(ms)
                print(ms)
                last_sn = sn
            x.set_attr("sent_time", now)
            try:
                x.insert()
            except ValueError as e:
                """ValueError: 重复的 sn:..."""
                print(e)
            finally:
                pass

    """写入一次完整的批量抓取信息"""
    record = {"type": type_name, "last_sn": last_sn}
    record = DrawRecord(**record)
    key = "last_sn_{}".format(type_name)
    cache.set(key, last_sn, timeout=1200)
    record.insert()


def do_jobs():
    """批量作业"""
    begin = datetime.datetime.now()
    ms = "批量作业开始: {}".format(begin)
    logger.info(ms)
    b = get_browser(False, 1)
    open_platform(b)
    for type_name in formater_dict.keys():
        redirect(b, type_name)
        parse_content(b, type_name)
    b.quit()
    del b
    end = datetime.datetime.now()
    d = (end - begin).total_seconds() / 60
    ms = "批量作业结束: {}, 耗时：{}分".format(end, d)
    logger.info(ms)


if __name__ == "__main__":
    """全套测试开始"""
    while 1:
        do_jobs()
        time.sleep(500)
    pass