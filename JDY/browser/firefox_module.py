#  -*- coding: utf-8 -*-
import os
import sys

__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import By
from module.spread_module import SpreadChannel
from mongo_db import get_datetime_from_str
import datetime
import time
import os
from log_module import get_logger
from mail_module import send_mail
import pyquery
import re
from module.transaction_module import Transaction
from module.transaction_module import Withdraw
import threading


"""简道云对接模块,火狐版，没有问题"""


logger = get_logger()
current_dir = os.path.dirname(os.path.realpath(__file__))


def month_str(month_int: int) -> str:
    l = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
    return l[month_int - 1]


def to_jiandao_cloud(**kwargs) -> bool:
    """
    推广页面的注册用户数据传送数据到简道云
    :param kwargs:
    :return:
    """
    display = Display(visible=0, size=(800, 600))
    display.start()  # 开启虚拟显示器

    """
    注意，pyvirtualdisplay需要xvfb支持。安装方法：sudo apt-get install xvfb
    下载火狐的geckodriver驱动。(当前文件夹下已经有一个了)地址是：
    https://github.com/mozilla/geckodriver/releases
    下载后解压是一个geckodriver 文件。拷贝到/usr/local/bin目录下，然后加上可执行的权限
    sudo chmod +x /usr/local/bin/geckodriver
    """

    browser = webdriver.Firefox()
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
    print(user_name)
    js_name = """let d = $(".widget-wrapper>ul>li:eq(1) input"); d.val("{}");""".format(kwargs['user_name'])
    browser.execute_script(js_name)  # 输入姓名

    js_phone = """let d = $(".widget-wrapper>ul>li:eq(2) input"); d.val("{}");""".format(kwargs['phone'])
    browser.execute_script(js_phone)  # 输入电话

    spread_keywords = SpreadChannel.analysis_url(kwargs['page_url'])
    desc1 = ''
    try:
        desc1 = spread_keywords[0]
    except IndexError as e:
        logger.exception("to_jiandao_cloud error!")
    except Exception as e:
        logger.exception("to_jiandao_cloud error!")
        raise e
    finally:
        js_desc_1 = """let d = $(".widget-wrapper>ul>li:eq(3) input"); d.val("{}");""".format(desc1)
        browser.execute_script(js_desc_1)  # 备注1

    desc2 = ''
    try:
        desc2 = spread_keywords[1]
    except IndexError as e:
        logger.exception("to_jiandao_cloud error!")
    except Exception as e:
        logger.exception("to_jiandao_cloud error!")
        raise e
    finally:
        js_desc_2 = """let d = $(".widget-wrapper>ul>li:eq(4) input"); d.val("{}");""".format(desc2)
        browser.execute_script(js_desc_2)  # 备注2

    desc3 = ''
    try:
        desc3 = spread_keywords[2]
    except IndexError as e:
        logger.exception("to_jiandao_cloud error!")
    except Exception as e:
        logger.exception("to_jiandao_cloud error!")
        raise e
    finally:
        js_desc_3 = """let d = $(".widget-wrapper>ul>li:eq(5) input"); d.val("{}");""".format(desc3)
        browser.execute_script(js_desc_3)  # 备注3

    desc6 = kwargs['page_url']
    js_desc_6 = """let d = $(".widget-wrapper>ul>li:eq(6) input"); d.val("{}");""".format(desc6)
    browser.execute_script(js_desc_6)  # 页面链接

    desc7 = kwargs['description']
    js_desc_7 = """let d = $(".widget-wrapper>ul>li:eq(7) input"); d.val("{}");""".format(desc7)
    print(js_desc_7)
    browser.execute_script(js_desc_7)  # 页面内容

    desc8 = kwargs['search_keyword']
    js_desc_8 = """let d = $(".widget-wrapper>ul>li:eq(9) input"); d.val("{}");""".format(desc8)
    print(js_desc_8)
    browser.execute_script(js_desc_8)  # 搜索关键字

    """
    如果查找器没有定位到dom元素或者页面尚未载入,会报如下的错误.
    selenium.common.exceptions.WebDriverException: Message: unknown error: cannot focus element
    """
    """ec.presence_of_all_elements_located方法可以取一组输入框,然后循环操作"""
    input_list = wait.until(
        ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".widget-wrapper>ul>li input")))  # 输入组
    submit_info = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".x-btn span")))  # 提交资料按钮
    submit_info.click()  # 提交信息

    time.sleep(1)

    # browser.refresh()  # 刷新页面

    time.sleep(10)
    browser.quit()
    display.stop()  # 关闭虚拟显示器
    return True


