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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import FirefoxProfile
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.webdriver import FirefoxWebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import *
from mail_module import send_mail
from log_module import get_logger
from selenium.webdriver import Chrome
import re
import time
import datetime


"""
https://chromedriver.storage.googleapis.com/index.html?path=2.35/
你也可以自行搜索chromedriver的下载地址,解压是个可执行文件,放到chrome的目录即可.
一般ubuntu下面,chrome的目录是/opt/google/chrome/
"""


logger = get_logger()
# chrome_driver = "/opt/google/chrome/chromedriver"  # chromedriver的路径
chrome_driver = os.path.join(__project_dir__, "resource/chromedriver")  # chromedriver的路径
firefox_driver = os.path.join(__project_dir__, "resource/geckodriver")  # firfoxdriver的路径
os.environ["ChromeDriver"] = chrome_driver  # 必须配置,否则会在execute_script的时候报错.
prev_calendar_date = None  # 上一条日历的日期,专门应对多条合并数据日历的格式(共用日期和国家的td的情况)


def get_browser(headless: bool = True, browser_class: int = 1, init_args: dict = None) -> Firefox:
    """
    获取一个浏览器
    :param headless:
    :param browser_class: 浏览器种类,0是谷歌, 1 是火狐, 服务器端不能使用谷歌
    :param init_args: 初始化字典
    :return:
    """
    """
    selenium安装方法: pip3 install selenium
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
    """
    if browser_class == 1:
        profile = FirefoxProfile()
        profile.set_preference("intl.accept_languages", "zh-cn")
        if isinstance(init_args, dict):
            for k, v in init_args.items():
                profile.set_preference(k, v)
        else:
            pass
        options = FirefoxOptions()
        options.add_argument("--headless")
        if headless:
            try:
                browser = Firefox(firefox_profile=profile, executable_path=firefox_driver, firefox_options=options)
            except Exception as e:
                title = "{} Firefox headless浏览器打开失败".format(datetime.datetime.now())
                content = "错误原因是：{}".format(e)
                send_mail(title=title, content=content)
                logger.exception(e)
                raise e
        else:
            try:
                browser = Firefox(firefox_profile=profile, executable_path=firefox_driver,)
            except Exception as e:
                title = "{} Firefox headless浏览器打开失败".format(datetime.datetime.now())
                content = "错误原因是：{}".format(e)
                send_mail(title=title, content=content)
                logger.exception(e)
                raise e
    else:
        options = ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        if headless:
            options.add_argument("--headless")
            try:
                browser = Chrome(executable_path=chrome_driver, chrome_options=options)
            except Exception as e:
                title = "{} Chrome headless浏览器打开失败".format(datetime.datetime.now())
                content = "错误原因是：{}".format(e)
                send_mail(title=title, content=content)
                logger.exception(e)
                raise e
        else:
            try:
                browser = Chrome(executable_path=chrome_driver, chrome_options=options)
            except Exception as e:
                title = "{} Chrome headless浏览器打开失败".format(datetime.datetime.now())
                content = "错误原因是：{}".format(e)
                send_mail(title=title, content=content)  # 这是我自定义的方法
                logger.exception(e)
                raise e
    return browser


def open_url(url: str = "https://www.taobao.com", browser: (Firefox, Chrome) = None, timeout: int = 10,
             size: str = "1334*1000") -> dict:
    """
    打开浏览器
    :param url:
    :param browser:
    :param timeout:  等待超时,
    :param size: 窗口尺寸,默认1334*1000大小
    :return:
    返回值 是一个字典
    {
      "browser": "Firefox或者Chrome的实例.",
      "wait": "WebDriverWait的实例",
    }
    """
    browser = get_browser(headless=False, browser_class=0) if browser is None else browser
    browser.get(url=url)
    size = size.lower()
    if size == "max":
        browser.maximize_window()
    else:
        if "*" in size:
            width = 1334
            height = 100
            t = size.split("*")[0: 2]
            try:
                width = int(t[0])
                height = int(t[-1])
            except Exception as e:
                print(e)
            finally:
                browser.set_window_rect(x=0, y=0, width=width, height=height)
        else:
            pass
    wait = WebDriverWait(browser, timeout=timeout)
    return {"browser": browser, "wait": wait}


