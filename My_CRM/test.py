# -*- coding:utf-8 -*-
import requests
import pyquery


url = "http://yyk.99.com.cn/changning/"

r = requests.get(url)
text = r.text

query = pyquery.PyQuery(text)
lis = query.find(".tablist li>a")
a = pyquery.PyQuery(lis[1])
print(dir(a))