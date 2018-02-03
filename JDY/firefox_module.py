#  -*- coding: utf-8 -*-
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import By

import datetime
import time
import os
import threading


"""简道云对接模块,火狐版，没有问题"""


cur_dir = os.path.dirname(os.path.realpath(__file__))


def to_jiandao_cloud(**kwargs) -> dict:
    """
    传送数据到简道云
    :param kwargs:
    :return:
    """
    display = Display(visible=0, size=(800, 600))
    display.start()   # 开启虚拟显示器

    """
    注意，pyvirtualdisplay需要xvfb支持。安装方法：sudo apt-get install xvfb
    下载火狐的geckodriver驱动。地址是：
    https://github.com/mozilla/geckodriver/releases
    下载后解压是一个geckodriver 文件。拷贝到/usr/local/bin目录下，然后加上可执行的权限
    sudo chmod +x /usr/local/bin/geckodriver
    一般ubuntu下面,chrome的目录是/opt/google/chrome/
    """

    # firefox_driver = os.path.join(cur_dir, "geckodriver")  #必须配置,否则会在execute_script的时候报错.
    # os.environ["geckodriver"] = firefox_driver  # 必须配置,否则会在execute_script的时候报错.
    browser = webdriver.Firefox()
    wait = WebDriverWait(browser, 10)

    url_1 = "https://www.jiandaoyun.com/f/5a658cbc7b87e86216236cb3"
    browser.get(url=url_1)  # 打开页面

    # 密码输入按钮
    input_password = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".x-layout-table input[type='password']")))
    # 提交按钮
    submit_password = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".x-layout-table .x-btn span")))

    input_password.send_keys("xundie789")  # 输入密码
    time.sleep(1)
    submit_password.click()  # 提交密码

    time.sleep(3)  # 等待是为了给页面时间载入
    # 修改时间选择器输入框脚本
    js_datepicker = """let d = $(".widget-wrapper>ul>li:first input"); d.val("{}");""".\
        format(datetime.datetime.now().strftime("%F"))
    browser.execute_script(js_datepicker)  # 输入时间

    print(type(kwargs))
    print(kwargs)

    user_name = kwargs.get('user_name')
    print(user_name)
    js_name = """let d = $(".widget-wrapper>ul>li:eq(1) input"); d.val("{}");""".format(kwargs['user_name'])
    browser.execute_script(js_name)  # 输入姓名

    js_phone = """let d = $(".widget-wrapper>ul>li:eq(2) input"); d.val("{}");""".format(kwargs['phone'])
    browser.execute_script(js_phone)  # 输入电话

    js_desc_1 = """let d = $(".widget-wrapper>ul>li:eq(3) input"); d.val("{}");""".format(kwargs['search_keyword'])
    browser.execute_script(js_desc_1)  # 备注1 填入用户搜索过的关键词

    js_desc_2 = """let d = $(".widget-wrapper>ul>li:eq(4) input"); d.val("{}");""".format(kwargs['referrer'])
    browser.execute_script(js_desc_2)  # 备注2 填入用户跳转之前的页面

    js_desc_2 = """let d = $(".widget-wrapper>ul>li:eq(5) input"); d.val("{}  自动注册");""".format(datetime.datetime.now().
                                                                                          strftime("%Y-%m-%d %H:%M:%S"))
    browser.execute_script(js_desc_2)  # 备注3 填入用户注册的原始时间,用以比较时间的大差

    js_desc_6 = """let d = $(".widget-wrapper>ul>li:eq(6) input"); d.val("{}");""".format(kwargs['base_url'])
    browser.execute_script(js_desc_6)  # 页面链接

    js_desc_7 = """let d = $(".widget-wrapper>ul>li:eq(7) input"); d.val("{}");""".format(kwargs['description'])
    browser.execute_script(js_desc_7)  # 页面内容


    """
    如果查找器没有定位到dom元素或者页面尚未载入,会报如下的错误.
    selenium.common.exceptions.WebDriverException: Message: unknown error: cannot focus element
    """
    """ec.presence_of_all_elements_located方法可以取一组输入框,然后循环操作"""
    input_list = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".widget-wrapper>ul>li input")))  #输入组
    submit_info = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".x-btn span")))  # 提交资料按钮
    submit_info.click()  # 提交信息

    time.sleep(1)

    # browser.refresh()  # 刷新页面

    time.sleep(10)
    browser.quit()
    display.stop()  # 关闭虚拟显示器
    return True


def x(**kwargs):
    print(kwargs['name'])
    print(kwargs['age'])

import time
def send_info(**kwargs):
    """多线程发送信息到简道云"""
    kwarg = kwargs
    t = threading.Thread(target=x, kwargs=kwarg, daemon=0)
    time.sleep(3)
    t.start()


if __name__ == "__main__":
    args = {
        'phone': '15611224444',
        'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0',
        'description': '页面标题:注册示范',
        'referrer': 'http://127.0.0.1:9000/register_demo.html', 'search_keyword': '',
        'user_name': '344444444444444445',
        'host_url': 'http://127.0.0.1:9000/',
        'base_url': 'http://127.0.0.1:9000/register',
        'time': datetime.datetime(2018, 2, 3, 17, 18, 27, 743466)
    }
    to_jiandao_cloud(**args)
    # send_info(name="jadf", age=12)

    time.sleep(1)