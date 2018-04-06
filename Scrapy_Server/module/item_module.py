# -*- coding:utf-8 -*-
import sys
import os
"""直接运行此脚本，避免import失败的方法"""
__item_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if __item_dir not in sys.path:
    sys.path.append(__item_dir)
import mongo_db
from log_module import get_logger
import scrapy


ObjectId = mongo_db.ObjectId
DBRef = mongo_db.DBRef
logger = get_logger()


class LoginItem(scrapy.Item):
    """登录"""
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()

    def __init__(self, title, link, desc):
        self.title = title
        self.link = link
        self.desc =desc


class LoginSpider(scrapy.Spider):
    """登录页面爬虫"""
    def __init__(self, name: str, **kwargs):
        """
        name=name, allow_domains=allow_domains, start_urls=start_urls
        """
        super(LoginSpider, self).__init__(name=name, **kwargs)

    def parse(self, response):
        file_name = response.url.split("/")[-2]
        with open(file_name, 'wb') as f:
            f.write(response.body)


if __name__ == "__main__":
    user_name2 = "627853018@qq.com"
    user_password2 = "XIAOxiao@741"
    domain2 = "office.shengfxchina.com:8443"
    login_url2 = "https://office.shengfxchina.com:8443/Public/login"
    login_spider_02 = LoginSpider(name='p_02', allow_domains=[domain2], start_urls=[login_url2])
    print(login_spider_02)
    pass