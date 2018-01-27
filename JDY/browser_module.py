#  -*- coding: utf-8 -*-
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import By

import datetime
import time
import os


"""简道云对接模块"""


display = Display(visible=0, size=(1024, 768))
# display.start()   # 开启虚拟显示器

"""
https://chromedriver.storage.googleapis.com/index.html?path=2.35/
你也可以自行搜索chromedriver的下载地址,解压是个可执行文件,放到chrome的目录即可.
一般ubuntu下面,chrome的目录是/opt/google/chrome/
"""

chrome_driver = "/opt/google/chrome/chromedriver"  # chromedriver的路径
os.environ["ChromeDriver"] = chrome_driver  # 必须配置,否则会在execute_script的时候报错.
browser = webdriver.Chrome(chrome_driver)
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

js_name = """let d = $(".widget-wrapper>ul>li:eq(1) input"); d.val("{}");""".format("测试人员")
browser.execute_script(js_name)  # 输入姓名

js_phone = """let d = $(".widget-wrapper>ul>li:eq(2) input"); d.val("{}");""".format("18888888888")
browser.execute_script(js_phone)  # 输入电话

js_desc_1 = """let d = $(".widget-wrapper>ul>li:eq(3) input"); d.val("{}");""".format("此消息由迅迭后台自动发送.")
browser.execute_script(js_desc_1)  # 备注1


"""selenium.common.exceptions.WebDriverException: Message: unknown error: cannot focus element"""
"""ec.presence_of_all_elements_located方法可以取一组输入框,然后循环操作"""
input_list = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".widget-wrapper>ul>li input")))  #输入组
submit_info = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, ".x-btn span")))  # 提交资料按钮
submit_info.click()  # 提交信息

time.sleep(1)
browser.refresh()  # 刷新页面

time.sleep(10)
browser.quit()
# display.stop()  # 关闭虚拟显示器
