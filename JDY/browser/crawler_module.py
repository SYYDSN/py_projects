#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from log_module import get_logger
from log_module import recode
import requests
import re
import gc
import time
import json
import datetime
import mongo_db
from module import send_moudle
from module.spread_module import SpreadChannel
from gevent.queue import JoinableQueue
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import FirefoxProfile
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import Firefox
from selenium.webdriver import ChromeOptions
from selenium.webdriver import Chrome
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import By
from pyquery import PyQuery
from mongo_db import get_datetime_from_str
from werkzeug.contrib.cache import RedisCache
from module.transaction_module import Transaction
from module.transaction_module import Withdraw
from gevent.queue import JoinableQueue
from mail_module import send_mail
from threading import Lock


send_signal = send_moudle.send_signal
ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
logger = get_logger()
cache = RedisCache()
queue = JoinableQueue()
job_key = "job_list"
cache.delete(job_key)


"""爬虫模块"""


class CustomerManagerRelation(mongo_db.BaseDoc):
    """客户和客户经理/总监的对应关系类，用来确认客户归属"""
    _table_name = 'customer_manager_relation'
    type_dict = dict()
    type_dict['_id'] = ObjectId
    type_dict['record_id'] = str  # 简道云提交过来的_id，仅仅在删除信息的时候做对应的判断。
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
    def get_relation(cls, mt4_account: str) -> dict:
        """
        JDY的这个方法不会被使用
        根据用户的mt4帐号,查询用户的归属关系
        :param mt4_account:
        :return:
        """
        f = {
            "mt4_account": mt4_account,
            "delete_date": {"$exists": False}
        }
        s = {"update_date": -1}   # 可能有重复的对象，所以要排序
        r = cls.find_one_plus(filter_dict=f, sort_dict=s, instance=False, can_json=False)
        res = dict()
        if r is None:
            res['director_name'] = ''
            res['sales_name'] = ''
            res['manager_name'] = ''
            res['customer_name'] = ''
        else:
            res['director_name'] = r['director_name']
            res['sales_name'] = r['sales_name']
            res['manager_name'] = r['manager_name']
            res['customer_name'] = r['customer_name']
        return res