def get_wait(browser: (Firefox, Chrome), timeout: (float, int) = 10) -> WebDriverWait:
    """
    获取一个WebDriverWait对象的实例
    :param browser: 浏览器对象
    :param timeout:  超时
    :return:
    """
    wait = WebDriverWait(browser, timeout=timeout)
    return wait


def get_dom(wait: WebDriverWait, find_type: str = "css", cond: str = '', lot: bool = False, until: bool = True) -> (FirefoxWebElement, WebDriver):
    """
    获取一个页面元素的对象.
    :param wait:
    :param find_type: 定位器,有多种可选 css/css定位 class/类名定位 tag/表签名定位 id/id名定位
    :param cond: 查询条件,因为方法不同而代表不同含义
    :param lot:  返回多个元素还是单个元素?
    :param until:  等待出现还是消失?
    :return:
    主要是
    ec.presence_of_element_located
    ec.presence_of_elements_located
    元素选择器和判定方法(部分)
    title_is： 判断当前页面的title是否完全等于（==）预期字符串，返回布尔值
    title_contains : 判断当前页面的title是否包含预期字符串，返回布尔值
    presence_of_element_located : 获取dom树里dom，并不代表该元素一定可见,返回一个Element对象
    presence_of_all_elements_located : 获取dom树里多个dom，并不代表该元素一定可见,返回一个Element对象
    visibility_of_element_located: 获取可见元素. 返回一个Element对象
    text_to_be_present_in_element: 获取包含指定文本的元素. 返回一个Element对象
    text_to_be_present_in_element_value: 获取包含指定value的元素. 返回一个Element对象
    element_to_be_clickable: 获取可见的可点击的元素. 返回一个Element对象
    """
    locator_map = {
        "id": By.ID,
        "css": By.CSS_SELECTOR,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME,
        "tag_name": By.TAG_NAME,
    }
    find_type = find_type.lower()
    if find_type in locator_map:
        finder = locator_map[find_type]
    else:
        finder = By.CSS_SELECTOR
    locator = (finder, cond)
    if lot:
        expectation = ec.presence_of_all_elements_located
    else:
        expectation = ec.presence_of_element_located
    method = expectation(locator)
    if not until:
        element = wait.until_not(method=method, message="元素仍然存在")
    else:
        element = wait.until(method=method, message="元素未被发现")
    return element


def switch_to_root(b: WebDriver) -> bool:
    """
    切换到根页面
    :param b:
    :return:
    """
    w = WebDriverWait(b, timeout=0.1)
    dom = None
    try:
        dom = get_dom(wait=w, find_type="id", cond="root")
    except TimeoutException as e:
        print(e)
    finally:
        if dom is None:
            b.switch_to.parent_frame()
            switch_to_root(b)
        else:
            return True


def switch_to_news(b: WebDriver) -> bool:
    """
    切换到新闻页
    :param b:
    :return:
    """
    w = WebDriverWait(b, timeout=0.1)
    dom = None
    try:
        dom = get_dom(wait=w, find_type="class", cond="jin-timeline")
    except TimeoutException as e:
        print(e)
    finally:
        if dom is None:
            b.switch_to.parent_frame()
            b.switch_to.frame("jin10_news")
            switch_to_news(b)
        else:
            return True


def switch_to_calendar(b: WebDriver) -> bool:
    """
    切换到日历页
    :param b:
    :return:
    """
    w = WebDriverWait(b, timeout=0.1)
    dom = None
    try:
        dom = get_dom(wait=w, find_type="class", cond="jin-rili")
    except TimeoutException as e:
        print(e)
    finally:
        if dom is None:
            b.switch_to.parent_frame()
            b.switch_to.frame("jin10_calendar")
            switch_to_calendar(b)
        else:
            return True


def parse_news(item, b) -> dict:
    """
    解析一条新闻,现在只解析文本新闻
    :param item: WebElement对象.
    :param b:
    :return:
    """
    id_str = item.get_attribute("id")
    t = datetime.datetime.strptime(id_str, "%Y%m%d%H%M%S%f")
    dom = None
    try:
        dom = item.find_element_by_class_name("is-only-text")
    except NoSuchElementException as e:
        print(e)
    finally:
        if dom is None:
            resp = dict()
        else:
            resp = dict()
            a_time = item.find_element_by_class_name("jin-flash_time").text.strip()
            a_text = dom.text.strip()
            if a_text.startswith("【金十电台】"):
                pass
            else:
                resp['time'] = a_time
                text_3 = a_text if len(a_text.split("。")) < 1 else a_text.split("。")[0]
                resp['text'] = text_3
        return resp


