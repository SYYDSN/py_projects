#  -*- coding: utf-8 -*-
import os
import scrapy
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
import logging
import scrapy.log


class TorrentItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    size = scrapy.Field()


class SiteSpider(Spider):
    name = "p2_login"
    # allowed_domains = ['office.shengfxchina.com:8443']
    start_urls = ['https://office.shengfxchina.com:8443/Public/login']
    login_flag = False

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formname="loginform",
            formdata={
                'account': '627853018@qq.com', 'password': 'XIAOxiao@741',
                "phoneverify": "", "verify": ""
            },
            callback=self.after_login
        )

    def after_login(self, response):
        """登录成功后的回调方法"""
        filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "a.html")
        with open(filename, 'wb') as f:
            f.write(response.body)
        if response.url.startswith("https://office.shengfxchina.com:8443/Public/login"):
            ms = "登录失败"
            self.log(ms)
            self.log(ms, logging.ERROR)
            self.login_flag = False
            return False
        else:
            ms = "登录成功"
            self.log(ms)
            self.login_flag = True
            return True


    



if __name__ == '__main__':
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
        "Accept-Language": "zh-CN,zh;q=0.9"
    })

    process.crawl(crawler_or_spidercls=SiteSpider)
    process.start()
    pass