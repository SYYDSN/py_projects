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
import re
import datetime
import time
import os
from log_module import get_logger
from mail_module import send_mail
import pyquery
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
            obj.status = "free"  # 由于浏览器同时只能
            obj.user_name = "849607604@qq.com"
            obj.user_password = "Kai3349665"
            obj.login_url = "http://office.shengfx888.com"
            obj.balance_url_base = "http://office.shengfx888.com/report/history_trade?" \
                  "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=&PROFIT_e=&" \
                  "qtype=&CMD=6&closetime=&OPEN_TIME_s=&OPEN_TIME_e=&CLOSE_TIME_s=&" \
                  "CLOSE_TIME_e=&T_LOGIN="
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

    def open_balance_page(self, page_num: int = 1) -> bool:
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

    def parse_page(self, page_num: int = 1) -> dict:
        """
        分析页面数据
        :param page_num: 页码
        :return: 返回分析结果字典
        """
        message = {"message": "success"}
        if self.open_balance_page():
            """打开页面成功"""
            source = self.browser.page_source
            html = pyquery.PyQuery(source)
            print(html)
            trs = pyquery.PyQuery(html.find("#editable tbody tr"))
        else:
            title = "office.shengfx888.com爬取数据失败"
            content = "{} {}".format(datetime.datetime.now(), title)
            send_mail(title=title, content=content)
            message['message'] = "数据爬取失败"
        return message

        



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
    crawler.parse_page()
    pass
