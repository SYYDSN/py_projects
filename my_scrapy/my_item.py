# -*- coding: utf-8 -*-
import scrapy


"""item定义模块"""


class TestItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()