chrome_driver = "/opt/google/chrome/chromedriver"  # chromedriver的路径
os.environ["ChromeDriver"] = chrome_driver  # 必须配置,否则会在execute_script的时候报错.
type_dict = {"buy": 0, "sell": 1, "balance": 6, "credit": 7}
# headers1 = {'Accept': 'text/html',
#            'Accept-Encoding': 'gzip, deflate',
#            'Accept-Charset': 'utf-8',
#            'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
#            'Connection': 'Keep-Alive',
#            'Host': 'office.shengfx888.com',
#            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#                          ' (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
# headers2 = {'Accept': 'text/html',
#            'Accept-Encoding': 'gzip, deflate',
#            'Accept-Charset': 'utf-8',
#            'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
#            'Connection': 'Keep-Alive',
#            'Host': 'office.shengfxchina.com:8443',
#            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#                          ' (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
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
login_url2 = "https://office.shengfxchina.com:8443/Public/login"
check_login_url2 = "https://office.shengfxchina.com:8443/Public/checkLogin"
domain2 = "office.shengfxchina.com:8443"
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
    """
    if browser_class == 1:
        profile = FirefoxProfile()
        profile.set_preference("intl.accept_languages", "zh-cn")
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


def upload_and_update_reg(browser, **kwargs) -> bool:
    """
    推广页面的注册用户数据传送数据到简道云
    :param browser:
    :param kwargs:
    :return:
    """
    ms = "开始向简道云推广资源表单写数据,参数: {}".format(kwargs)
    logger.info(ms)

    """
    注意，pyvirtualdisplay需要xvfb支持。安装方法：sudo apt-get install xvfb
    下载火狐的geckodriver驱动。(当前文件夹下已经有一个了)地址是：
    https://github.com/mozilla/geckodriver/releases
    下载后解压是一个geckodriver 文件。拷贝到/usr/local/bin目录下，然后加上可执行的权限
    sudo chmod +x /usr/local/bin/geckodriver
    """
    wait = WebDriverWait(browser, 10)

    url_1 = "https://www.jiandaoyun.com/f/5a658cbc7b87e86216236cb3"
    browser.get(url=url_1)  # 打开页面

    # 密码输入按钮
    input_password = wait.until(
        ec.presence_of_element_located((By.CSS_SELECTOR, ".x-layout-table input[type='password']")))
    # 提交按钮
    submit_password = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".x-layout-table .x-btn span")))

    input_password.send_keys("xundie789")  # 输入密码
    time.sleep(1)
    submit_password.click()  # 提交密码

    time.sleep(3)  # 等待是为了给页面时间载入
    # 时间选择器必须手动
    click_date = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datetime .icon-widget-datetime")))
    click_date.click()  # 弹出日期选择器
    # 修改时间
    click_today = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".dt .today")))
    click_today.click()  # 选今天

    user_name = kwargs.get('user_name')
    js_name = """let d = $(".widget-wrapper>ul>li:eq(1) input"); d.val("{}");""".format(kwargs.get('user_name'))
    browser.execute_script(js_name)  # 输入姓名

    js_phone = """let d = $(".widget-wrapper>ul>li:eq(2) input"); d.val("{}");""".format(kwargs.get('phone'))
    browser.execute_script(js_phone)  # 输入电话

    spread_keywords = SpreadChannel.analysis_url(kwargs.get('page_url'))
    desc1 = ''
    try:
        desc1 = spread_keywords[0]
    except IndexError as e:
        logger.exception("to_jiandao_cloud error!")
        recode(e)
        raise e
    except Exception as e:
        logger.exception("to_jiandao_cloud error!")
        recode(e)
        raise e
    finally:
        js_desc_1 = """let d = $(".widget-wrapper>ul>li:eq(3) input"); d.val("{}");""".format(desc1)
        browser.execute_script(js_desc_1)  # 备注1

    desc2 = ''
    try:
        desc2 = spread_keywords[1]
    except IndexError as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(e)
    finally:
        js_desc_2 = """let d = $(".widget-wrapper>ul>li:eq(4) input"); d.val("{}");""".format(desc2)
        browser.execute_script(js_desc_2)  # 备注2

    desc3 = ''
    try:
        desc3 = spread_keywords[2]
    except IndexError as e:
        recode(e)
        logger.exception(e)
    except Exception as e:
        recode(e)
        logger.exception(e)
    finally:
        js_desc_3 = """let d = $(".widget-wrapper>ul>li:eq(5) input"); d.val("{}");""".format(desc3)
        browser.execute_script(js_desc_3)  # 备注3

    desc6 = kwargs.get('page_url')
    desc6 = '' if desc6 is None else desc6
    js_desc_6 = """let d = $(".widget-wrapper>ul>li:eq(6) input"); d.val("{}");""".format(desc6)
    browser.execute_script(js_desc_6)  # 页面链接

    desc7 = kwargs.get('description')
    desc7 = '' if desc7 is None else desc7
    js_desc_7 = """let d = $(".widget-wrapper>ul>li:eq(7) input"); d.val("{}");""".format(desc7)
    browser.execute_script(js_desc_7)  # 页面内容

    desc8 = kwargs.get('search_keyword')
    desc8 = '' if desc8 is None else desc8
    js_desc_8 = """let d = $(".widget-wrapper>ul>li:eq(9) input"); d.val("{}");""".format(desc8)
    browser.execute_script(js_desc_8)  # 搜索关键字

    """
    如果查找器没有定位到dom元素或者页面尚未载入,会报如下的错误.
    selenium.common.exceptions.WebDriverException: Message: unknown error: cannot focus element
    """
    """ec.presence_of_all_elements_located方法可以取一组输入框,然后循环操作"""
    input_list = wait.until(
        ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".widget-wrapper>ul>li input")))  # 输入组
    ms = "简道云推广资源表单胡据填充完毕,准备提交"
    logger.info(ms)
    recode(ms)
    submit_info = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".x-btn span")))  # 提交资料按钮
    submit_info.click()  # 提交信息

    time.sleep(1)

    # browser.refresh()  # 刷新页面

    time.sleep(10)
    ms = "向简道云推广资源表单写数据成功,参数: {}".format(kwargs)
    logger.info(ms)
    recode(ms)
    return True


def get_page_url(domain: str, transaction: str, page_num: int = 1) -> str:
    """
    获取一号/二号平台综合业务网址
    :param domain: 基础网址
    :param transaction: 交易类型， buy/sell/balance/credit
    :param page_num:
    :return:
    """
    if domain == domain1:
        _base = __page_url_base1
    else:
        _base = __page_url_base2
    r = _base.format(type_dict[transaction], page_num)
    return r


def login_platform(browser, domain: str):
    """
    登录一号/二号平台
    :param browser:
    :param domain:
    :return:requests.Session
    """
    if domain == domain1:
        url = login_url1
        user_name = user_name1
        user_password = user_password1

    else:
        url = login_url2
        user_name = user_name2
        user_password = user_password2

    browser.get(url=url)
    # recode("html= {}".format(browser.page_source))
    # 用户名输入
    input_user_name = WebDriverWait(browser, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "form .uname")))
    input_user_name.send_keys(user_name)  # 输入用户名
    # 用户密码输入
    input_user_password = WebDriverWait(browser, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "form .pword")))
    input_user_password.send_keys(user_password)  # 输入用户密码
    # 点击登录按钮
    button_login = WebDriverWait(browser, 10).until(
        ec.presence_of_element_located((By.ID, "loginbtn")))  # 注意,这里用的不是css选择器而是id选择器
    button_login.click()  # 登录

    time.sleep(10)
    return True


def need_login_platform(browser) -> bool:
    """
    一号/二号平台是否需要登录？
    :param browser:
    :return: True需要登录，False，不需要登录
    """
    if browser.current_url.startswith("http://office.shengfx888.com/Public/login?") or \
            browser.current_url.startswith("https://office.shengfxchina.com:8443/Public/login"):
        return True
    else:
        return False


def open_platform(browser, domain: str) -> bool:
    """
    打开一号/二号平台站点,如果已经登录,返回True,否则尝试重新login,三次失败后,返回False
    :param browser:
    :param domain:
    :return: 布尔值 True开打成功，False，打开失败，请检查程序
    """
    if domain == domain1:
        url = page_url_base1
    else:
        url = page_url_base2

    try:
        browser.get(url)
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
            login_platform(browser=browser, domain=domain)

        browser.get(url)
        return not need_login_platform(browser)


def get_page_platform(browser, page_url: str) -> (PyQuery, None):
    """
    获取一页一号/二号平台站点的页面html,包含交易和出金申请,返回页面内容的PQuery对象
    :param browser:
    :param page_url: 页面网址
    :return:
    """
    try:
        browser.get(page_url)
    except TimeoutException as e:
        title = "{} 打开页面失败".format(datetime.datetime.now())
        content = "错误原因：{}".format(e)
        send_mail(title=title, content=content)
        print(page_url)
        ms = "Error {} on {}".format(page_url, e)
        recode(ms)
        raise e
    except Exception as e:
        title = "{} 打开页面失败".format(datetime.datetime.now())
        content = "错误原因：{}".format(e)
        send_mail(title=title, content=content)
        print(e)
        ms = "Error {} on {}".format(page_url, e)
        recode(ms)
        raise e
    source = browser.page_source
    html = PyQuery(source)
    return html


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
    ms = "begin parse_transaction_tr"
    recode(ms)
    init_dict = dict()
    tds = tr.find("td")
    """平台1和平台2区别对待"""
    if domain == domain1:
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
            if command.lower() in ['buy', 'sell']:
                seventh = PyQuery(tds[6])
                seventh = seventh.text().split("\n")
                if len(seventh) < 2:
                    """只有手续费"""
                    commission_match = re.search(r'[+, -]?\d+.?\d*', seventh[-1])
                    if commission_match is not None:
                        commission = float(commission_match.group())  # 手续费
                    else:
                        commission = None
                else:
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
            第七个，利息/佣金，
            """
            if command.lower() in ['buy', 'sell']:
                seventh = PyQuery(tds[6])
                seventh = seventh.text().split("\n")
                if len(seventh) < 2:
                    """只有手续费"""
                    commission_match = re.search(r'[+, -]?\d+.?\d*', seventh[-1])
                    if commission_match is not None:
                        commission = float(commission_match.group())  # 手续费
                    else:
                        commission = None
                else:
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

            """第十个，点差"""
            tenth = PyQuery(tds[-2]).text()
            spread_profit = float(tenth)
            init_dict['spread_profit'] = spread_profit

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
    ms = "begin parse_withdraw_tr"
    recode(ms)
    if len(tds) < 10:
        return None
    else:
        domain = domain2
        init_dict['system'] = domain
        """第一个td,取mt帐号和mt分组"""
        first = PyQuery(tds[0])
        texts_1 = first.text().split("\n")
        account = int(re.search(r'\d{4,}', texts_1[0].lower()).group())  # mt账户
        init_dict['account'] = account
        """第二个td，取客户2"""
        second = PyQuery(tds[1])
        init_dict['nick_name'] = second.text().split("\n")[0].split("：")[-1].strip()
        """第三个td，金额"""
        fourth = PyQuery(tds[2])
        texts_4 = fourth.text().split("\n")
        amount_usd = float(texts_4[0].split("$")[-1].strip())  # 金额/美元
        amount_cny = float(texts_4[-1].split("￥")[-1].strip())  # 金额/人民币
        init_dict['amount_usd'] = amount_usd
        init_dict['amount_cny'] = amount_cny
        """
        第四个，取手续费
        """
        fifth = PyQuery(tds[3])
        texts_5 = fifth.text().split("\n")
        commission_usd = float(texts_5[0].split("$")[-1].strip())  # 手续费/美元
        commission_cny = float(texts_5[-1].split("￥")[-1].strip())  # 手续费/人民币
        init_dict['commission_usd'] = commission_usd
        init_dict['commission_cny'] = commission_cny
        """
        第五个，转账方式，
        """
        sixth = PyQuery(tds[4])
        init_dict['channel'] = sixth.text().strip()
        """
        第六个，时间
        """
        seventh = PyQuery(tds[5])
        seventh = seventh.text().split("\n")
        apply_time = seventh[0][5:].strip("")
        apply_time = get_datetime_from_str(apply_time)
        close_time = seventh[-1][5:].strip("")
        close_time = get_datetime_from_str(close_time)
        init_dict['apply_time'] = apply_time
        init_dict['close_time'] = close_time
        """第七个，开户行"""
        eighth = PyQuery(tds[6]).text()
        init_dict['blank_name'] = eighth.strip()
        """第八个，银行卡号"""
        tenth = PyQuery(tds[7]).text()
        init_dict['code_id'] = tenth.strip()
        """第九个，状态"""
        eleventh = PyQuery(tds[8]).text()
        init_dict['status'] = eleventh.strip()
        """第十个，账户余额"""
        twelfth = PyQuery(tds[9]).text()
        init_dict['account_balance'] = float(twelfth.strip()[1:])
        """第十一个，账户净值"""
        thirteenth = PyQuery(tds[10]).text()
        init_dict['account_value'] = float(thirteenth.strip()[1:])
        """第十二个，持仓量"""
        fourteenth = PyQuery(tds[11]).text()
        init_dict['open_interest'] = float(fourteenth.strip()[0: -1])
        """第十三个，可用保证金"""
        fifteenth = PyQuery(tds[12]).text()
        init_dict['account_margin'] = float(fifteenth.strip()[1:])
        """第十四个，单号"""
        sixth = PyQuery(tds[13].find("a"))
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
                    print("query_withdraw  {} : {} {}".format(x['ticket'], ticket_limit, the_time))
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


