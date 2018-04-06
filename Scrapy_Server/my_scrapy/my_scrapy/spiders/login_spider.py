# -*- coding:utf-8 -*-
import os
import scrapy


dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class LoginSpider(scrapy.Spider):
    """登录页面爬虫"""
    name = 'p_2'
    allow_domains = ['office.shengfxchina.com:8443']
    start_urls = ['https://office.shengfxchina.com:8443/Public/login']

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'account': '627853018@qq.com', 'password': 'XIAOxiao@741'},
            callback=self.after_login
        )

    def after_login(self, response):
        file_name = response.url.split("/")[-1]
        parent_path = os.path.join(dir_path, "html")
        if not os.path.exists(parent_path):
            os.makedirs(parent_path)
        file_name = os.path.join(parent_path, "{}.html".format(file_name))
        with open(file_name, 'wb') as f:
            f.write(response.body)