def listen_shengfx888():
    """爬取实盘用户信息, 这是个临时方法,用来测试思路"""
    display = Display(visible=0, size=(800, 600))
    display.start()  # 开启虚拟显示器
    browser = webdriver.Firefox()  # 表示headless firefox browser
    driver = WebDriverWait(browser, 10)
    login_url = "http://office.shengfx888.com"
    user_name = "849607604@qq.com"
    user_password = "Kai3349665"
    """平衡页(第一页)"""
    balance_url = "http://office.shengfx888.com/report/history_trade?" \
                  "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=&PROFIT_e=&" \
                  "qtype=&CMD=&closetime=&OPEN_TIME_s=&OPEN_TIME_e=&CLOSE_TIME_s=&" \
                  "CLOSE_TIME_e=&T_LOGIN=&page=1"

    """登录http://office.shengfx888.com"""
    browser.get(url=login_url)
    # 用户名输入
    input_user_name = driver.until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请输入邮箱或者MT账号']")))
    input_user_name.send_keys(user_name)  # 输入用户名
    # 用户密码输入
    input_user_password = driver.until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请输入登录密码']")))
    input_user_password.send_keys(user_password)  # 输入用户密码
    # 点击登录按钮
    button_login = driver.until(
        ec.presence_of_element_located((By.ID, "loginbtn")))  # 注意,这里用的不是css选择器而是id选择器
    button_login.click()  # 登录

    time.sleep(10)
    browser.get(balance_url)
    time.sleep(30)
    browser.quit()
    # display.stop()  # 关闭虚拟显示器