def parse_page(browser, domain: str = None, t_type: str = None, ticket_limit: int = None) -> list:
    """
    分析某一类型的页面数据（包含交易和出金申请），并返回结果的list,此函数必须按照交易类型分别调用
    :param browser:
    :param domain: 平台域名
    :param t_type: 交易类型,None表示是出金申请
    :param ticket_limit: ticket下限，不能小于此值
    :return:
    """
    res = list()
    stop = False
    # browser = get_browser(False)
    if open_platform(browser, domain):
        for i in range(1, 9999999999):
            if t_type is None:
                """出金申请"""
                url = withdraw_url_base2.format(i)
                html = get_page_platform(browser, url)
                records = extract_withdraw_table(html)
                if isinstance(records, list) and len(records) > 0:
                    temp = extend_data(res, records, ticket_limit)
                    res = temp['data']
                    stop = temp['stop']
                else:
                    ms = "stop page by empty: {}".format(url)
                    print(ms)
                    recode(ms)
                    break
            else:
                """buy, sell, balance credit"""
                url = get_page_url(domain, t_type, i)
                html = get_page_platform(browser, url)
                records = extract_transaction_table(html, domain)
                if isinstance(records, list) and len(records) > 0:
                    temp = extend_data(res, records, ticket_limit)
                    res = temp['data']
                    stop = temp['stop']
                else:
                    ms = "stop page by empty: {}".format(url)
                    print(ms)
                    recode(ms)
                    break
            if stop:
                ms = "stop page by flag: {}".format(url)
                print(ms)
                recode(ms)
                break
            else:
                pass
    else:
        title = "{}打开平台失败".format(domain)
        content = "{} 平台: {}  ".format(datetime.datetime.now(), domain)
        send_mail(title=title, content=content)
        logger.exception(msg=title)
        raise ValueError(title)
    """去除已上传的数据"""
    if len(res) > 0:
        if t_type is None:
            """出金申请"""
            f_dict = {"upload": 1}
            uploads = Withdraw.find_plus(filter_dict=f_dict, to_dict=True)
            if len(uploads) == 0:
                pass
            else:
                tickets = [x['ticket'] for x in uploads]
                res = [x for x in res if x['ticket'] not in tickets]
        else:
            system_str = res[0]['system']
            uploads = get_uploaded_transaction()
            if len(uploads) == 0:
                pass
            else:
                tickets = uploads.get(system_str)
                if isinstance(tickets, list):
                    res = [x for x in res if x['ticket'] not in tickets]
    return res


def save_transaction_data(raw_data: list) -> list:
    """
    1. 保存并更新数据库中的交易记录，如果有对应的持仓记录转为平仓就更新他们。
    2. 插入新的数据到数据库
    :param raw_data: 从平台抓取来的数据。包含平仓和持仓的数据。
    :return: 需要插入的数据
    """
    if len(raw_data) == 0:
        pass
    else:
        end = raw_data[0]
        type_str = end['command']
        system_str = end['system']
        insert_list = list()
        if type_str not in ['sell', 'buy']:
            """
            credit和balance类型的单子，
            无需要考虑持仓变平仓的问题，
            所有的新数据直接插入。
            直接保存即可。
            """
            insert_list = raw_data
        else:
            """
            buy和sell类型的单子。
            分四种情况：
            1. 抓取到的是新单子。处于平仓状态的。写入。
            2. 抓取到的是旧单子。处于平常状态的。update
            3. 抓取到的是新单子。处于持仓状态的。写入
            4. 抓取带的是旧单子。处于持仓状态的。放弃
            """
            filter_dict = {"close_time": {"$exists": False}, "command": type_str, 'system': system_str}
            """查找处于持仓状态的单子，用于应对以上的2/3/4状态中的比较"""
            db_holdings = Transaction.find_plus(filter_dict=filter_dict, to_dict=True, projection=["_id", "ticket"])
            if len(db_holdings) == 0:
                insert_list = raw_data
            else:
                db_holdings = {x['ticket']: x["_id"] for x in db_holdings}
                tickets = db_holdings.keys()
                for x in raw_data:
                    t = x['ticket']
                    close_time = x.get('close_time')  # 抓取到的数据的平仓时间
                    """检查抓取到的数据是否有平仓记录并且是持仓变平仓的状态，"""
                    if t in tickets and isinstance(close_time, datetime.datetime):
                        """持仓变平仓的记录"""
                        _id = db_holdings[t]
                        f_dict = {"_id": _id}
                        u_dict = {
                            "$set":
                                {
                                    "close_time": close_time,   # 平仓时间
                                    "profit": x.get("profit"),  # 盈亏
                                    "exit_price": x.get("exit_price"),
                                    "swap": x.get("swap"),
                                    "spread_profit": x.get("spread_profit"),
                                    "description": x.get("description")
                            }
                        }
                        """update持仓变平仓的记录"""
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
            """保存抓取到的四种交易的订单信息"""
            r = Transaction.insert_many(insert_list)
            ms = "save_transaction_data success"
            recode(ms)
            return r
        else:
            pass


def save_withdraw_data(raw_data: list) -> list:
    """
    1. 更新数据库中的出金申请。
    :param raw_data: 从平台抓取来的出金申请数据。
    :return:
    """
    if len(raw_data) == 0:
        return raw_data
    else:
        last = Withdraw.last_record(domain2)
        if last is not None:
            raw_data = [x for x in raw_data if x['ticket'] > last['ticket']]
        else:
            pass
        r = Withdraw.insert_many(raw_data)
        """向机器人消息服务器发送出金申请消息"""
        send_all_withdraw_signal()
        ms = "save_withdraw_data success"
        recode(ms)
        return r


