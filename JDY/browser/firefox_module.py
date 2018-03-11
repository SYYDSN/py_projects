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
import threading


"""简道云对接模块,火狐版，没有问题"""


logger = get_logger()


def to_jiandao_cloud(**kwargs) -> bool:
    """
    推广页面的注册用户数据传送数据到简道云
    :param kwargs:
    :return:
    """
    display = Display(visible=0, size=(800, 600))
    # display.start()  # 开启虚拟显示器

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
    # display.start()  # 开启虚拟显示器
    browser = webdriver.Firefox()  # 表示headless firefox browser
    driver = WebDriverWait(browser, 10)
    login_url = "http://office.shengfx888.com"
    user_name = "849607604@qq.com"
    user_password = "Kai3349665"
    """平衡页(第一页)"""
    balance_url = "http://office.shengfx888.com/report/history_trade?" \
                  "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=&PROFIT_e=&" \
                  "qtype=&CMD=6&closetime=&OPEN_TIME_s=&OPEN_TIME_e=&CLOSE_TIME_s=&" \
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
            # obj.display.start()
            obj.browser = webdriver.Firefox()
            obj.driver = WebDriverWait(obj.browser, 10)
            obj.stop = False  # 批量解析页面时的 中止标志
            obj.user_name = "849607604@qq.com"
            obj.user_password = "Kai3349665"
            obj.login_url = "http://office.shengfx888.com"
            obj.balance_url_base = "http://office.shengfx888.com/report/history_trade?" \
                                   "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=" \
                                   "&PROFIT_e=&qtype=&CMD=&closetime=&OPEN_TIME_s=" \
                                   "&OPEN_TIME_e=&CLOSE_TIME_s=&CLOSE_TIME_e=&T_LOGIN="
            cls.instance = obj
        return cls.instance

    def get_balance_url(self, page_num: int = 1) -> str:
        """
        返回交易列表页的url
        :param page_num: 第几页?
        :return: 交易列表页的url
        """
        return "{}&page={}".format(self.balance_url_base, page_num)

    def login(self):
        """登录http://office.shengfx888.com"""
        self.browser.get(url=self.login_url)
        # 用户名输入
        input_user_name = self.driver.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请输入邮箱或者MT账号']")))
        input_user_name.send_keys(self.user_name)  # 输入用户名
        # 用户密码输入
        input_user_password = self.driver.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请输入登录密码']")))
        input_user_password.send_keys(self.user_password)  # 输入用户密码
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
        if self.browser.current_url.startswith("http://office.shengfx888.com/Public/login?"):
            return True
        else:
            return False

    def open_page(self, page_num: int = 1) -> bool:
        """
        打开出入金页面,如果已经登录,返回True,否则尝试重新login,三次失败后,返回False
        :param page_num: 页码
        :return: 布尔值
        """
        url = self.get_balance_url(page_num)
        self.browser.get(url)
        count = 0
        while self.need_login() and count < 3:
            self.login()
            count += 1
        self.browser.get(url)
        return not self.need_login()

    def __parse_tr_html(self, tr: pyquery.PyQuery) ->(dict, None):
        """
        解析表格的tr，生成一个可以转化为Transaction的实例的字典对象，这是一个专用的方法。被parse_page调用
        :param tr: tr的html文本 pyquery.PyQuery类型
        :return: dict或者None
        """
        init_dict = dict()
        tds = tr.find("td")
        sys_val = "office.shengfx888.com"  # 平台信息
        init_dict['system'] = sys_val
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
        init_dict['command'] = command[0]
        print(ticket, command)
        if command == "balance" or command == "credit":
            """出入金和赠金，少了几个td"""
            """第四个，交易时间"""
            eighth = pyquery.PyQuery(tds[4]).text()
            the_time = get_datetime_from_str(eighth)  # 交易时间
            init_dict['time'] = the_time
            print("出如金时间：{}".format(the_time))
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
            if len(texts_3) > 1:
                symbol = texts_3[-1].lower()
                init_dict['symbol'] = symbol
            """第四个td，取交易手数"""
            fourth = pyquery.PyQuery(tds[3])
            lot_find = re.search(r'\d+.?\d*', fourth.text())
            lot = lot_find if lot_find is None else float(lot_find.group())
            init_dict['lot'] = lot
            """
            第五个，取价格，注意，由于目前看不到数据格式，只能简单的记录文本,
            所以字段的名称暂时和类中描述的不同。
            """
            fifth = pyquery.PyQuery(tds[4])
            prices = fifth.text().split("\n")
            enter_price = float(re.search(r'\d+.?\d*', prices[0]).group())  # 开仓
            exit_price = float(re.search(r'\d+.?\d*', prices[-1]).group())  # 平仓
            init_dict['enter_price'] = enter_price
            init_dict['exit_price'] = exit_price
            """
            第六个，止盈/止损，注意，由于目前看不到数据格式，只能简单的记录文本,
            所以字段的名称暂时和类中描述的不同。
            """
            sixth = pyquery.PyQuery(tds[5])
            stop = sixth.text().split("\n")
            stop_losses = float(re.search(r'\d+.?\d*', stop[0]).group())  # 止损
            take_profit = float(re.search(r'\d+.?\d*', stop[-1]).group())  # 止盈
            init_dict['stop_losses'] = stop_losses
            init_dict['take_profit'] = take_profit
            """
            第七个，利息/佣金，注意，由于目前看不到数据格式，只能简单的记录文本,
            所以字段的名称暂时和类中描述的不同。
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
            if command != "balance":
                print(eighth)
                open_time = get_datetime_from_str(eighth[0].split("：")[1])  # 开仓时间
                init_dict['open_time'] = open_time
                if eighth[-1].find("持仓中") == -1:
                    """持仓中不计算"""
                    return None
                else:
                    colse_time_list = eighth[-1].split("：")
                    if len(colse_time_list) > 1:
                        close_time = get_datetime_from_str(colse_time_list[1])  # 平仓时间
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
            """第十个，点差"""
            tenth = pyquery.PyQuery(tds[9]).text()
            spread_profit = float(tenth)
            init_dict['spread_profit'] = spread_profit
            """第十一个，注释"""
            eleventh = pyquery.PyQuery(tds[10]).text()
            comment = eleventh
            init_dict['comment'] = comment

            init_dict = {k: v for k, v in init_dict.items() if v is not None}
        return init_dict

    def parse_page(self, page_num: int = 1) -> (list, None):
        """
            分析页面数据
            :param page_num: 页码
            :return: 返回分析的多个tr的内容的字典组成的列表
            """
        res = None
        if self.open_page(page_num):
            """打开页面成功"""
            source = self.browser.page_source
            html = pyquery.PyQuery(source)
            tr_htmls = pyquery.PyQuery(html.find("#editable tbody tr"))
            res = list()
            for tr_html in tr_htmls:
                tr = pyquery.PyQuery(tr_html)
                tr_dict = self.__parse_tr_html(tr)
                if isinstance(tr_dict, dict):
                    res.append(tr_dict)
        else:
            title = "office.shengfx888.com爬取数据失败"
            content = "{} {}".format(datetime.datetime.now(), title)
            send_mail(title=title, content=content)
            logger.exception(msg=title)
            raise ValueError(title)
        return res

    def extend_data(self, data1: list, data2: list, ticket_limit: int = None) -> list:
        """
        组装数组，把data2接到data1,然后返回data1,
        期间检查ticket是小于限制，
        :param data1:
        :param data2:
        :param ticket_limit: ticket下限，不能小于此值
        :return:
        """
        if len(data1) == 0:
            data2.sort(key=lambda obj: obj['ticket'], reverse=True)
            if ticket_limit is None:
                data1.extend(data2)
            else:
                for x in data2:
                    print("{} : {}".format(x['ticket'], ticket_limit))
                    if x['ticket'] <= ticket_limit:
                        self.stop = True
                        break
                    else:
                        data1.append(x)
        else:
            """这时候的data1已经排序过了"""
            data2.sort(key=lambda obj: obj['ticket'], reverse=True)
            if ticket_limit is None:
                ticket_limit = data1[-1]['ticket']
                for x in data2:
                    print("{} : {}".format(x['ticket'], ticket_limit))
                    if x['ticket'] <= ticket_limit:
                        self.stop = True
                        break
                    else:
                        data1.append(x)
            else:
                for x in data2:
                    print("{} : {}".format(x['ticket'], ticket_limit))
                    if x['ticket'] <= ticket_limit:
                        self.stop = True
                        break
                    else:
                        data1.append(x)
        return data1

    def batch_parse(self, ticket_limit: int = None) -> list:
        """
        批量分析页面数据，并返回结果的list
        :param ticket_limit: ticket下限，不能小于此值
        :return:
        """
        res = list()
        balance_data = list()
        buy_data = list()
        sell_data = list()
        credit_data = list()
        for i in range(1, 9999999999):
            if not self.stop:
                temp = self.parse_page(i)  # 一页内容解析的结果
                if isinstance(temp, list):
                    res = self.extend_data(res, temp, ticket_limit=ticket_limit)
                else:
                    break
            else:
                break
        return res

    def parse_and_save(self, ticket_limit: int = None) -> list:
        """
        解析页面内容，并保存解析结果
        :param ticket_limit: ticket下限，不能小于此值
        :return:
         """
        if ticket_limit is None:
            ticket_limit = Transaction.last_ticket()
        res = self.batch_parse(ticket_limit)
        res = Transaction.insert_many(res)
        print(res)


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
    crawler.parse_and_save(ticket_limit=31949)
    pass
