#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import FirefoxProfile
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import By
from module.spread_module import SpreadChannel
from mongo_db import get_datetime_from_str
import datetime
import time
from log_module import get_logger
from mail_module import send_mail
import pyquery
import re
from log_module import recode
from module.transaction_module import Transaction
from module.transaction_module import Withdraw


"""简道云对接模块,火狐版，没有问题"""


logger = get_logger()
current_dir = os.path.dirname(os.path.realpath(__file__))


def month_str(month_int: int) -> str:
    l = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
    return l[month_int - 1]


def get_browser(headless: bool = True) -> Firefox:
    """
    获取一个浏览器
    :param headless:
    :return:
    """
    profile = FirefoxProfile()
    """
    因为headless的浏览器的语言跟随操作系统,为了保证爬回来的数据是正确的语言,
    这里必须设置浏览器的初始化参数,
    注意，使用headless必须先安装对应浏览器正常的版本,然后再安装headless版本
    比如火狐的headless
    下载火狐的geckodriver驱动。(当前文件夹下已经有一个了)地址是：
    https://github.com/mozilla/geckodriver/releases
    下载后解压是一个geckodriver 文件。拷贝到/usr/local/bin目录下，然后加上可执行的权限
    sudo chmod +x /usr/local/bin/geckodriver
    """
    profile.set_preference("intl.accept_languages", "zh-cn")
    options = FirefoxOptions()
    options.add_argument("--headless")
    if headless:
        try:
            browser = Firefox(firefox_profile=profile, firefox_options=options)
        except Exception as e:
            title = "JDY {} headless浏览器打开失败".format(datetime.datetime.now())
            content = "错误原因是：{}".format(e)
            send_mail(title=title, content=content)
            recode(e)
            logger.exception(e)
            raise e
    else:
        try:
            browser = Firefox(firefox_profile=profile)
        except Exception as e:
            title = "JDY {} headless浏览器打开失败".format(datetime.datetime.now())
            content = "错误原因是：{}".format(e)
            send_mail(title=title, content=content)
            recode(e)
            logger.exception(e)
            raise e
    return browser


def to_jiandao_cloud(**kwargs) -> bool:
    """
    推广页面的注册用户数据传送数据到简道云
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
    # profile = webdriver.FirefoxProfile()
    # """因为headless的浏览器的语言跟随操作系统,为了保证爬回来的数据是正确的语言,这里必须设置浏览器的初始化参数"""
    # profile.set_preference("intl.accept_languages", "zh-cn")
    # browser = webdriver.Firefox(profile)
    browser = get_browser(1)
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
        logger.exception(e)
    except Exception as e:
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

    desc10 = kwargs.get('group_by')
    if desc10 is not None:
        js_desc_10 = """let d = $(".widget-wrapper>ul>li:eq(11) input"); d.val("{}");""".format(desc10)
        browser.execute_script(js_desc_10)  # 搜索关键字

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
    ms = "向简道云推广资源表单写数据成功,参数: {}".format(kwargs)
    logger.info(ms)
    del browser
    return True


if __name__ == "__main__":
    """测试往简道云写数据"""
    args = {
        "description": "搜索内容: 长江是有交易所↵预算: 0↵营销: 营销3↵水果: 梨子李子↵项目描述: 测试项目",
        "page_url": "http://localhost:63342/projects/index.html?_ijt=22a6gi3e6no6e4dkrnrqsp6q8o",
        "referrer": "",
        "search_keyword": "长江是有交易所",
        "sms_code": "6659",
        "user_name": "测试人员",
        "group": "2",
        "phone": "15618317376"
    }
    to_jiandao_cloud(**args)
    pass