#  -*- coding: utf-8 -*-
import os
import sys
__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import By
from mongo_db import get_datetime_from_str
import datetime
import time
from log_module import get_logger


def test_login_track():
    """测试登录,搜索历史轨迹"""
    profile = webdriver.FirefoxProfile()
    """因为headless的浏览器的语言跟随操作系统,为了保证爬回来的数据是正确的语言,这里必须设置浏览器的初始化参数"""
    profile.set_preference("intl.accept_languages", "zh-cn")
    browser = webdriver.Firefox(profile)
    wait = WebDriverWait(browser, 10)

    url_1 = "http://127.0.0.1:5000/manage/login"
    browser.get(url=url_1)  # 打开页面

    # 密码输入input
    input_user_name = wait.until(
        ec.presence_of_element_located((By.ID, "user_name")))
    # 密码输入input
    input_password = wait.until(
        ec.presence_of_element_located((By.ID, "user_password")))
    # 提交按钮
    submit_password = wait.until(ec.element_to_be_clickable((By.ID, "submit_btn")))

    input_user_name.send_keys("15618317376")  # 输入用户名
    time.sleep(1)
    input_password.send_keys("317376")  # 输入密码
    time.sleep(1)
    submit_password.click()  # 提交密码

    track_nav = WebDriverWait(browser, 10).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "a[href='track']")))
    track_nav.click()

    driver = WebDriverWait(browser, 10).until(ec.element_to_be_clickable((By.CLASS_NAME, "nav_item")))
    driver.click()
    date_picker = WebDriverWait(browser, 10).until(ec.element_to_be_clickable((By.ID, "my_datetime_picker")))
    date_picker.click()
    days = WebDriverWait(browser, 10).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".table-condensed .day")))
    for day in days:
        if day.get_attribute("class").find("old") == -1 and day.get_attribute("class").find("new") == -1:
            if day.text == "3":
                day.click()
                break
            else:
                pass
        else:
            pass
    query_track = WebDriverWait(browser, 10).until(ec.element_to_be_clickable((By.ID, "submit_query")))
    query_track.click()


if __name__ == "__main__":
    test_login_track()

