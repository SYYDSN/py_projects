# -*- coding:utf-8 -*-
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver import FirefoxProfile
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import Firefox
from selenium.webdriver import ChromeOptions
from selenium.webdriver import Chrome
from selenium.webdriver.firefox.webelement import FirefoxWebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import By
from selenium.webdriver.support.ui import Select
from pyquery import PyQuery


chrome_driver = "/opt/google/chrome/chromedriver"  # chromedriver的路径
os.environ["ChromeDriver"] = chrome_driver  # 必须配置,否则会在execute_script的时候报错.


def read_file():
    p = "data.txt"
    res = list()
    with open(p, "r", encoding="utf-8") as f:
        for line in f:

            t = list()
            for x in line.split("\t"):
                x = x.strip()
                if x != "":
                    res.append(x)
    return res


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
    附录:
    安装火狐浏览器标准版的方法:
    1. sudo add-apt-repository ppa:mozillateam/firefox-next  出现提示后回车继续
       如果你提示 add-apt-repository: command not found ,那就是缺少命令,请用如下方式安装:
       sudo apt-get install software-properties-common python-software-properties  
    2. sudo apt update
    3. sudo apt install firefox
    """
    if browser_class == 1:
        profile = FirefoxProfile()
        profile.set_preference("intl.accept_languages", "zh-cn")
        """设置代理"""
        # profile.set_preference("signon.autologin.proxy", False)
        # profile.set_preference("network.proxy.type", 1)
        # profile.set_preference("network.proxy.http", "121.236.77.190")
        # profile.set_preference("network.proxy.http_port", 8118)
        # profile.set_preference("network.proxy.share_proxy_settings", True)

        options = FirefoxOptions()
        options.add_argument("--headless")
        if headless:
            try:
                browser = Firefox(firefox_profile=profile, firefox_options=options)
            except Exception as e:
                raise e
        else:
            try:
                browser = Firefox(firefox_profile=profile)
            except Exception as e:
                raise e
    else:
        options = ChromeOptions()
        options.add_argument("--headless")
        if headless:
            try:
                browser = Chrome(executable_path=chrome_driver, chrome_options=options)
            except Exception as e:
                raise e
        else:
            try:
                browser = Chrome(executable_path=chrome_driver)
            except Exception as e:
                raise e
    return browser


def search(b, keyword: str):

    b.get("https://www.baidu.com")
    """寻找输入框"""
    kw = WebDriverWait(b, 10).until(ec.presence_of_element_located((By.ID, "kw")))
    keyword = "{} 电话".format(keyword)
    kw.send_keys(keyword)
    """寻找搜索按钮"""
    sub_btn = WebDriverWait(b, 10).until(ec.element_to_be_clickable((By.ID, "su")))
    sub_btn.click()
    content = WebDriverWait(b, 10).until(ec.presence_of_element_located((By.ID, "content_left")))
    rs = content.find_elements_by_class_name("result")
    for r in rs:
        print(r)




if __name__ == "__main__":
    b = get_browser(headless=False)
    rs = read_file()[30: 40]
    for i, key in enumerate(rs):
        if i % 2 == 0:
            search(b, key)
    b.quit()
    pass