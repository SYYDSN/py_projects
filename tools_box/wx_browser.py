#  -*- coding: utf-8 -*-
import datetime
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import FirefoxProfile
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import Firefox
from selenium.webdriver import ChromeOptions
from selenium.webdriver import Chrome
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import By


"""模拟微信浏览器"""


chrome_driver = "/opt/google/chrome/chromedriver"  # chromedriver的路径
os.environ["ChromeDriver"] = chrome_driver  # 必须配置,否则会在execute_script的时候报错.


def get_browser() -> Firefox:
    """
    获取一个浏览器
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
    headers = {
                'Accept-Language': 'zh-CN,en-US;q=0.8', 
                'Connection': 'keep-alive', 
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,image/wxpic,image/sharpp,image/apng,*/*;q=0.8', 
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; vivo Y53 Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044203 Mobile Safari/537.36 MicroMessenger/6.6.7.1321(0x26060739) NetType/WIFI Language/zh_CN', 
                'Accept-Encoding': 'gzip, deflate'
                }
    """
    profile = FirefoxProfile()
    profile.set_preference("intl.accept_languages", "zh-CN,en-US;q=0.8")
    profile.set_preference("intl.Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,image/wxpic,image/sharpp,image/apng,*/*;q=0.8")
    profile.set_preference("intl.User-Agent", "Mozilla/5.0 (Linux; Android 6.0.1; vivo Y53 Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044203 Mobile Safari/537.36 MicroMessenger/6.6.7.1321(0x26060739) NetType/WIFI Language/zh_CN")
    profile.set_preference("intl.Accept-Encoding'", "gzip, deflate")
    browser = Firefox(firefox_profile=profile)
    return browser


if __name__ == "__main__":
    b = get_browser()
    b.get(url="http://192.168.0.122:8080/welcome")
    pass