class ShengFX888:
    """爬取实盘用户信息的类"""
    def __new__(cls, *args, **kwargs):
        """单例模式设计"""
        if not hasattr(cls, "instance"):
            obj = super(ShengFX888, cls).__new__(cls)
            obj.display = Display(visible=0, size=(800, 600))
            obj.display.start()
            obj.browser = webdriver.Firefox()
            obj.driver = WebDriverWait(obj.browser, 10)
            obj.stop = {"domain": False, "domain2": False}  # 批量解析页面时的 平台1/2中止标志
            obj.user_name = "849607604@qq.com"
            obj.user_password = "Kai3349665"
            obj.login_url = "http://office.shengfx888.com"
            obj.domain = "office.shengfx888.com"
            obj.page_url_base = "http://office.shengfx888.com/report/history_trade?" \
                                   "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=" \
                                   "&PROFIT_e=&qtype=&CMD=&closetime=&OPEN_TIME_s=" \
                                   "&OPEN_TIME_e=&CLOSE_TIME_s=&CLOSE_TIME_e=&T_LOGIN="
            obj.user_name2 = "admin@shengfxChina.com"
            obj.user_password2 = "aykPA1h5"
            obj.domain2 = "office.shengfxchina.com:8443"
            obj.login_url2 = "https://office.shengfxchina.com:8443/Public/login"
            obj.page_url_base2 = "https://office.shengfxchina.com:8443/report/history_trade?" \
                                 "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=&PROFIT_e=&qtype=" \
                                 "&CMD=&closetime=&OPEN_TIME_s=&OPEN_TIME_e=&CLOSE_TIME_s=" \
                                 "&CLOSE_TIME_e=&comm_type=&T_LOGIN="
            obj.withdraw_url_base2 = "https://office.shengfxchina.com:8443/deposit/waitin?" \
                                     "layout=yes&weburlredect=1&"    # 2号平台,出金申请
            cls.instance = obj
        return cls.instance

    def get_page_url(self, url_base: str = None, page_num: int = 1) -> str:
        """
        获取一号平台综合业务网址
        :param url_base: 基础网址
        :param page_num:
        :return:
        """
        url_base = self.page_url_base if url_base is None else url_base
        return "{}&page={}".format(url_base, page_num)

    def login(self, login_url: str = None):
        """
        登录http://office.shengfx888.com和https://office.shengfxchina.com:8443/Public/login
        :param login_url: 默认是http://office.shengfx888.com
        :return:
        """
        if login_url is None or login_url == self.login_url:
            url = self.login_url
            user_name = self.user_name
            user_password = self.user_password
        else:
            url = self.login_url2
            user_name = self.user_name2
            user_password = self.user_password2
        self.browser.get(url=url)
        # print(self.browser.current_url)
        # print(self.browser.page_source)
        # 用户名输入
        input_user_name = self.driver.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "form .uname")))
        input_user_name.send_keys(user_name)  # 输入用户名
        # 用户密码输入
        input_user_password = self.driver.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "form .pword")))
        input_user_password.send_keys(user_password)  # 输入用户密码
        # 点击登录按钮
        button_login = self.driver.until(
            ec.presence_of_element_located((By.ID, "loginbtn")))  # 注意,这里用的不是css选择器而是id选择器
        button_login.click()  # 登录

        time.sleep(10)
        # self.browser.close()
        # time.sleep(30)
        # self.browser.get(self.get_balance_url())
        # self.browser.quit()
        
    def need_login(self) -> bool:
        """
        检查当前的登录会话是否过时?(是否需要登录?)
        :return: 需要登录返回True,不需要登录返回False
        """
        if self.browser.current_url.startswith("http://office.shengfx888.com/Public/login?") or \
                self.browser.current_url.startswith("https://office.shengfxchina.com:8443/Public/login"):
            return True
        else:
            return False

    def open_page(self, url_base: str = None, page_num: int = 1) -> bool:
        """
        打开出入金页面,如果已经登录,返回True,否则尝试重新login,三次失败后,返回False
        :param url_base: 基础网址
        :param page_num: 页码
        :return: 布尔值
        """
        url = self.get_page_url(url_base=url_base, page_num=page_num)
        self.browser.get(url)
        if url_base == self.page_url_base:
            login_url = self.login_url
        else:
            login_url = self.login_url2
        count = 0
        while self.need_login() and count < 3:
            self.login(login_url)
            count += 1
        self.browser.get(url)
        return not self.need_login()

    def __parse_tr_html(self, domain: str, tr: pyquery.PyQuery) ->(dict, None):
        """
        解析表格的tr，生成一个可以转化为Transaction的实例的字典对象，这是一个专用的方法。被parse_page调用
        :param domain: domain
        :param tr: tr的html文本 pyquery.PyQuery类型
        :return: dict或者None
        """
        init_dict = dict()
        tds = tr.find("td")

        """第一个td,取订单号和客户帐号"""
        first = pyquery.PyQuery(tds[0])
        texts_1 = first.text().split("\n")
        ticket = int(re.search(r'\d{4,}', texts_1[0]).group())  # 订单号
        login = int(re.search(r'\d{6,}', texts_1[-1]).group())  # 客户帐号
        init_dict['ticket'] = ticket
        init_dict['login'] = login
        """第二个td，取英文名和真实姓名"""
        second = pyquery.PyQuery(tds[1])
        texts_2 = second.text().split("\n")
        nick_name = texts_2[0][4:].strip("")
        real_name = texts_2[-1][5:].strip("")
        init_dict['nick_name'] = nick_name
        init_dict['real_name'] = real_name
        """第三个td，取交易指令和品种"""
        third = pyquery.PyQuery(tds[2])
        texts_3 = third.text().split("\n")
        command = texts_3[0].lower()
        init_dict['command'] = command
        sys_val = domain
        print("domain = {}, command = {}, tds,length = {}".format(sys_val, command, len(tds)))
        init_dict['system'] = sys_val
        print(ticket, command, texts_3)
        if command == "balance" or command == "credit":
            """出入金和赠金，少了几个td"""
            """第四个，交易时间"""
            eighth = pyquery.PyQuery(tds[4]).text()
            the_time = get_datetime_from_str(eighth)  # 交易时间
            init_dict['time'] = the_time
            print("出入金时间：{}".format(the_time))
            """
            第五个，盈亏
            """
            ninth = pyquery.PyQuery(tds[5]).text()
            profit = re.search(r'[+, -]?\d+.?\d*', ninth)
            if profit is not None:
                profit = float(profit.group())
                init_dict['profit'] = profit
            """第六个，点差"""
            tenth = pyquery.PyQuery(tds[6]).text()
            spread_profit = float(tenth)
            init_dict['spread_profit'] = spread_profit
            """第七个，注释"""
            eleventh = pyquery.PyQuery(tds[7]).text()
            comment = eleventh
            init_dict['comment'] = comment
            init_dict = {k: v for k, v in init_dict.items() if v is not None}
        else:
            """buy和sell的情况"""
            symbol = ''
            if len(texts_3) > 1:
                symbol = texts_3[-1].lower()
                init_dict['symbol'] = symbol
            """第四个td，取交易手数"""
            fourth = pyquery.PyQuery(tds[3])
            lot_find = re.search(r'\d+.?\d*', fourth.text())
            lot = lot_find if lot_find is None else float(lot_find.group()) if symbol != "hk50mini" else \
                float(lot_find.group()) / 10
            init_dict['lot'] = lot
            """
            第五个，取价格，
            """
            fifth = pyquery.PyQuery(tds[4])
            prices = fifth.text().split("\n")
            enter_price = float(re.search(r'\d+.?\d*', prices[0]).group())  # 开仓
            exit_price = float(re.search(r'\d+.?\d*', prices[-1]).group())  # 平仓
            init_dict['enter_price'] = enter_price
            init_dict['exit_price'] = exit_price
            """
            第六个，止盈/止损，
            """
            sixth = pyquery.PyQuery(tds[5])
            stop = sixth.text().split("\n")
            stop_losses = float(re.search(r'\d+.?\d*', stop[0]).group())  # 止损
            take_profit = float(re.search(r'\d+.?\d*', stop[-1]).group())  # 止盈
            init_dict['stop_losses'] = stop_losses
            init_dict['take_profit'] = take_profit
            """
            第七个，利息/佣金，
            """
            seventh = pyquery.PyQuery(tds[6])
            seventh = seventh.text().split("\n")
            swap = float(re.search(r'[+, -]?\d+.?\d*', seventh[0]).group())  # 利息
            commission = float(re.search(r'[+, -]?\d+.?\d*', seventh[-1]).group())  # 手续费
            init_dict['swap'] = swap
            init_dict['commission'] = commission
            """第八个，交易时间"""
            eighth = pyquery.PyQuery(tds[7]).text()
            eighth = eighth.split("\n")
            if command not in ["balance", "credit"]:
                print(eighth)
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
            ninth = pyquery.PyQuery(tds[8]).text()
            profit = re.search(r'[+, -]?\d+.?\d*', ninth)
            if profit is not None:
                profit = float(profit.group())
                init_dict['profit'] = profit
            """注意,平台1和平台2的列数不一样,平台1有点差,11列,平台2没有点差,10列"""
            if len(tds) == 11:
                """第十个，点差"""
                tenth = pyquery.PyQuery(tds[-2]).text()
                spread_profit = float(tenth)
                init_dict['spread_profit'] = spread_profit
            else:
                pass
            """最后一个，注释"""
            eleventh = pyquery.PyQuery(tds[-1]).text()
            comment = eleventh
            init_dict['comment'] = comment

            init_dict = {k: v for k, v in init_dict.items() if v is not None}
        """只记录指定类型的单子"""
        if init_dict['command'] in ['balance', 'credit', 'buy', 'sell']:
            return init_dict
        else:
            return None

    def __parse_withdraw_tr_html(self, tr: pyquery.PyQuery) ->(dict, None):
        """
        解析出金申请的表格的tr，生成一个可以转化为Withdraw的实例的字典对象，这是一个专用的方法。被parse_withdraw_page调用
        :param tr: tr的html文本 pyquery.PyQuery类型
        :return: dict或者None
        """
        init_dict = dict()
        tds = tr.find("td")
        if len(tds) < 15:
            return None
        else:
            domain = self.domain2
            init_dict['system'] = domain
            """第一个td,取mt帐号和mt分组"""
            first = pyquery.PyQuery(tds[0])
            texts_1 = first.text().split("\n")
            account = int(re.search(r'\d{4,}', texts_1[0].lower()).group())  # mt账户
            group = texts_1[-1].lower()[5:]  # mt分组
            init_dict['account'] = account
            init_dict['group'] = group
            """第二个td，取客户2"""
            second = pyquery.PyQuery(tds[1])
            init_dict['manager'] = second.text().strip()
            """第三个td，取英文名"""
            third = pyquery.PyQuery(tds[2])
            texts_3 = third.text().split("\n")
            nick_name = texts_3[0][4:].strip("")
            init_dict['nick_name'] = nick_name
            """第四个，金额"""
            fourth = pyquery.PyQuery(tds[3])
            texts_4 = fourth.text().split("\n")
            amount_usd = float(texts_4[0].split("$")[-1].strip())  # 金额/美元
            amount_cny = float(texts_4[-1].split("￥")[-1].strip())  # 金额/人民币
            init_dict['amount_usd'] = amount_usd
            init_dict['amount_cny'] = amount_cny
            """
            第五个，取手续费
            """
            fifth = pyquery.PyQuery(tds[4])
            texts_5 = fifth.text().split("\n")
            commission_usd = float(texts_5[0].split("$")[-1].strip())  # 手续费/美元
            commission_cny = float(texts_5[-1].split("￥")[-1].strip())  # 手续费/人民币
            init_dict['commission_usd'] = commission_usd
            init_dict['commission_cny'] = commission_cny
            """
            第六个，转账方式，
            """
            sixth = pyquery.PyQuery(tds[5])
            init_dict['channel'] = sixth.text().strip()
            """
            第七个，时间
            """
            seventh = pyquery.PyQuery(tds[6])
            seventh = seventh.text().split("\n")
            apply_time = seventh[0][5:].strip("")
            apply_time = get_datetime_from_str(apply_time)
            close_time = seventh[-1][5:].strip("")
            close_time = get_datetime_from_str(close_time)
            init_dict['apply_time'] = apply_time
            init_dict['close_time'] = close_time
            """第八个，开户行"""
            eighth = pyquery.PyQuery(tds[7]).text()
            init_dict['blank_name'] = eighth.strip()
            """第九个，开户行代码"""
            ninth = pyquery.PyQuery(tds[8]).text()
            init_dict['blank_code'] = ninth.strip()
            """第十个，银行"""
            tenth = pyquery.PyQuery(tds[9]).text()
            init_dict['code_id'] = tenth.strip()
            """第十一个，状态"""
            eleventh = pyquery.PyQuery(tds[10]).text()
            init_dict['status'] = eleventh.strip()
            """第十二个，账户余额"""
            twelfth = pyquery.PyQuery(tds[11]).text()
            init_dict['account_balance'] = float(twelfth.strip()[1:])
            """第十三个，账户净值"""
            thirteenth = pyquery.PyQuery(tds[12]).text()
            init_dict['account_value'] = float(thirteenth.strip()[1:])
            """第十四个，持仓量"""
            fourteenth = pyquery.PyQuery(tds[13]).text()
            init_dict['open_interest'] = float(fourteenth.strip()[0: -1])
            """第十五个，可用保证金"""
            fifteenth = pyquery.PyQuery(tds[14]).text()
            init_dict['account_margin'] = float(fifteenth.strip()[1:])
            """第十六个，单号"""
            sixth = pyquery.PyQuery(tds[15].find("a"))
            init_dict['ticket'] = int(sixth.attr("href").split("/")[-1])

            init_dict = {k: v for k, v in init_dict.items()}
            """只记录指定类型的单子"""
            if init_dict['status'] == "审核中":
                return init_dict
            else:
                return None

    def parse_page(self, url_base: str = None, page_num: int = 1) -> (list, None):
        """
        分析页面数据
        :param url_base:
        :param page_num: 页码
        :return: 返回分析的多个tr的内容的字典组成的列表
        """
        res = None
        query = "#editable tbody tr"
        if url_base is None:
            url = self.page_url_base
        else:
            url = url_base
        domain = self.domain if re.search(self.domain, url_base) else self.domain2
        if self.open_page(url, page_num):
            """打开页面成功"""
            source = self.browser.page_source
            html = pyquery.PyQuery(source)
            tr_htmls = pyquery.PyQuery(html.find(query))
            res = list()
            for tr_html in tr_htmls:
                tr = pyquery.PyQuery(tr_html)
                tr_dict = self.__parse_tr_html(domain, tr)
                if isinstance(tr_dict, dict):
                    res.append(tr_dict)
                else:
                    pass
        else:
            if url == self.page_url_base:
                domain = self.domain
            else:
                domain = self.domain2
            title = "{}爬取数据失败".format(domain)
            content = "{} {}".format(datetime.datetime.now(), title)
            send_mail(title=title, content=content)
            logger.exception(msg=title)
            raise ValueError(title)
        return res

    def parse_withdraw_page(self, url_base: str = None, page_num: int = 1) -> (list, None):
        """
        分析出金申请页面数据
        :param url_base:
        :param page_num: 页码
        :return: 返回分析的多个tr的内容的字典组成的列表
        """
        res = None
        url = self.withdraw_url_base2 if url_base is None else url_base
        query = "#editable tbody tr"
        if self.open_page(url, page_num):
            """打开页面成功"""
            source = self.browser.page_source
            html = pyquery.PyQuery(source)
            tr_htmls = pyquery.PyQuery(html.find(query))
            res = list()
            for tr_html in tr_htmls:
                tr = pyquery.PyQuery(tr_html)
                tr_dict = self.__parse_withdraw_tr_html(tr)
                if isinstance(tr_dict, dict):
                    res.append(tr_dict)
                else:
                    pass
        else:
            title = "{}&page={}爬取数据失败".format(url, page_num)
            content = "{} {}".format(datetime.datetime.now(), title)
            send_mail(title=title, content=content)
            logger.exception(msg=title)
            raise ValueError(title)
        return res

    def extend_data(self, data1: list, data2: list, ticket_limit: int = None) -> dict:
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
            time_limit = datetime.datetime.strptime("2018-2-1 0:0:0", "%Y-%m-%d %H:%M:%S")
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

    def batch_parse(self, domain: str = None, ticket_limit: int = None) -> list:
        """
        批量分析页面数据，并返回结果的list
        :param domain: 平台域名
        :param ticket_limit: ticket下限，不能小于此值
        :return:
        """
        res = list()
        stop = False
        stop2 = False
        domain = self.domain if domain is None else domain
        page_url_base = self.page_url_base if domain == self.domain else self.page_url_base2
        for i in range(1, 9999999999):
            if domain == self.domain:
                if not stop:
                    temp = self.parse_page(page_url_base, i)  # 一页内容解析的结果
                    if isinstance(temp, list) and len(temp) > 0:
                        temp = self.extend_data(res, temp, ticket_limit)  # 拼接每一页解析出来的数据
                        res = temp['data']
                        stop = temp['stop']
                    else:
                        break
                else:
                    break
            else:
                if not stop2:
                    temp = self.parse_page(page_url_base, i)  # 一页内容解析的结果
                    if isinstance(temp, list) and len(temp) > 0:
                        temp = self.extend_data(res, temp, ticket_limit)  # 拼接每一页解析出来的数据
                        res = temp['data']
                        stop2 = temp['stop']
                    else:
                        break
                else:
                    break
        return res

    def batch_parse_withdraw(self, url_base: str = None, ticket_limit: int = None) -> list:
        """
        批量分析出金申请页面数据，并返回结果的list
        :param url_base: 页面基础url
        :param ticket_limit: ticket下限，不能小于此值
        :return:
        """
        res = list()
        page_url_base = self.withdraw_url_base2 if url_base is None else url_base
        stop = False
        for i in range(1, 9999999999):
            if not stop:
                temp = self.parse_withdraw_page(page_url_base, i)  # 一页内容解析的结果
                if isinstance(temp, list) and len(temp) > 0:
                    temp = self.extend_data(res, temp, ticket_limit)  # 拼接每一页解析出来的数据
                    res = temp['data']
                    stop = temp['stop']
                else:
                    break
            else:
                break
        return res

    @staticmethod
    def split_data(records: list, holdings: list, repeat: list = list()) -> dict:
        """
        把结果集按指令类型分类
        :param records: 交易的记录
        :param holdings: 数据库中保存的持仓记录
        :param repeat: 数据库中保存的小于last_ticket的非持仓记录.
        :return: 分类后的交易记录
        """
        # deposit_list = []  # 入金申请
        # withdraw_list = []  # 出金申请 需要上传到简道云
        upload_list = []  # 已经平仓的buy和sell  需要被上传到简道云
        insert_db_list = []  # 需要插入数据库的数据,包括新的出入金,buy,sell,赠金四类
        update_db_list = []  # 需要修改的数据库的记录,一般是已经平仓了的持仓信息
        other_list = []  # 其他订单
        holding_tickets = [x['ticket'] for x in holdings]
        repeat = [x['ticket'] for x in repeat]
        for x in records:
            command = x['command']
            ticket = x['ticket']
            if command in ["buy", "sell"]:
                if ticket in holding_tickets:
                    """持仓中的buy/sell单子"""
                    close_time = x.get("close_time")
                    if isinstance(close_time, datetime.datetime):
                        """持仓中的单子平仓了"""
                        update_db_list.append(x)
                        """持仓的单子变成平仓了,需要上传"""
                        upload_list.append(x)
                    else:
                        """仍然持仓的单子，不理会"""
                        pass
                else:
                    """新增加的buy/sell单子"""
                    if x.get('close_time') is None or x.get('close_time') == "":
                        """新增持仓中的单子,不要上传,只保存到数据库"""
                        insert_db_list.append(x)
                    else:
                        if ticket in repeat:
                            """重复的无需插入"""
                            pass
                        else:
                            """新增加的已平仓的buy/sell单子,这些单子需要上传到简道云和数据库"""
                            upload_list.append(x)
                            insert_db_list.append(x)
            elif command in ['balance', 'credit']:
                """查询到的出入金和赠金"""
                if ticket in repeat:
                    """重复的无需插入"""
                    pass
                else:
                    insert_db_list.append(x)
            else:
                other_list.append(x)
        res = {
            "upload": upload_list,  # 上传到简道云交易汇总信息
            "insert_db": insert_db_list,  # 插入数据库
            "update_db": update_db_list,  # 更新数据库
            # "deposit": deposit_list,  # 入金申请,
            # "withdraw": withdraw_list,  # 出金申请, 需要写入简道云
            "other": other_list
        }
        return res

    def upload_all_records(self, **kwargs) -> None:
        """
        上传所有的出入金,赠金,已平仓的buy和sell记录
        :return:
        """
        command = kwargs['command']
        open_time = kwargs['time'] if command in ["credit", "balance"] else kwargs['open_time']
        close_time = kwargs['time'] if command in ["credit", "balance"] else kwargs.get('close_time')
        close_time = '' if close_time is None else close_time
        if close_time == "":
            pass  # 持仓中的单子不需要记录
        else:
            browser = self.browser
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
            time.sleep(5)  # 等待是为了给页面时间载入
            create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(create_time)
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

            lot = '' if kwargs.get('lot') is None else kwargs['lot']
            if lot == "":
                print(kwargs)
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
            js_profit = """let d = $(".widget-wrapper>ul>li:eq(17) input"); d.val("{}");""".format(profit)
            browser.execute_script(js_profit)  # 盈利点数

            time.sleep(1)
            submit_info = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".x-btn span")))  # 提交资料按钮
            submit_info.click()  # 提交信息

            browser.refresh()  # 刷新页面

    def upload_withdraw_apply(self, **kwargs) -> None:
        """
        上传出金的记录
        :return:
        """
        browser = self.browser
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

        apply_time = kwargs['apply_time']
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

        time.sleep(1)
        browser.refresh()  # 刷新页面

    def parse_and_save(self, domain: str = None, ticket_limit: int = None) -> None:
        """
        解析页面内容，并保存解析结果
        :param domain: 平台名称
        :param ticket_limit: ticket下限，不能小于此值, 仅仅在调试时使用。用于缩小查找范围。
        :return:
         """
        data = dict()
        data["upload"] = list()  # 上传到简道云交易汇总信息
        data["insert_db"] = list()  # 插入数据库
        data["update_db"] = list()  # 更新数据库
        data['other'] = list()
        domain = self.domain if domain is None else domain
        if ticket_limit is None:
            query = Transaction.last_ticket([self.domain, self.domain2])
        else:
            query = {domain: {"last_ticket": ticket_limit, "holdings": list, "repeat": list()}}
        """采集两个平台大的四种交易信息"""
        for domain, item in query.items():
            ticket_limit = item['last_ticket']
            holdings = item['holdings']
            repeat = item['repeat']
            res = self.batch_parse(domain, ticket_limit)
            res = self.split_data(res, holdings, repeat)  # 按照类型拆分数据
            data['upload'].extend(res['upload'])
            data['insert_db'].extend(res['insert_db'])
            data['update_db'].extend(res['update_db'])
            data['other'].extend(res['other'])
        """获取平台2的出金申请记录"""
        last_withdraw = Withdraw.last_record(self.domain2)
        last_ticket = None if last_withdraw is None else last_withdraw['ticket']
        withdraw_list = self.batch_parse_withdraw(self.withdraw_url_base2, last_ticket)
        withdraw_list.sort(key=lambda obj: obj['apply_time'], reverse=False)
        data['withdraw'] = withdraw_list
        upload_list = data['upload']
        upload_list.sort(key=lambda obj: (obj['time'] if obj.get("close_time") is None else
                                          obj['close_time']), reverse=False)
        update_list = data['update_db']
        insert_list = data['insert_db']
        [self.upload_all_records(**record) for record in upload_list]  # 上传所有交易记录
        [self.upload_withdraw_apply(**record) for record in withdraw_list]  # 上传出金信息
        res = Transaction.insert_many(insert_list)  # 存数据库
        print("insert many result is {}".format(res))
        for record in update_list:
            filter_dict = {"ticket": record.pop('ticket'), 'system': record.pop('system')}
            update_dict = {"$set": record}
            res = Withdraw.find_one_and_update_plus(filter_dict=filter_dict, update_dict=update_dict)
            print("update result is {}".format(res))

    @classmethod
    def write_error(cls, func_name: str, ticket: int, domain: str, is_apply: bool) -> None:
        """
        当发生错误的时候，记录下错误的信息，以方便接着中断的地方记录进行
        :param func_name: 函数名，可以自定义，只要有对应关系即可
        :param ticket:
        :param domain: domain或者对象的system
        :param is_apply: 是否是出金申请？
        :return:
        """
        file_name = "error.log"
        file_path = os.path.join(current_dir, file_name)
        file = open(file_path, mode="w", encoding="utf-8")
        lines = [
            'func_name = {}'.format(func_name),
            'ticket = {}'.format(ticket),
            'domain = {}'.format(domain),
            'is_apply = {}'.format(is_apply)
        ]
        file.writelines(lines)
        file.flush()
        file.close()

     @classmethod
    def clear_error_file(cls) -> bool:
         """
         处理完出错后，请调用此方法删除错误记录文件。
         :return:
         """