def send_all_withdraw_signal():
    """
    从数据库查询所有未发送过消息的出金申请，并依次发送信号给机器人服务器
    :return:
    """
    f = {"$or": [
        {"send_signal": {"$exists": False}},
        {"send_signal": {"$ne": 1}}
    ]}
    res = Withdraw.find_plus(filter_dict=f, to_dict=False)
    for obj in res:
        d = obj.__dict__
        r = send_withdraw_signal(d)
        if r:
            """发送到机器人成功"""
            obj.set_attr("send_signal", 1)
            obj.save_plus()
        else:
            pass


def send_withdraw_signal(reg_info: dict):
    """
    发送出金信息到钉订机器人的消息服务器
    :param reg_info:
    :return:
    """
    out_put = dict()
    markdown = dict()
    token_name = "钉订小助手"
    out_put['msgtype'] = 'markdown'
    markdown['title'] = "出金申请"
    system_info = reg_info['system']
    apply_time = reg_info['apply_time']
    apply_time = apply_time.strftime("%Y年%m月%d日 %H:%M:%S")
    mt4_account = reg_info['account']
    relation = CustomerManagerRelation.get_relation(mt4_account)
    customer_name = reg_info['nick_name']
    sales_name = relation['sales_name']
    manager_name = relation['manager_name']
    director_name = relation['director_name']
    amount_usd = reg_info['amount_usd']
    open_interest = reg_info['open_interest']
    account_balance = reg_info['account_balance']
    markdown['text'] = "> 出金申请 \r\n >提交时间：{} \r\n > 所属平台：{} \r\n > MT帐号：{} \r\n > 客户姓名：{} \r\n > " \
                       "出金金额:{} \r\n > 目前持仓手数:{} \r\n > 目前余额：{} \r\n > 所属员工:{} \r\n > 所属经理：{} \r\n " \
                       "> 所属总监:{}".format(apply_time, system_info, mt4_account, customer_name, amount_usd,
                                          open_interest, account_balance, sales_name, manager_name, director_name)
    out_put['markdown'] = markdown
    out_put['at'] = {'atMobiles': [], 'isAtAll': False}
    res = send_signal(out_put, token_name=token_name)
    print(res)
    return res


def upload_transaction(browser, **kwargs) -> bool:
    """
    上传所有的出入金,赠金,已平仓的buy和sell记录
    :param browser:
    :return:
    """
    command = kwargs['command']
    open_time = kwargs['time'] if command in ["credit", "balance"] else kwargs['open_time']
    close_time = kwargs['time'] if command in ["credit", "balance"] else kwargs.get('close_time')
    close_time = '' if close_time is None else close_time
    if close_time == "":
        pass  # 持仓中的单子不需要记录
    else:
        browser = browser
        url_1 = "https://jiandaoyun.com/f/5a9cf444dc9e7a6325f7684f"
        browser.get(url=url_1)  # 打开页面
        wait = WebDriverWait(browser, 10)

        """检查是否需要登录"""
        js_find = """return $(".password-write-tip>a").text();"""
        if browser.execute_script(js_find) == "填写该表单需输入密码，请输入密码：":
            """需要登录"""
            print("需要登录")
            # 密码输入按钮
            input_password = wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, ".x-layout-table input[type='password']")))
            # 提交按钮
            submit_password = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".x-layout-table .x-btn span")))

            input_password.send_keys("XunDie963741")  # 输入密码
            time.sleep(1)
            submit_password.click()  # 提交密码
        else:
            print("不需要登录")

        # 等待直到表单填写页面完全载入
        time.sleep(5)

        create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        js_create_time = """let d = $(".widget-wrapper>ul>li:eq(0) input"); d.val("{}");""".format(create_time)
        browser.execute_script(js_create_time)  # 输入创建时间

        system_name = kwargs.get('system')
        js_system_name = """let d = $(".widget-wrapper>ul>li:eq(1) input"); d.val("{}");""".format(system_name)
        browser.execute_script(js_system_name)

        ticket = kwargs.get('ticket')
        js_ticket = """let d = $(".widget-wrapper>ul>li:eq(2) input"); d.val("{}");""".format(ticket)
        browser.execute_script(js_ticket)

        js_login = """let d = $(".widget-wrapper>ul>li:eq(3) input"); d.val("{}");""".format(kwargs['login'])
        browser.execute_script(js_login)  # 输入mt账户
        js_blur = """$(".widget-wrapper>ul>li:eq(3) input").blur();"""
        browser.execute_script(js_blur)  # blur激活关联
        time.sleep(3)  # 等待3秒,让关联生效

        js_real_name = """let d = $(".widget-wrapper>ul>li:eq(4) input"); d.val("{}");""".format(kwargs['real_name'])
        browser.execute_script(js_real_name)  # 输入用户姓名

        js_command = """let d = $(".widget-wrapper>ul>li:eq(8) input"); d.val("{}");""".format(command)
        browser.execute_script(js_command)  # 输入交易类型

        symbol = '' if kwargs.get('symbol') is None else kwargs['symbol']
        js_symbol = """let d = $(".widget-wrapper>ul>li:eq(9) input"); d.val("{}");""".format(symbol)
        browser.execute_script(js_symbol)  # 输入产品

        lot = 0 if kwargs.get('lot') is None or kwargs.get('lot') is None == "" else kwargs['lot']
        js_lot = """let d = $(".widget-wrapper>ul>li:eq(10) input"); d.val("{}");""".format(lot)
        browser.execute_script(js_lot)  # 输入手数

        enter_price = '' if kwargs.get("enter_price") is None else kwargs['enter_price']
        js_enter_price = """let d = $(".widget-wrapper>ul>li:eq(11) input"); d.val("{}");""".format(enter_price)
        browser.execute_script(js_enter_price)  # 建仓点位

        exit_price = '' if kwargs.get("exit_price") is None else kwargs['exit_price']
        js_exit_price = """let d = $(".widget-wrapper>ul>li:eq(12) input"); d.val("{}");""".format(exit_price)
        browser.execute_script(js_exit_price)  # 平仓点位

        profit = '' if kwargs.get("profit") is None else kwargs['profit']
        js_profit = """let d = $(".widget-wrapper>ul>li:eq(13) input"); d.val("{}");""".format(profit)
        browser.execute_script(js_profit)  # 盈亏

        commission = '' if kwargs.get("commission") is None else kwargs['commission']
        js_commission = """let d = $(".widget-wrapper>ul>li:eq(14) input"); d.val("{}");""".format(commission)
        browser.execute_script(js_commission)  # 佣金

        swap = '' if kwargs.get("swap") is None else kwargs['swap']
        js_swap = """let d = $(".widget-wrapper>ul>li:eq(15) input"); d.val("{}");""".format(swap)
        browser.execute_script(js_swap)  # 利息

        spread_profit = '' if kwargs.get("spread_profit") is None else kwargs['spread_profit']
        js_spread_profit = """let d = $(".widget-wrapper>ul>li:eq(16) input"); d.val("{}");""".format(spread_profit)
        browser.execute_script(js_spread_profit)  # 点差

        comment = '' if kwargs.get("comment") is None else kwargs['comment']
        js_comment = """let d = $(".widget-wrapper>ul>li:eq(17) input"); d.val("{}");""".format(comment)
        browser.execute_script(js_comment)  # 注释

        """输入建仓时间"""
        if isinstance(open_time, datetime.datetime):
            click_date = wait.until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datetime[widgetname='_widget_1520834605640'] "
                                                             ".icon-widget-datetime")))
            click_date.click()  # 弹出日期选择器
            date_title = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datepicker .title")))
            date_title.click()  # 弹出年份和月份选择
            m_str = month_str(open_time.month)
            y_str = str(open_time.year)
            d_str = str(open_time.day)
            hour_str = str(open_time.hour)
            minute_str = str(open_time.minute)
            second_str = str(open_time.second)
            months = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .month")))
            """选择月份"""
            for month in months:
                if month.text == m_str:
                    month.click()
                    break
                else:
                    pass
            years = wait.until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .year")))
            """选择年份"""
            for year in years:
                if year.text == y_str:
                    year.click()
                    break
                else:
                    pass
            """点击月份和年份界面的确定按钮"""
            btn_1 = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datepicker .ok[colspan='4']")))
            btn_1.click()
            days = wait.until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .day")))
            """选择天"""
            for day in days:
                if day.text == d_str:
                    day.click()
                    break
                else:
                    pass
            """修改小时,分钟,秒"""
            tds = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .tt td")))
            hour = tds[1].find_element_by_tag_name("input")
            minute = tds[3].find_element_by_tag_name("input")
            second = tds[5].find_element_by_tag_name("input")
            hour.clear()
            hour.send_keys(hour_str)
            minute.clear()
            minute.send_keys(minute_str)
            second.clear()
            second.send_keys(second_str)
            """点击最后的确定按钮"""
            btn_2 = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datepicker .ok[colspan='2']")))
            btn_2.click()

        """输入平仓时间"""
        if isinstance(close_time, datetime.datetime):
            click_date = wait.until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datetime[widgetname='_widget_1520834605650'] "
                                                             ".icon-widget-datetime")))
            click_date.click()  # 弹出日期选择器
            date_title = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datepicker .title")))
            date_title.click()  # 弹出年份和月份选择
            m_str = month_str(close_time.month)
            y_str = str(close_time.year)
            d_str = str(close_time.day)
            hour_str = str(close_time.hour)
            minute_str = str(close_time.minute)
            second_str = str(close_time.second)
            months = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .month")))
            """选择月份"""
            for month in months:
                if month.text == m_str:
                    month.click()
                    break
                else:
                    pass
            years = wait.until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .year")))
            """选择年份"""
            for year in years:
                if year.text == y_str:
                    year.click()
                    break
                else:
                    pass
            """点击月份和年份界面的确定按钮"""
            btn_1 = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datepicker .ok[colspan='4']")))
            btn_1.click()
            days = wait.until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .day")))
            """选择天"""
            for day in days:
                if day.text == d_str:
                    day.click()
                    break
                else:
                    pass
            """修改小时,分钟,秒"""
            tds = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .tt td")))
            hour = tds[1].find_element_by_tag_name("input")
            minute = tds[3].find_element_by_tag_name("input")
            second = tds[5].find_element_by_tag_name("input")
            hour.clear()
            hour.send_keys(hour_str)
            minute.clear()
            minute.send_keys(minute_str)
            second.clear()
            second.send_keys(second_str)
            """点击最后的确定按钮"""
            btn_2 = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datepicker .ok[colspan='2']")))
            btn_2.click()

        profit = kwargs.get('profit')
        profit = '' if profit is None else profit
        js_profit = """let d = $(".widget-wrapper>ul>li:eq(20) input"); d.val("{}");""".format(profit)
        browser.execute_script(js_profit)  # 盈利点数

        time.sleep(1)
        submit_info = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".x-btn span")))  # 提交资料按钮
        submit_info.click()  # 提交信息
        time.sleep(3)

        res = False
        try:
            msg_span = WebDriverWait(browser, 10).until(ec.presence_of_element_located((
                By.CLASS_NAME, "msg-title")))
            print(msg_span.get_attribute("class"))
            print(msg_span.text)
            if msg_span.get_attribute("class") == "msg-title":
                """操作成功"""
                browser.refresh()  # 刷新页面
                ms = "upload transaction success"
                recode(ms)
                res = True
            else:
                ms = "upload transaction fail"
                recode(ms)
                pass  # 添加数据失败
        except Exception as e:
            print(e)
            ms = str(e)
            recode(ms)
            logger.exception(e)
        finally:
            return res


