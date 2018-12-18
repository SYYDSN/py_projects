#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from log_module import get_logger
from module.browser_module import get_browser
from module.browser_module import get_wait
from module.browser_module import get_dom
import re
import time
import subprocess



"""数据抓取模块"""


logger = get_logger()
root_dir = __project_dir__
DOWNLOAD_DIR = os.path.join(__project_dir__, "download_data")  # 下载文件的默认目录
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


def get_page(browser, url: str) -> dict:
    """
    抓取页面数据
    :param browser:  浏览器对象
    :param url:  网址
    :return:
    """
    browser.get(url=url)
    w = get_wait(browser=browser)
    lis = get_dom(wait=w, find_type="css", cond="#show_page li", lot=True)
    for li in lis:
        spans = li.find_elements_by_tag_name("span")
        dept = spans[0].text  # 审批部门
        title = li.find_element_by_class_name("fl").text.replace(dept, '').split(" ")[-1]  # 标题
        group = re.search("^[\S{4,}$]", dept)
        if group:
            string = group.string
            string = string[1: len(string) - 1]
            dept = string
        else:
            pass
        batch_sn = spans[1].text  # 批号
        date_str = spans[-1].text  # 日期
        a = li.find_element_by_tag_name("a")
        href = a.get_attribute("href")  # 下载地址
        js = 'window.open("{}");'.format(href)
        browser.execute_script(script=js)
        print("ok")


def open_doc():
    """
    读取文件
    :param
    :return:
    """
    p = os.path.join(DOWNLOAD_DIR, "1.doc")
    d = subprocess.check_output(['antiword', p]).decode()
    for line in d.splitlines():
        print(line)



if __name__ == "__main__":
    # init = {
    #     "browser.download.folderList": 2,  # 下载到制定目录
    #     "browser.download.dir": DOWNLOAD_DIR,  # 下载地址
    #     "browser.download.manager.showWhenStarting": False,  # 显式开始下载
    #     "browser.helperApps.neverAsk.saveToDisk": "application/octet-stream, application/vnd.ms-excel, text/csv, application/zip",  # 以下类型不再确认下载
    # }
    # b = get_browser(headless=True, init_args=init)
    #
    # """抓取的地址"""
    url = "http://www.hntzxm.gov.cn/portal/zcfg/busiotherpublicinfo!selectPublicInfo.action#"
    # d = get_page(browser=b, url=url)
    open_doc()
    pass