#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from log_module import get_logger
from mail_module import send_mail
import requests
import re
import time
import datetime
from pyquery import PyQuery
from mongo_db import get_datetime_from_str
from werkzeug.contrib.cache import RedisCache
from module.transaction_module import Transaction
from module.transaction_module import Withdraw

logger = get_logger()
cache = RedisCache()

"""爬虫模块,使用requests，有限制，只能爬前16页"""

type_dict = {"buy": 0, "sell": 1, "balance": 6, "credit": 7}
headers1 = {'Accept': 'text/html',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Charset': 'utf-8',
           'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
           'Connection': 'Keep-Alive',
           'Host': 'office.shengfx888.com',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
headers2 = {'Accept': 'text/html',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Charset': 'utf-8',
           'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
           'Connection': 'Keep-Alive',
           'Host': 'office.shengfxchina.com:8443',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         ' (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
user_name1 = "849607604@qq.com"
user_password1 = "Kai3349665"
login_url1 = "http://office.shengfx888.com"
check_login_url1 = "http://office.shengfx888.com/Public/checkLogin"
domain1 = "office.shengfx888.com"
page_url_base1 = "http://office.shengfx888.com/report/history_trade?" \
                "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=" \
                "&PROFIT_e=&qtype=&CMD=&closetime=&OPEN_TIME_s=" \
                "&OPEN_TIME_e=&CLOSE_TIME_s=&CLOSE_TIME_e=&T_LOGIN="
__page_url_base1 = "http://office.shengfx888.com/report/history_trade?" \
                "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=" \
                "&PROFIT_e=&qtype=&CMD={}&closetime=&OPEN_TIME_s=" \
                "&OPEN_TIME_e=&CLOSE_TIME_s=&CLOSE_TIME_e=&T_LOGIN=&page={}"
user_name2 = "627853018@qq.com"
user_password2 = "XIAOxiao@741"
domain2 = "office.shengfxchina.com:8443"
login_url2 = "https://office.shengfxchina.com:8443/Public/login"
check_login_url2 = "https://office.shengfxchina.com:8443/Public/checkLogin"
page_url_base2 = "https://office.shengfxchina.com:8443/report/history_trade?" \
                 "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=&PROFIT_e=&qtype=" \
                 "&CMD=&closetime=&OPEN_TIME_s=&OPEN_TIME_e=&CLOSE_TIME_s=" \
                 "&CLOSE_TIME_e=&comm_type=&T_LOGIN="
__page_url_base2 = "https://office.shengfxchina.com:8443/report/history_trade?" \
                 "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=&PROFIT_e=&qtype=" \
                 "&CMD={}&closetime=&OPEN_TIME_s=&OPEN_TIME_e=&CLOSE_TIME_s=" \
                 "&CLOSE_TIME_e=&comm_type=&T_LOGIN=&page={}"
withdraw_url_base2 = "https://office.shengfxchina.com:8443/deposit/waitin?" \
                     "layout=yes&weburlredect=1&page={}"  # 2号平台,出金申请


def get_page_url(domian: str, transaction: str, page_num: int = 1) -> str:
    """
    获取一号/二号平台综合业务网址
    :param domian: 基础网址
    :param transaction: 交易类型， buy/sell/balance/credit
    :param page_num:
    :return:
    """
    if domian == domain1:
        _base = __page_url_base1
    else:
        _base = __page_url_base2
    r = _base.format(type_dict[transaction], page_num)
    return r


def login_platform(session: requests.Session, domain: str):
    """
    登录一号/二号平台
    :param session:
    :param domain:
    :return:requests.Session
    """
    if domain == domain1:
        url = login_url1
        user_name = user_name1
        user_password = user_password1
        headers = headers1
        check_login_url = check_login_url1
    else:
        url = login_url2
        user_name = user_name2
        user_password = user_password2
        headers = headers2
        check_login_url = check_login_url2
    session.headers = headers
    resp = session.get(url)
    # text = resp.text
    # print(text)
    args = {"account": user_name, "password": user_password}
    resp = session.post(check_login_url, data=args)
    code = resp.status_code
    if code != 200:
        ms = "登录平台{}失败，错误码 {}".format(domain, code)
        logger.exception(ms)
        return False
    else:
        # mes = resp.text
        # print(mes)
        return True


def need_login_platform(session: requests.Session, domain: str) -> bool:
    """
    一号/二号平台是否需要登录？
    :param session:
    :param domain:
    :return: True需要登录，False，不需要登录
    """
    if domain == domain1:
        page_url_base = page_url_base1
        headers = headers1
    else:
        headers = headers2
        page_url_base = page_url_base2
    session.headers = headers
    r = session.get(page_url_base)
    code = r.status_code
    if code != 200:
        ms = "检查是否需要登录平台{}失败，错误码 {}".format(domain, code)
        logger.exception(ms)
        return False
    else:
        t = r.content
        print(r.text)
        pq = PyQuery(t)
        u_name = pq.find("form .uname")
        if u_name.attr("placeholder") == '请输入邮箱或者MT账号':
            return True
        else:
            return False


def open_platform(session: requests.Session, domain: str) -> bool:
    """
    打开一号/二号平台站点,如果已经登录,返回True,否则尝试重新login,三次失败后,返回False
    :param session: 基础网址
    :param domain:
    :return: 布尔值 True开打成功，False，打开失败，请检查程序
    """
    if domain == domain1:
        headers = headers1
        login_url = login_url1
    else:
        headers = headers2
        login_url = login_url2

    session.headers = headers
    count = 0
    flag = not need_login_platform(session, domain)
    while (not flag) and count < 3:
        flag = login_platform(session, login_url)
        if not flag:
            ms = "登录{}失败".format(login_url)
            logger.exception(ms)
        else:
            pass
        count += 1
    return flag


def get_page_platform(session: requests.Session, page_url: str) -> (PyQuery, None):
    """
    获取一页一号/二号平台站点的页面html,包含交易和出金申请,返回页面内容的PQuery对象
    :param session:
    :param page_url: 页面网址
    :return:
    """
    r = session.get(page_url)
    code = r.status_code
    if code != 200:
        ms = "page_html_platform {}失败，错误码 {}".format(page_url, code)
        logger.exception(ms)
        return None
    else:
        html = r.content
        pq = PyQuery(html)
        return pq


def extract_transaction_table(pq: PyQuery, domain: str) -> list:
    """
    提取一页一号/二号平台站点的四类交易页面html，从中提取出来表格,
    然后提出多个tr，把每一个tr分别解析成dict对象。最后返回单个tr解析成的dict的list
    :param pq:
    :param domain:
    :return:
    """
    query = "#editable tbody tr"
    trs = PyQuery(pq.find(query))
    res = list()
    for tr_html in trs:
        tr = PyQuery(tr_html)
        tr_dict = parse_transaction_tr(tr, domain)
        if isinstance(tr_dict, dict):
            res.append(tr_dict)
        else:
            pass
    return res


def extract_withdraw_table(pq: PyQuery) -> list:
    """
    提取一页二号平台站点的出金申请页面html，从中提取出来表格,虽然代码和extract_transaction_table
    几乎一样，但是分开的目的是防止这2类页面代码修改，这样就不得不分开方法。所以干脆提前分开方法
    然后提出多个tr，把每一个tr分别解析成dict对象。最后返回单个tr解析成的dict的list
    :param pq:
    :return:
    """
    query = "#editable tbody tr"
    trs = PyQuery(pq.find(query))
    res = list()
    for tr_html in trs:
        tr = PyQuery(tr_html)
        tr_dict = parse_withdraw_tr(tr)
        if isinstance(tr_dict, dict):
            res.append(tr_dict)
        else:
            pass
    return res


def parse_transaction_tr(tr: PyQuery, domain: str) -> dict:
    """
    解析一页一号/二号平台站点的四类交易的tr
    :param tr: 
    :param domain: 
    :return: 
    """
    init_dict = dict()
    tds = tr.find("td")
    """平台1和平台2区别对待"""
    if domain == domain:
        """第一个td,取订单号和客户帐号"""
        first = PyQuery(tds[0])
        texts_1 = first.text().split("\n")
        ticket = int(re.search(r'\d{4,}', texts_1[0]).group())  # 订单号
        login = int(re.search(r'\d{6,}', texts_1[-1]).group())  # 客户帐号
        init_dict['ticket'] = ticket
        init_dict['login'] = login
        """第二个td，取英文名和真实姓名"""
        second = PyQuery(tds[1])
        texts_2 = second.text().split("\n")
        nick_name = texts_2[0][4:].strip("")
        real_name = texts_2[-1][5:].strip("")
        init_dict['nick_name'] = nick_name
        init_dict['real_name'] = real_name
        """第三个td，取交易指令和品种"""
        third = PyQuery(tds[2])
        texts_3 = third.text().split("\n")
        command = texts_3[0].lower()
        init_dict['command'] = command
        sys_val = domain
        print("domain = {}, command = {}, tds'length = {}".format(sys_val, command, len(tds)))
        init_dict['system'] = sys_val
        # print(ticket, command, texts_3)
        if command == "balance" or command == "credit":
            """出入金和赠金，少了几个td"""
            """第四个，交易时间"""
            eighth = PyQuery(tds[4]).text()
            the_time = get_datetime_from_str(eighth)  # 交易时间
            init_dict['time'] = the_time
            # print("出入金时间：{}".format(the_time))
            """
            第五个，盈亏
            """
            ninth = PyQuery(tds[5]).text()
            profit = re.search(r'[+, -]?\d+.?\d*', ninth)
            if profit is not None:
                profit = float(profit.group())
                init_dict['profit'] = profit
            """第六个，点差"""
            tenth = PyQuery(tds[6]).text()
            spread_profit = None
            try:
                spread_profit = float(tenth)
            except ValueError as e:
                print(e)
            finally:
                if spread_profit is None:
                    pass
                else:
                    init_dict['spread_profit'] = spread_profit
            """第七个，注释"""
            comment = None
            try:
                eleventh = PyQuery(tds[7]).text()
                comment = eleventh

            except IndexError as e:
                print(e)
            finally:
                if comment is not None:
                    init_dict['comment'] = comment
                else:
                    pass

            init_dict = {k: v for k, v in init_dict.items() if v is not None}
        else:
            """buy和sell的情况"""
            symbol = ''
            if len(texts_3) > 1:
                symbol = texts_3[-1].lower()
                init_dict['symbol'] = symbol
            """第四个td，取交易手数"""
            fourth = PyQuery(tds[3])
            lot_find = re.search(r'\d+.?\d*', fourth.text())
            lot = lot_find if lot_find is None else float(lot_find.group()) if symbol != "hk50mini" else \
                float(lot_find.group()) / 10
            init_dict['lot'] = lot
            """
            第五个，取价格，
            """
            fifth = PyQuery(tds[4])
            prices = fifth.text().split("\n")
            enter_price = float(re.search(r'\d+.?\d*', prices[0]).group())  # 开仓
            exit_price = float(re.search(r'\d+.?\d*', prices[-1]).group())  # 平仓
            init_dict['enter_price'] = enter_price
            init_dict['exit_price'] = exit_price
            """
            第六个，止盈/止损，
            """
            sixth = PyQuery(tds[5])
            stop = sixth.text().split("\n")
            stop_losses = float(re.search(r'\d+.?\d*', stop[0]).group())  # 止损
            take_profit = float(re.search(r'\d+.?\d*', stop[-1]).group())  # 止盈
            init_dict['stop_losses'] = stop_losses
            init_dict['take_profit'] = take_profit
            """
            第七个，利息/佣金，
            """
            seventh = PyQuery(tds[6])
            seventh = seventh.text().split("\n")
            swap_match = re.search(r'[+, -]?\d+.?\d*', seventh[0])
            if swap_match is not None:
                swap = float(swap_match.group())  # 利息
            else:
                swap = None
            commission_match = re.search(r'[+, -]?\d+.?\d*', seventh[-1])
            if commission_match is not None:
                commission = float(commission_match.group())  # 手续费
            else:
                commission = None
            init_dict['swap'] = swap
            init_dict['commission'] = commission
            """第八个，交易时间"""
            eighth = PyQuery(tds[7]).text()
            eighth = eighth.split("\n")
            if command not in ["balance", "credit"]:
                open_time = get_datetime_from_str(eighth[0].split("：")[1])  # 开仓时间
                init_dict['open_time'] = open_time
                if eighth[-1].find("持仓中") != -1:
                    """持仓中"""
                    pass
                else:
                    close_time_list = eighth[-1].split("：")
                    if len(close_time_list) > 1:
                        close_time = get_datetime_from_str(close_time_list[1])  # 平仓时间
                        init_dict['close_time'] = close_time
                    else:
                        pass
            else:
                pass
            """
            第九个，盈亏
            """
            ninth = PyQuery(tds[8]).text()
            profit = re.search(r'[+, -]?\d+.?\d*', ninth)
            if profit is not None:
                profit = float(profit.group())
                init_dict['profit'] = profit
            """注意,平台1和平台2的列数不一样,平台1有点差,11列,平台2没有点差,10列"""
            if len(tds) == 11:
                """第十个，点差"""
                tenth = PyQuery(tds[-2]).text()
                spread_profit = float(tenth)
                init_dict['spread_profit'] = spread_profit
            else:
                pass
            """最后一个，注释"""
            eleventh = PyQuery(tds[-1]).text()
            comment = eleventh
            init_dict['comment'] = comment

    else:
        """平台2的解析"""
        """第一个td,取订单号和客户帐号"""
        first = PyQuery(tds[0])
        texts_1 = first.text().split("\n")
        ticket = int(re.search(r'\d{4,}', texts_1[0]).group())  # 订单号
        login = int(re.search(r'\d{6,}', texts_1[-1]).group())  # 客户帐号
        init_dict['ticket'] = ticket
        init_dict['login'] = login
        """第二个td，取英文名和MT名称"""
        second = PyQuery(tds[1])
        texts_2 = second.text().split("\n")
        nick_name = texts_2[0][4:].strip("")
        real_name = texts_2[-1][5:].strip("")
        init_dict['nick_name'] = nick_name
        init_dict['real_name'] = real_name
        """第三个td，取交易指令和品种"""
        third = PyQuery(tds[2])
        texts_3 = third.text().split("\n")
        command = texts_3[0].lower()
        init_dict['command'] = command
        sys_val = domain
        print("domain = {}, command = {}, tds'length = {}".format(sys_val, command, len(tds)))
        init_dict['system'] = sys_val
        # print(ticket, command, texts_3)
        if command == "balance" or command == "credit":
            """出入金和赠金，少了几个td"""
            """第四个，交易时间"""
            eighth = PyQuery(tds[4]).text()
            the_time = get_datetime_from_str(eighth)  # 交易时间
            init_dict['time'] = the_time
            # print("出入金时间：{}".format(the_time))
            """
            第五个，盈亏
            """
            ninth = PyQuery(tds[5]).text()
            profit = re.search(r'[+, -]?\d+.?\d*', ninth)
            if profit is not None:
                profit = float(profit.group())
                init_dict['profit'] = profit
            """第六个，注释"""
            comment = None
            try:
                eleventh = PyQuery(tds[-1]).text()
                comment = eleventh

            except IndexError as e:
                print(e)
            finally:
                if comment is not None:
                    init_dict['comment'] = comment
                else:
                    pass

            init_dict = {k: v for k, v in init_dict.items() if v is not None}
        else:
            """buy和sell的情况"""
            symbol = ''
            if len(texts_3) > 1:
                symbol = texts_3[-1].lower()
                init_dict['symbol'] = symbol
            """第四个td，取交易手数"""
            fourth = PyQuery(tds[3])
            lot_find = re.search(r'\d+.?\d*', fourth.text())
            lot = lot_find if lot_find is None else float(lot_find.group()) if symbol != "hk50mini" else \
                float(lot_find.group()) / 10
            init_dict['lot'] = lot
            """
            第五个，取价格，
            """
            fifth = PyQuery(tds[4])
            prices = fifth.text().split("\n")
            enter_price = float(re.search(r'\d+.?\d*', prices[0]).group())  # 开仓
            exit_price = float(re.search(r'\d+.?\d*', prices[-1]).group())  # 平仓
            init_dict['enter_price'] = enter_price
            init_dict['exit_price'] = exit_price
            """
            第六个，止盈/止损，
            """
            sixth = PyQuery(tds[5])
            stop = sixth.text().split("\n")
            stop_losses = float(re.search(r'\d+.?\d*', stop[0]).group())  # 止损
            take_profit = float(re.search(r'\d+.?\d*', stop[-1]).group())  # 止盈
            init_dict['stop_losses'] = stop_losses
            init_dict['take_profit'] = take_profit
            """
            第七个td是空的
            """
            """第八个，交易时间"""
            eighth = PyQuery(tds[7]).text()
            eighth = eighth.split("\n")
            if command not in ["balance", "credit"]:
                open_time = get_datetime_from_str(eighth[0].split("：")[1])  # 开仓时间
                init_dict['open_time'] = open_time
                if eighth[-1].find("持仓中") != -1:
                    """持仓中"""
                    pass
                else:
                    close_time_list = eighth[-1].split("：")
                    if len(close_time_list) > 1:
                        close_time = get_datetime_from_str(close_time_list[1])  # 平仓时间
                        init_dict['close_time'] = close_time
                    else:
                        pass
            else:
                pass
            """
            第九个，盈亏
            """
            ninth = PyQuery(tds[8]).text()
            profit = re.search(r'[+, -]?\d+.?\d*', ninth)
            if profit is not None:
                profit = float(profit.group())
                init_dict['profit'] = profit
            """注意,平台1和平台2的列数不一样,平台1有点差,11列,平台2没有点差,10列"""
            if len(tds) == 11:
                """第十个，点差"""
                tenth = PyQuery(tds[-2]).text()
                spread_profit = float(tenth)
                init_dict['spread_profit'] = spread_profit
            else:
                pass
            """最后一个，注释"""
            eleventh = PyQuery(tds[-1]).text()
            comment = eleventh
            init_dict['comment'] = comment
    """先整理初始化字典"""
    init_dict = {k: v for k, v in init_dict.items() if v is not None}  # 去None
    """只记录指定类型的单子"""
    if init_dict['command'] in ['balance', 'credit', 'buy', 'sell']:
        return init_dict
    else:
        return None
    
    
def parse_withdraw_tr(tr: PyQuery) -> dict:
    """
    解析一页二号平台站点的出金申请的tr
    :param tr:
    :return:
    """
    init_dict = dict()
    tds = tr.find("td")
    if len(tds) < 15:
        return None
    else:
        domain = domain2
        init_dict['system'] = domain
        """第一个td,取mt帐号和mt分组"""
        first = PyQuery(tds[0])
        texts_1 = first.text().split("\n")
        account = int(re.search(r'\d{4,}', texts_1[0].lower()).group())  # mt账户
        group = texts_1[-1].lower()[5:]  # mt分组
        init_dict['account'] = account
        init_dict['group'] = group
        """第二个td，取客户2"""
        second = PyQuery(tds[1])
        init_dict['manager'] = second.text().strip()
        """第三个td，取英文名"""
        third = PyQuery(tds[2])
        texts_3 = third.text().split("\n")
        nick_name = texts_3[0][4:].strip("")
        init_dict['nick_name'] = nick_name
        """第四个，金额"""
        fourth = PyQuery(tds[3])
        texts_4 = fourth.text().split("\n")
        amount_usd = float(texts_4[0].split("$")[-1].strip())  # 金额/美元
        amount_cny = float(texts_4[-1].split("￥")[-1].strip())  # 金额/人民币
        init_dict['amount_usd'] = amount_usd
        init_dict['amount_cny'] = amount_cny
        """
        第五个，取手续费
        """
        fifth = PyQuery(tds[4])
        texts_5 = fifth.text().split("\n")
        commission_usd = float(texts_5[0].split("$")[-1].strip())  # 手续费/美元
        commission_cny = float(texts_5[-1].split("￥")[-1].strip())  # 手续费/人民币
        init_dict['commission_usd'] = commission_usd
        init_dict['commission_cny'] = commission_cny
        """
        第六个，转账方式，
        """
        sixth = PyQuery(tds[5])
        init_dict['channel'] = sixth.text().strip()
        """
        第七个，时间
        """
        seventh = PyQuery(tds[6])
        seventh = seventh.text().split("\n")
        apply_time = seventh[0][5:].strip("")
        apply_time = get_datetime_from_str(apply_time)
        close_time = seventh[-1][5:].strip("")
        close_time = get_datetime_from_str(close_time)
        init_dict['apply_time'] = apply_time
        init_dict['close_time'] = close_time
        """第八个，开户行"""
        eighth = PyQuery(tds[7]).text()
        init_dict['blank_name'] = eighth.strip()
        """第九个，开户行代码"""
        ninth = PyQuery(tds[8]).text()
        init_dict['blank_code'] = ninth.strip()
        """第十个，银行"""
        tenth = PyQuery(tds[9]).text()
        init_dict['code_id'] = tenth.strip()
        """第十一个，状态"""
        eleventh = PyQuery(tds[10]).text()
        init_dict['status'] = eleventh.strip()
        """第十二个，账户余额"""
        twelfth = PyQuery(tds[11]).text()
        init_dict['account_balance'] = float(twelfth.strip()[1:])
        """第十三个，账户净值"""
        thirteenth = PyQuery(tds[12]).text()
        init_dict['account_value'] = float(thirteenth.strip()[1:])
        """第十四个，持仓量"""
        fourteenth = PyQuery(tds[13]).text()
        init_dict['open_interest'] = float(fourteenth.strip()[0: -1])
        """第十五个，可用保证金"""
        fifteenth = PyQuery(tds[14]).text()
        init_dict['account_margin'] = float(fifteenth.strip()[1:])
        """第十六个，单号"""
        sixth = PyQuery(tds[15].find("a"))
        init_dict['ticket'] = int(sixth.attr("href").split("/")[-1])

        init_dict = {k: v for k, v in init_dict.items()}
        """只记录指定类型的单子"""
        if init_dict['status'] == "审核中":
            return init_dict
        else:
            return None


def extend_data(data1: list, data2: list, ticket_limit: int = None) -> dict:
    """
    1. 组装数组，把data2接到data1,然后返回data1,
    2. 期间检查ticket是小于限制，
    :param data1:
    :param data2:
    :param ticket_limit: ticket下限，不能小于此值
    :return:
    """
    stop = False
    if len(data2) == 0:
        pass
    else:
        time_limit = datetime.datetime.strptime("2017-11-01 0:0:0", "%Y-%m-%d %H:%M:%S")
        if len(data1) == 0:
            data2.sort(key=lambda obj: obj['ticket'], reverse=True)
            if ticket_limit is None:
                for x in data2:
                    the_time = x.get('time')
                    the_time = x.get('close_time') if the_time is None else the_time
                    print("extend_data function  {} : {} {}".format(x['ticket'], ticket_limit, the_time))
                    if the_time is not None and the_time <= time_limit:
                        stop = True
                        break
                    else:
                        data1.append(x)
            else:
                for x in data2:
                    the_time = x.get('time')
                    the_time = x.get('close_time') if the_time is None else the_time
                    print("extend_data function  {} : {} {}".format(x['ticket'], ticket_limit, the_time))
                    if (x['ticket'] - ticket_limit) <= 0 or (the_time is not None and the_time <= time_limit):
                        stop = True
                        break
                    else:
                        data1.append(x)
        else:
            """这时候的data1已经排序过了"""
            data2.sort(key=lambda obj: obj['ticket'], reverse=True)
            if ticket_limit is None:
                for x in data2:
                    the_time = x.get('time')
                    the_time = x.get('close_time') if the_time is None else the_time
                    print("extend_data function  {} : {} {}".format(x['ticket'], ticket_limit, the_time))
                    if the_time is not None and the_time <= time_limit:
                        stop = True
                        break
                    else:
                        data1.append(x)
            else:
                for x in data2:
                    the_time = x.get('time')
                    the_time = x.get('close_time') if the_time is None else the_time
                    print("extend_data function  {} : {} {}".format(x['ticket'], ticket_limit, the_time))
                    if x['ticket'] <= ticket_limit or (the_time is not None and the_time <= time_limit):
                        stop = True
                        break
                    else:
                        data1.append(x)
    return {"data": data1, "stop": stop}


def parse_page(domain: str = None, t_type: str = None, ticket_limit: int = None) -> list:
    """
    分析某一类型的页面数据，并返回结果的list,此函数必须按照交易类型分别调用
    :param domain: 平台域名
    :param t_type: 交易类型,None表示是出金申请
    :param ticket_limit: ticket下限，不能小于此值
    :return:
    """
    res = list()
    stop = False
    s = requests.Session()
    if open_platform(s, domain):
        for i in range(15, 9999999999):
            if t_type is None:
                """出金申请"""
                url = withdraw_url_base2.format(i)
                html = get_page_platform(s, url)
                records = extract_withdraw_table(html)
                if isinstance(records, list) and len(records) > 0:
                    temp = extend_data(res, records, ticket_limit)
                    res = temp['data']
                    stop = temp['stop']
                else:
                    print("stop page by empty: {}".format(url))
                    break
            else:
                url = get_page_url(domain, t_type, i)
                html = get_page_platform(s, url)
                records = extract_transaction_table(html, domain)
                count = 0
                while len(records) == 0 and count < 3:
                    time.sleep(3)
                    html = get_page_platform(s, url)
                    records = extract_transaction_table(html, domain)
                    count += 1
                if isinstance(records, list) and len(records) > 0:
                    temp = extend_data(res, records, ticket_limit)
                    res = temp['data']
                    stop = temp['stop']
                else:
                    print("stop page by empty: {}".format(url))
                    break
            if stop:
                print("stop page by flag: {}".format(url))
                break
            else:
                pass
    else:
        title = "{}打开平台失败".format(domain)
        content = "{} 平台: {}  ".format(datetime.datetime.now(), domain)
        send_mail(title=title, content=content)
        logger.exception(msg=title)
        raise ValueError(title)

    return res


def update_data(raw_data: list) -> None:
    """
    1. 更新数据库中的持仓记录，如果对应的持仓记录转为平仓就更新。
    2. 插入新的数据到数据库
    :param raw_data: 从平台抓取来的数据。包含平仓和持仓的数据。
    :return:
    """
    if len(raw_data) == 0:
        pass
    else:
        end = raw_data[0]
        type_str = end['command']
        system_str = end['system']
        insert_list = list()
        if type_str not in ['sell', 'buy']:
            insert_list = raw_data
        else:
            filter_dict = {"close_time": {"$exists": False}, "command": type_str, 'system': system_str}
            db_holdings = Transaction.find_plus(filter_dict=filter_dict, to_dict=True, projection=["_id", "ticket"])
            if len(db_holdings) == 0:
                insert_list = raw_data
            else:
                db_holdings = {x['ticket']: x["_id"] for x in db_holdings}
                tickets = db_holdings.keys()
                for x in raw_data:
                    t = x['ticket']
                    close_time = x.get('close_time')
                    if t in tickets and isinstance(close_time, datetime.datetime):
                        """持仓变平仓的记录"""
                        _id = db_holdings[t]
                        f_dict = {"_id": _id}
                        u_dict = {"$set": {"close_time": close_time}}
                        r = Transaction.find_one_and_update_plus(filter_dict=f_dict, update_dict=u_dict)
                        if r is None:
                            ms = "更新平仓信息失败,_id:{}  close_time:{}".format(_id, close_time)
                            logger.exception(ms)
                            print(ms)
                        else:
                            pass
                    else:
                        insert_list.append(x)
        if len(insert_list) > 0:
            r = Transaction.insert_many(insert_list)
            print(len(r))
        else:
            pass







if __name__ == "__main__":
    # for k in type_dict.keys():
    #     s1 = parse_page(domain1, k)
    #     try:
    #         update_data(s1)
    #     except IndexError as e:
    #         print(s1, k)
    #         raise e
    #     finally:
    #         pass
    #     s2 = parse_page(domain2, k)
    #     try:
    #         update_data(s2)
    #     except IndexError as e:
    #         print(s2, k)
    #         raise e
    #     finally:
    #         pass
    s = parse_page(domain1, 'buy')
    update_data(s)
    pass