def upload_withdraw(browser, **kwargs) -> bool:
    """
    上传出金的记录
    :param browser: 。
    :return:
    """
    browser = browser
    url_withdraw = "https://jiandaoyun.com/f/5a9cf2441fc6e726b6f08f8c"  # 出金记录表地址
    browser.get(url=url_withdraw)  # 打开页面
    wait = WebDriverWait(browser, 10)

    """检查是否需要登录"""
    js_find = """return $(".password-write-tip>a").text();"""
    if browser.execute_script(js_find) == "填写该表单需输入密码，请输入密码：":
        """需要登录"""
        print("需要登录")
        # 密码输入按钮
        input_password = wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".x-layout-table input[type='password']")))
        # 提交按钮
        submit_password = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".x-layout-table .x-btn span")))

        input_password.send_keys("XunDie963741")  # 输入密码
        time.sleep(1)
        submit_password.click()  # 提交密码
        time.sleep(3)  # 等待是为了给页面时间载入
    else:
        print("不需要登录")

    apply_time = kwargs.get('apply_time')
    """输入申请时间"""
    if isinstance(apply_time, datetime.datetime):
        click_date = wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datetime[widgetname='_widget_1520917209957'] "
                                                         ".icon-widget-datetime")))
        click_date.click()  # 弹出日期选择器
        date_title = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datepicker .title")))
        date_title.click()  # 弹出年份和月份选择
        m_str = month_str(apply_time.month)
        y_str = str(apply_time.year)
        d_str = str(apply_time.day)
        hour_str = str(apply_time.hour)
        minute_str = str(apply_time.minute)
        second_str = str(apply_time.second)
        months = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .month")))
        """选择月份"""
        for month in months:
            if month.text == m_str:
                month.click()
                break
            else:
                pass
        years = wait.until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .year")))
        """选择年份"""
        for year in years:
            if year.text == y_str:
                year.click()
                break
            else:
                pass
        """点击月份和年份界面的确定按钮"""
        btn_1 = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datepicker .ok[colspan='4']")))
        btn_1.click()
        days = wait.until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .day")))
        """选择天"""
        for day in days:
            if day.text == d_str:
                day.click()
                break
            else:
                pass
        """修改小时,分钟,秒"""
        tds = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".fui_datepicker .tt td")))
        hour = tds[1].find_element_by_tag_name("input")
        minute = tds[3].find_element_by_tag_name("input")
        second = tds[5].find_element_by_tag_name("input")
        hour.clear()
        hour.send_keys(hour_str)
        minute.clear()
        minute.send_keys(minute_str)
        second.clear()
        second.send_keys(second_str)
        """点击最后的确定按钮"""
        btn_2 = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".fui_datepicker .ok[colspan='2']")))
        btn_2.click()

    """输入平台地址"""
    system_name = kwargs['system']
    js_system = """let d = $(".widget-wrapper>ul>li:eq(1) input"); d.val("{}");""".format(system_name)
    browser.execute_script(js_system)

    """输入申请单号"""
    ticket = kwargs.get('ticket')
    js_ticket = """let d = $(".widget-wrapper>ul>li:eq(2) input"); d.val("{}");""".format(ticket)
    browser.execute_script(js_ticket)  # 输入单号

    js_login = """let d = $(".widget-wrapper>ul>li:eq(3) input"); d.val("{}");""".format(kwargs['account'])
    browser.execute_script(js_login)  # 输入mt账户

    js_real_name = """let d = $(".widget-wrapper>ul>li:eq(4) input"); d.val("{}");""".format(kwargs['nick_name'])
    browser.execute_script(js_real_name)  # 输入用户姓名
    js_blur = """$(".widget-wrapper>ul>li:eq(4) input").blur();"""
    browser.execute_script(js_blur)  # blur激活关联
    time.sleep(3)  # 等待3秒,让关联生效

    profit = kwargs['amount_usd']
    js_profit = """let d = $(".widget-wrapper>ul>li:eq(8) input"); d.val("{}");""".format(profit)
    browser.execute_script(js_profit)  # 出金/入金金额

    open_interest = kwargs['open_interest']
    js_open_interest = """let d = $(".widget-wrapper>ul>li:eq(9) input"); d.val("{}");""".format(open_interest)
    browser.execute_script(js_open_interest)  # 持仓量

    account_value = kwargs['account_value']
    js_account_value = """let d = $(".widget-wrapper>ul>li:eq(10) input"); d.val("{}");""".format(account_value)
    browser.execute_script(js_account_value)  # 净值

    account_margin = kwargs['account_margin']
    js_account_margin = """let d = $(".widget-wrapper>ul>li:eq(11) input"); d.val("{}");""".format(account_margin)
    browser.execute_script(js_account_margin)  # 可用保证金

    account_balance = kwargs['account_balance']
    js_account_balance = """let d = $(".widget-wrapper>ul>li:eq(12) input"); d.val("{}");""".format(account_balance)
    browser.execute_script(js_account_balance)  # 余额

    blank_name = kwargs['blank_name']
    js_blank_name = """let d = $(".widget-wrapper>ul>li:eq(13) input"); d.val("{}");""".format(blank_name)
    browser.execute_script(js_blank_name)  # 银行

    code_id = kwargs['code_id']
    js_code_id = """let d = $(".widget-wrapper>ul>li:eq(14) input"); d.val("{}");""".format(code_id)
    browser.execute_script(js_code_id)  # 银行账号

    submit_info = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".x-btn span")))  # 提交资料按钮
    submit_info.click()  # 提交信息
    time.sleep(3)

    res = False
    try:
        msg_span = WebDriverWait(browser, 10).until(ec.presence_of_element_located((
            By.CLASS_NAME, "msg-title")))
        print(msg_span.get_attribute("class"))
        print(msg_span.text)
        if msg_span.get_attribute("class") == "msg-title":
            """操作成功"""
            browser.refresh()  # 刷新页面
            ms = "upload withdraw success"
            recode(ms)
            res = True
        else:
            ms = "upload withdraw fail"
            recode(ms)
            pass  # 添加数据失败
    except Exception as e:
        print(e)
        ms = str(e)
        recode(ms)
        logger.exception(e)
    finally:
        return res


