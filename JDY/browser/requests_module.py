#  -*- coding: utf-8 -*-
import os
import sys

__project_dir__ = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __project_dir__ not in sys.path:
    sys.path.append(__project_dir__)
from log_module import get_logger
from mail_module import send_mail
import requests
from werkzeug.contrib.cache import RedisCache

"""使用requests的爬取模块,此模块工作有问题"""

logger = get_logger()
cache = RedisCache()


class Crawler:
    """爬取实盘用户信息的类，多例模式"""
    def __init__(self):
        headers = {'Accept': 'text/html',
                   'Accept-Encoding': 'gzip, deflate',
                   'Accept-Charset': 'utf-8',
                   'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
                   'Connection': 'Keep-Alive',
                   'Host': 'zhannei.baidu.com',
                   "Referer": "",
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                 ' (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
        self.ses = requests.Session()
        self.headers = headers
        self.user_name = "849607604@qq.com"
        self.user_password = "Kai3349665"
        self.login_url = "http://office.shengfx888.com"
        self.domain = "office.shengfx888.com"
        self.page_url_base = "http://office.shengfx888.com/report/history_trade?" \
                             "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=" \
                             "&PROFIT_e=&qtype=&CMD=&closetime=&OPEN_TIME_s=" \
                             "&OPEN_TIME_e=&CLOSE_TIME_s=&CLOSE_TIME_e=&T_LOGIN="
        self.user_name2 = "627853018@qq.com"
        self.user_password2 = "XIAOxiao@741"
        self.domain2 = "office.shengfxchina.com:8443"
        self.login_url2 = "https://office.shengfxchina.com:8443/Public/login"
        self.page_url_base2 = "https://office.shengfxchina.com:8443/report/history_trade?" \
                              "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=&PROFIT_e=&qtype=" \
                              "&CMD=&closetime=&OPEN_TIME_s=&OPEN_TIME_e=&CLOSE_TIME_s=" \
                              "&CLOSE_TIME_e=&comm_type=&T_LOGIN="
        self.withdraw_url_base2 = "https://office.shengfxchina.com:8443/deposit/waitin?" \
                                  "layout=yes&weburlredect=1&"  # 2号平台,出金申请

    def login(self, domain: str = None):
        """
        登录
        :param domain:
        :return:
        """
        domain = self.domain if domain is None else domain
        if domain == self.domain:
            url = self.login_url
            user_name = self.user_name
            user_password = self.user_password
        else:
            url = self.login_url2
            user_name = self.user_name2
            user_password = self.user_password2
        ses = self.ses
        self.headers['Host'] = domain
        self.headers['Referer'] = domain
        resp = ses.get(url, headers=self.headers)
        text = resp.text
        print(text)
        check_login_url = "http://office.shengfx888.com/Public/checkLogin"
        args = {"account": self.user_name, "password": self.user_password}
        resp = ses.post(check_login_url, data=args)
        mes = resp.content
        print(mes)
        resp = ses.get("http://office.shengfx888.com/report/history_trade?username=&datascope=&LOGIN="
                       "&TICKET=&PROFIT_s=&PROFIT_e=&qtype=&CMD=&closetime=&OPEN_TIME_s=&OPEN_TIME_e"
                       "=&CLOSE_TIME_s=&CLOSE_TIME_e=&T_LOGIN=", headers=self.headers)
        mes = resp.content
        print(mes)


class CrawlerSingle(Crawler):
    """爬取实盘用户信息的类"""
    def __new__(cls):
        """单例模式设计"""
        if not hasattr(cls, "instance"):
            obj = super(CrawlerSingle, cls).__new__(cls)
            headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
                       'Accept - Encoding': 'gzip, deflate',
                       'Accept-Charset': 'utf-8',
                       'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
                       'Connection': 'Keep-Alive',
                       'Host': 'zhannei.baidu.com',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                     ' (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
            obj.ses = requests.Session()
            obj.headers = headers
            obj.user_name = "849607604@qq.com"
            obj.user_password = "Kai3349665"
            obj.login_url = "http://office.shengfx888.com"
            obj.domain = "office.shengfx888.com"
            obj.page_url_base = "http://office.shengfx888.com/report/history_trade?" \
                                "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=" \
                                "&PROFIT_e=&qtype=&CMD=&closetime=&OPEN_TIME_s=" \
                                "&OPEN_TIME_e=&CLOSE_TIME_s=&CLOSE_TIME_e=&T_LOGIN="
            obj.user_name2 = "627853018@qq.com"
            obj.user_password2 = "XIAOxiao@741"
            obj.domain2 = "office.shengfxchina.com:8443"
            obj.login_url2 = "https://office.shengfxchina.com:8443/Public/login"
            obj.page_url_base2 = "https://office.shengfxchina.com:8443/report/history_trade?" \
                                 "username=&datascope=&LOGIN=&TICKET=&PROFIT_s=&PROFIT_e=&qtype=" \
                                 "&CMD=&closetime=&OPEN_TIME_s=&OPEN_TIME_e=&CLOSE_TIME_s=" \
                                 "&CLOSE_TIME_e=&comm_type=&T_LOGIN="
            obj.withdraw_url_base2 = "https://office.shengfxchina.com:8443/deposit/waitin?" \
                                     "layout=yes&weburlredect=1&"  # 2号平台,出金申请
            cls.instance = obj
        return cls.instance


if __name__ == "__main__":
    p = Crawler()
    p.login()