def get_news_data(b: WebDriver, last: datetime.datetime = None) -> list:
    """
    取金10数据的新闻
    :param b:
    :param last: 最后的新闻的time
    :return:
    """
    switch_to_news(b)
    w = WebDriverWait(b, timeout=1)
    items = get_dom(wait=w, cond="#J_flashList .jin-flash_item", lot=True)
    news_list = list()
    for x in items:
        temp = parse_news(x, b)
        if len(temp) > 0:
            news_list.append(temp)
    return news_list


def parse_calendar_data(item) -> dict:
    """
    解析一条数据日历
    :param item: WebElement对象.
    :return:
    """
    # a_time = item.find_element_by_class_name("jin-rili_content-time").text.strip()
    # title = item.find_element_by_class_name("jin-table_alignLeft").text.strip()
    # level = re.findall("\d{2}", item.find_element_by_class_name("jin-star_active").get_attribute("style"))
    tds = item.find_elements_by_tag_name("td")
    print(len(tds))
    if len(tds) == 9:
        a_time = tds[0].text.strip()
        global prev_calendar_date
        prev_calendar_date = a_time
        title = tds[2].text.strip()  #
        level = re.findall("\d{2}", tds[3].find_element_by_class_name("jin-star_active").get_attribute("style"))
        star = 0 if len(level) == 0 else int(int(level[0]) / 20)
        td_prev = tds[4].text.strip()  # 前值
        td_forecast = tds[5].text.strip()  # 预测值
        td_publish = tds[6].text.strip()  # 公布值
        td_effect = tds[7].text.strip()  # 影响
        d = {
            "time": a_time,
            "title": title,
            "star": star,
            "prev": td_prev,
            "forecast": td_forecast,
            "publish": td_publish,
            "effect": td_effect
        }
    else:
        if len(tds) < 7:
            """无数据"""
            print(tds[0].text)
            d = dict()
        else:
            """
            如果是合并多条数据日历的情况.在这多条数据中.
            1. 第一条数据td的长度是9.
            2. 其他数据的td的长度是7
            """
            a_time = prev_calendar_date  # prev_calendar_date是全局变量
            title = tds[0].text.strip()  #
            # level = re.findall("\d{2}", tds[2].get_attribute("style"))
            level = re.findall("\d{2}", tds[1].find_element_by_class_name("jin-star_active").get_attribute("style"))
            star = 0 if len(level) == 0 else int(int(level[0]) / 20)
            td_prev = tds[2].text.strip()  # 前值
            td_forecast = tds[3].text.strip()  # 预测值
            td_publish = tds[4].text.strip()  # 公布值
            td_effect = tds[5].text.strip()  # 影响
            d = {
                "time": a_time,
                "title": title,
                "star": star,
                "prev": td_prev,
                "forecast": td_forecast,
                "publish": td_publish,
                "effect": td_effect
            }
    return d


def get_calendar_data(b: WebDriver, last: datetime.datetime = None) -> (list, tuple):
    """
    取金10数据的日历
    :param b:
    :param last: 最后的日历的time
    :return:
    """
    switch_to_calendar(b)
    w = WebDriverWait(b, timeout=1)
    today_dom = get_dom(wait=w, find_type="class", cond="jin-rili_content-title", lot=False)
    year, month, day = re.findall("\d{2,4}", today_dom.text)
    current_date = "{}-{}-{}".format(year, month, day)
    items = get_dom(wait=w, find_type="css", cond=".jin-rili_body .jin-rili_content", lot=True)
    doms1 = items[0]  # 数据一览
    doms2 = items[1]  # 财经大事
    doms2 = items[2]  # 休市一览
    d1 = list()
    doms1 =doms1.find_elements_by_css_selector(".jin-table_body tr")
    for x in doms1:
        temp = parse_calendar_data(x)
        if len(temp) > 0:
            d1.append(temp)
    """目前只处理数据日历"""
    return d1, current_date


if __name__ == "__main__":
    pass