def get_uploaded_transaction() -> dict:
    """
    获取已上传的交易数据,用于去重
    :return:
    """
    ses = mongo_db.get_conn("transaction_info")
    system_names = ses.distinct("system")
    filter_dict = {"upload": 1}
    if len(system_names) == 0:
        return dict()
    else:
        data = dict(zip(system_names, [list() for i in range(len(system_names))]))
        records = Transaction.find_plus(filter_dict=filter_dict, projection=['system', 'ticket'], to_dict=True)
        for x in records:
            domain = x['system']
            temp = data[domain]
            temp.append(x['ticket'])
            data[domain] = temp
        return data


def query_transaction(upload: bool = True, only_transaction: bool = False) ->list:
    """
    从数据库查询buy, sell交易。
    :param upload: 是否只查需要上传的？
    :param only_transaction: 是否只包含交易信息？ True=['sell', 'buy']  False=['sell', 'buy'， ‘balance', 'credit]
    :return:
    """
    types = ['sell', 'buy'] if only_transaction else ['sell', 'buy', 'balance', 'credit']
    if upload:
        if only_transaction:
            filter_dict = {
                "close_time": {"$exists": True}, 'command': {'$in': ['sell', 'buy']},
                "$or": [{"upload": {"$ne": 1}}, {"upload": {"$exists": False}}]
            }
        else:
            filter_dict = {"$and": [
                {"$or": [{"upload": {"$ne": 1}}, {"upload": {"$exists": False}}]},
                {"$or": [
                    {"close_time": {"$exists": True}, 'command': {'$in': ['sell', 'buy']}},
                    {"time": {"$exists": True}, 'command': {'$in': ['balance', 'credit']}},
                ]}
              ]
            }
    else:
        if only_transaction:
            filter_dict = {'command': {'$in': ['sell', 'buy']}}
        else:
            filter_dict = dict()
    sort_dict = {"close_time": 1, "time": 1}
    r = Transaction.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, to_dict=True)
    ms = "query transaction success"
    recode(ms)
    return r


def query_withdraw(upload: bool = True) ->dict:
    """
    从数据库查询出金申请。出入金和赠金记录
    :param upload: 是否只查需要上传的？
    :return:
    """
    if upload:
        filter_dict = {"$or": [{"upload": {"$ne": 1}}, {"upload": {"$exists": False}}]}
    else:
        filter_dict = dict()
    sort_dict = {"apply_time": 1}
    withdraw = Withdraw.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, to_dict=True)
    sort_dict = {"time": 1}
    filter_dict['command'] = {"$in": ['balance', 'credit']}
    other = Transaction.find_plus(filter_dict=filter_dict, sort_dict=sort_dict, to_dict=True)
    ms = "query withdraw success!"
    recode(ms)
    return {"withdraw": withdraw, "other": other}


def upload_and_update_transaction(browser, **kwargs):
    """
    上传交易信息并更新数据库
    :param browser:
    :param kwargs:
    :return:
    """
    res = upload_transaction(browser, **kwargs)
    count = 0
    while not res and count <= 3:
        ms = "上传出金申请失败,实例:{}".format(kwargs)
        print(ms)
        count += 1
        time.sleep(3)
    if not res:
        ms = "上传交易信息已连续失败{}次,实例:{}".format(count, kwargs)
        raise ValueError(ms)
    else:
        """上传成功,更新数据库的upload标识"""
        filter_dict = {"_id": kwargs["_id"]}
        update_dict = {"$set": {"upload": 1}}
        res = Transaction.find_one_and_update_plus(filter_dict=filter_dict, update_dict=update_dict)
        if res:
            ms = "{} {} success".format(kwargs['system'], kwargs['ticket'])
            print(ms)
            recode(ms)
            return True
        else:
            ms = "更新出金申请数据库的upload标识失败,实例:{}".format(count, kwargs)
            recode(ms)
            raise ValueError(ms)