if __name__ == "__main__":
    """测试往简道云写数据"""
    # args = {
    #     "description": "搜索内容: 长江是有交易所↵预算: 0↵营销: 营销3↵水果: 梨子李子↵项目描述: 测试项目",
    #     "page_url": "http://localhost:63342/projects/index.html?_ijt=22a6gi3e6no6e4dkrnrqsp6q8o",
    #     "referrer": "",
    #     "search_keyword": "长江是有交易所",
    #     "sms_code": "6659",
    #     "user_name": "测试人员",
    #     "phone": "15618317376"
    # }
    # to_jiandao_cloud(**args)
    #
    # time.sleep(1)
    """测试爬取实盘用户信息"""
    # listen_shengfx888()
    # ShengFX888().login()
    """测试抓取结算站点数据"""
    crawler = ShengFX888()
    crawler.parse_and_save()
    # crawler.parse_and_save(ticket_limit=31017)
    # crawler.upload_all_records()
    # a = {'description': '出金', 'command': 'balance', 'ticket': 31349, 'login': 880300399,
    #      'time': datetime.datetime(2018, 3, 8, 17, 25, 38), 'spread_profit': 0.0,
    #      'nick_name': '李琳', 'comment': 'Withdraw maxib#319',  'real_name': '李琳',
    #      'profit': -2659.51, 'system': 'office.shengfx888.com', "lot": 0.5}
    #
    # crawler.upload_all_records(**a)
    pass
