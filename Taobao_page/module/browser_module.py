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
from mail_module import send_mail
from log_module import get_logger
from selenium.webdriver import Chrome
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
# browser = webdriver.Chrome(chrome_driver)
# wait = WebDriverWait(browser, 10)


def get_browser(headless: bool = True, browser_class: int = 1) -> Firefox:
    """
    获取一个浏览器
    :param headless:
    :param browser_class: 浏览器种类,0是谷歌, 1 是火狐, 服务器端不能使用谷歌
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
    """
    if browser_class == 1:
        profile = FirefoxProfile()
        profile.set_preference("intl.accept_languages", "zh-cn")
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


def login_taobao():
    """
    一个登录淘宝的demo
    :return:
    """
    r = open_url(size='max')
    browser = r['browser']
    wait = r['wait']
    """定位登录按钮"""
    condition = ec.presence_of_all_elements_located((By.CSS_SELECTOR, ".member a"))
    elements = wait.until(condition)
    login_btn = None  # 登录按钮
    for a in elements:
        text = a.text
        if text == "登录":
            login_btn = a
            break
        else:
            pass
    if login_btn is None:
        ms = "没有定位到首页登录按钮"
        raise RuntimeError(ms)
    else:
        time.sleep(0)
        login_btn.click()
        time.sleep(0)
        windows = browser.window_handles
        for window_name in windows:
            browser.switch_to_window(window_name)  # 切换浏览器窗口
            if browser.current_url.startswith("https://login.taobao.com"):
                break
            else:
                pass

        validate_code = None
        flag = False
        while not flag:
            """检查登录二维码是否已扫描成功/消息"""
            try:
                validate_code = get_dom(wait=wait, find_type='id', cond='J_QRCodeImg', until=False)
            except TimeoutException as e:
                print(e)
            except Exception as e:
                raise e
            finally:
                # browser.execute_script("alert('success');")  # 执行脚本的方法
                flag = True if validate_code else False
                time.sleep(1)
        cur_url = browser.current_url
        u = "https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.1.5f0d582dl2KC" \
            "0G&id=568861405922&skuId=3809693454909&areaId=320500&user_id=1971589536&cat_id" \
            "=2&is_b=1&rn=c1299e23dc2113188e8b5c2ff81efc60"
        browser.get(u)
        buy_btn = get_dom(wait=wait, find_type="id", cond='J_LinkBuy')
        buy_btn.click()
        while 1:
            time.sleep(10)


def get_book(url):
    """
    抓取小说
    :param url:
    :return:
    """
    r = open_url(url="http://www.biquge.com.tw/14_14055/9200049.html")
    browser = r['browser']
    wait = r['wait']
    id_str = 'content'
    dom = get_dom(wait=wait, find_type="id", cond=id_str)
    print(dom)



if __name__ == "__main__":
    # login_taobao()
    get_book(url="http://www.biquge.com.tw/14_14055/9200049.html")
    pass