def upload_and_update_withdraw(browser, **kwargs):
    """
    上传交易信息并更新数据库
    :param browser:
    :param kwargs:
    :return:
    """
    res = upload_withdraw(browser, **kwargs)
    count = 0
    while not res and count <= 3:
        ms = "上传出金申请失败,实例:{}".format(kwargs)
        print(ms)
        count += 1
        time.sleep(3)
    if not res:
        ms = "上传出金申请已连续失败{}次,实例:{}".format(count, kwargs)
        recode(ms)
        raise ValueError(ms)
    else:
        """上传出金申请成功,更新数据库的upload标识"""
        filter_dict = {"_id": kwargs.get("_id")}
        update_dict = {"$set": {"upload": 1}}
        res = Withdraw.find_one_and_update_plus(filter_dict=filter_dict, update_dict=update_dict)
        if res:
            ms = "{} {} success".format(kwargs['system'], kwargs['ticket'])
            print(ms)
            recode(ms)
            return True
        else:
            ms = "更新出金申请数据库的upload标识失败,实例:{}".format(count, kwargs)
            recode(ms)
            raise ValueError(ms)


def draw_transaction(browser):
    """
    从站点上查询buy和sell数据
    :return:
    """
    names = [domain2, domain1]
    limits = Transaction.last_ticket(names)
    for key in ['buy', 'sell']:
        s2 = parse_page(browser, domain2, key, limits[domain2]['last_ticket'])  # 平台2
        save_transaction_data(s2)
        ms = "平台2 {}数据抓取完毕,可插入数据长度{}".format(key, len(s2))
        recode(ms)
        logger.info(ms)
        print(ms)
        s1 = parse_page(browser, domain1, key, limits[domain1]['last_ticket'])  # 平台1
        save_transaction_data(s1)
        ms = "平台1 {}数据抓取完毕,可插入数据长度{}".format(key, len(s1))
        recode(ms)
        logger.info(ms)
        print(ms)
    return True


def draw_withdraw(browser):
    """
    从站点上查询withdraw,balance,credit
    :return:
    """
    names = [domain2, domain1]
    limits = Transaction.last_ticket(names)
    for key in ['balance', 'credit']:
        s2 = parse_page(browser, domain2, key, limits[domain2]['last_ticket'])  # 平台2
        save_transaction_data(s2)
        ms = "平台2 {}数据抓取完毕,可插入数据长度{}".format(key, len(s2))
        logger.info(ms)
        recode(ms)
        print(ms)
        s1 = parse_page(browser, domain1, key, limits[domain1]['last_ticket'])  # 平台1
        save_transaction_data(s1)
        ms = "平台1 {}数据抓取完毕,可插入数据长度{}".format(key, len(s1))
        recode(ms)
        logger.info(ms)
        print(ms)
    s = parse_page(browser, domain2, None)  # 出金申请
    save_withdraw_data(s)
    ms = "平台2 withdraw数据抓取完毕,可插入数据长度{}".format(len(s))
    logger.info(ms)
    recode(ms)
    print(ms)
    return True


def add_job(job_type: str, job_dict: dict) -> None:
    """
    增加一个任务到工作队列
    :param job_type:
    :param job_dict: 参数字典/None
    共计5种任务
    1. job_type=‘reg' job_dict=reg_dict
    注册
    2. job_type=‘draw_transaction' job_dict=None
    从平台查询buy和sell信息并写入数据库，每天凌晨一次。
    3. job_type=‘draw_withdraw' job_dict=None
    从平台查询withdraw，credit， balance数据并写入数据库，5分钟一次。
    4. job_type=‘query_transaction' job_dict=None
    从数据库查询是否有新的buy和sell数据，有的话就写入云，五分钟一次。
    5. job_type=‘query_withdraw' job_dict=None
    从数据库查询是否有新的withdraw，credit， balance数据，有的话就写入云，五分钟一次。
    :return:
    """
    job = {"job_type": job_type, "job_dict": job_dict}
    jobs = cache.get(job_key)
    if jobs is None:
        jobs = list()
    else:
        pass
    types = [x['job_type'] for x in jobs]
    if job_type in types:
        ms = "重复的任务：{}，放弃".format(job_type)
    else:
        ms = "加入新的任务：{}".format(job_type)
        jobs.append(job)
    cache.set(job_key, jobs, timeout=24*3600)
    recode(ms)
    recode(str(jobs))
    logger.info(ms)


lock = Lock()


def do_jobs():
    """批量做工作"""
    global jobs
    key = "in_do_jobs"
    lock.acquire()
    ms = "{} do_jobs locked".format(datetime.datetime.now())
    logger.info(ms)
    recode(ms)
    in_do_jobs = cache.get(key)
    if in_do_jobs == 1:
        """in_do_jobs表示工作中"""
        ms = "{} in_do_jobs ".format(datetime.datetime.now())
        logger.info(ms)
        recode(ms)
    else:
        ms = "{} not in_do_jobs ".format(datetime.datetime.now())
        logger.info(ms)
        recode(ms)
        in_do_jobs = 1
        cache.set(key, in_do_jobs, timeout=3600)
        jobs = cache.get(job_key)
        ms = "jobs = {}".format(jobs)
        recode(ms)
        if jobs is None:
            jobs = list()
        else:
            pass
        if len(jobs) == 0:
            pass
        else:
            ms = "{} begin do_jobs ".format(datetime.datetime.now())
            logger.info(ms)
            recode(ms)
            browser = get_browser(headless=True)
            while len(jobs) > 0:
                job = jobs.pop(0)
                job_type = job['job_type']
                job_dict = job['job_dict']
                if job_type == 'test':
                    print(job_dict)
                elif job_type == "draw_transaction":
                    draw_transaction(browser)  # 从平台查询并写入数据库
                elif job_type == "draw_withdraw":
                    draw_withdraw(browser)  # 从平台查询并写入数据库
                elif job_type == "query_transaction":
                    # transaction = query_transaction(True)  # 只查询数据库，没有上传动作。
                    transaction = query_transaction(upload=True, only_transaction=True)  # 查四种交易的的数据库，没有上传动作。
                    now = datetime.datetime.now()
                    ms = "{}当前任务{},交易记录的长度为{}".format(now, job_type, len(transaction))
                    content = "{}".format(jobs)
                    send_mail(title=ms, content=content)
                    recode(ms)
                    print(ms)
                    if len(transaction) == 0:
                        print("query transaction success")
                    else:
                        for x in transaction:
                            """上传交易信息"""
                            upload_and_update_transaction(browser=browser, **x)
                        print("upload transaction success")
                elif job_type == "query_withdraw":
                    data = query_withdraw(True)  # 只从数据库查询出金申请。出入金和赠金记录.没有上传动作
                    print("query withdraw,balance and credit success")
                    withdraw = data['withdraw']
                    other = data['other']  # 赠金和出入金记录
                    if isinstance(withdraw, list):
                        """上传出金申请"""
                        for x in withdraw:
                            upload_and_update_withdraw(browser=browser, **x)
                        print("upload withdraw success")
                    if isinstance(other, list):
                        for x in other:
                            upload_and_update_transaction(browser=browser, **x)
                        print("upload withdraw success")
                elif job_type == 'reg':
                    upload_and_update_reg(browser=browser, **job_dict)
                    print("upload reg success")
                else:
                    ms = "error job, type={} ,dict={}".format(job_type, job_dict)
                    recode(ms)
                    logger.exception(ms)
            browser.quit()
            del browser
            gc.collect()
            ms = "headless浏览器资源已经释放，无法释放的内存资源是：{}".format(gc.garbage)
            recode(ms)
        in_do_jobs = 0
        cache.set(key, in_do_jobs, timeout=3600)
    lock.release()
    ms = "{} do_jobs unlocked".format(datetime.datetime.now())
    recode(ms)
    logger.info(ms)
    return True


if __name__ == "__main__":
    """全套测试开始"""
    """draw"""
    # browser = get_browser(1, 1)
    # for key in type_dict.keys():
    #     s2 = parse_page(browser, domain2, key)  # 平台2
    #     save_transaction_data(s2)
    #     s1 = parse_page(browser, domain1, key)  # 平台1
    #     save_transaction_data(s1)
    #
    # s = parse_page(browser, domain2, None)  # 出金申请
    # save_withdraw_data(s)
    # """upload"""
    # transaction = query_transaction(True)
    # for x in transaction:
    #     upload_and_update_transaction(browser=browser, **x)
    # data = query_withdraw(True)
    # withdraw = data['withdraw']
    # other = data['other']
    # for x in withdraw:
    #     upload_and_update_withdraw(browser=browser, **x)  # 上传出金申请
    # for x in other:
    #     upload_and_update_transaction(browser=browser, **x)  # 上传balance和credit
    # browser.quit()
    # del browser
    # gc.collect()
    """全套测试结束"""
    """测试一条假的交易记录"""
    # browser = get_browser(0)
    # b = {
    #     "_id": ObjectId("5aaf48754513530b24fa429b"),
    #     "ticket": 34563,
    #     "profit": -60.0,
    #     "open_time": mongo_db.get_datetime_from_str("2018-03-19T08:56:26.000Z"),
    #     "enter_price": 1312.04,
    #     "nick_name": "吴川",
    #     "spread_profit": -44.0,
    #     "swap": 0.0,
    #     "login": 8300047,
    #     "take_profit": 0.0,
    #     "symbol": "xauusd",
    #     "description": "",
    #     "commission": -50.0,
    #     "system": "office.shengfxchina.com:8443",
    #     "exit_price": 1311.44,
    #     "command": "buy",
    #     "real_name": "吴川",
    #     "comment": "",
    #     "lot": 1.0,
    #     "stop_losses": 0.0,
    #     "close_time": mongo_db.get_datetime_from_str("2018-03-20T14:04:44.000Z"),
    #     "upload": 1
    # }
    # upload_and_update_transaction(browser, **b)
    # browser.quit()
    # del browser
    # gc.collect()
    """填入一条假的出金申请"""
    # a = {
    #     "blank_code" : "",
    #     "account_balance" : 228.71,
    #     "apply_time" : datetime.datetime.now(),
    #     "account_value" : 228.71,
    #     "nick_name" : "提汝洪",
    #     "channel" : "银联",
    #     "open_interest" : 0.0,
    #     "amount_usd" : "228.71",
    #     "account" : 8300082,
    #     "account_margin" : 228.71,
    #     "manager" : "王鹏",
    #     "commission_usd" : 0.0,
    #     "code_id" : "6230520530029871070",
    #     "status" : "审核中",
    #     "system" : "office.shengfxchina.com:8443",
    #     "ticket" : 30,
    #     "blank_name" : "中国农业银行吉林省长春市西安大路支行",
    #     "group" : "zxzg50",
    #     "amount_cny" : "1555.23",
    #     "commission_cny" : 0.0
    # }
    # b = get_browser()
    # upload_and_update_withdraw(b, **a)
    # b.quit()
    # del b
    """测试吸取网站数据"""
    # b = get_browser(0)
    # draw_withdraw(b)
    # """测试写入出金申请"""
    # a = {'account_balance': 949.9, 'account': 8300109, 'commission_cny': 0.0, 'amount_usd': 1000.0, 'commission_usd': 0.0, 'close_time': None, 'amount_cny': 6800.0, 'code_id': '6228480039009384874', 'status': '审核中', 'apply_time': datetime.datetime(2018, 3, 22, 19, 0, 42), 'blank_name': '中国农业银行上海市山阳支行', 'ticket': 34, 'open_interest': 0.0, 'nick_name': '张赛华', 'account_value': 949.9, 'account_margin': 949.9, 'channel': '银联', 'system': 'office.shengfxchina.com:8443'}
    # upload_and_update_withdraw(b, **a)
    # b.quit()
    # del b
    # gc.collect()
    # print(gc.garbage)
    """测试发出金申请消息"""
    # a = {
    #     "_id" : ObjectId("5acd6160a7a75167a9272566"),
    #     "account" : 8300091,
    #     "account_balance" : 133.1,
    #     "send_signal" : 1,
    #     "nick_name" : "周文庆",
    #     "amount_usd" : "133.1",
    #     "commission_cny" : 0.0,
    #     "code_id" : "6228412300245481616",
    #     "open_interest" : 0.0,
    #     "amount_cny" : "905.08",
    #     "channel" : "银联",
    #     "ticket" : 44,
    #     "blank_name" : "农业银行安庆市周潭支行",
    #     "system" : "office.shengfxchina.com:8443",
    #     "commission_usd" : 0.0,
    #     "account_value" : 133.1,
    #     "account_margin" : 133.1,
    #     "status" : "审核中",
    #     "apply_time" : get_datetime_from_str("2018-04-11T09:13:04.000Z"),
    #     "upload" : 1
    # }
    # send_withdraw_signal(a)
    """测试获取客户归属"""
    # i_dict = {
    #         "_id" : ObjectId("5ace114bc69abbd345bfa6c2"),
    #         "mt4_account" : 8300144,
    #         "record_id" : "5ace114b214d2c0a6b376269",
    #         "sales_name" : "黄腾飞",
    #         "customer_name" : "赵刚刚",
    #         "platform" : "shengfxchina",
    #         "director_name" : "倪丽娜",
    #         "manager_name" : "吴峰",
    #         "update_date" : get_datetime_from_str("2018-04-12T02:37:10.522Z"),
    #         "create_date" : get_datetime_from_str("2018-04-11T21:44:43.543Z")
    #     }
    # c = CustomerManagerRelation(**i_dict)
    # print(CustomerManagerRelation.get_relation('8300144'))
    r = query_transaction(upload=True, only_transaction=False)
    print(r)
    pass