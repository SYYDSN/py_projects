# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import threading
import hashlib,json
ALL_NEWS=[]   #全局变量，用于存放新闻

def news(url='http://www.jin10.com'):
    html=''
    try:
        html = requests.get(url)
        html.encoding='utf-8'
    except:
        print('打开并读取网页页面时出错！')
    soup = BeautifulSoup(html.text,'html5lib')

    news=soup.find_all('table',class_='important-text')
    return news

def handle_news(a_news):
    text=a_news.find_all('td')[2].text
    time=a_news.find_all('td')[1].text
#    print(text,time)
    #link=a_news[0].find_all('a')[0]['href']
    if not text:
        return False
    elif '金十' in text:
        return False
    elif a_news.find_all('td',rowspan='2'):
        return False
    else:
        #print(text,time)
        return({'text':text,'time':time})#,'link':link})

def get_all_news():
    all_news=[]
    a=news('http://www.jin10.com')
    for i in a:
        if handle_news(i):
            all_news.append(handle_news(i))
    global ALL_NEWS
    ALL_NEWS=all_news
    #print(ALL_NEWS)
    #print("i am workging...")
    return all_news

class my_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_thread=False
    def run(self):
        while not self.stop_thread:
            get_all_news()
            time.sleep(10*60)
    def stop(self):
        self.stop_thread=True

my_thread().start()
#print(ALL_NEWS)
#从模块获取实时新闻
def online_news(md5_str=''):#md5_str是客户端的校验md5,用于确认数据是否相同?
    global ALL_NEWS
    md5_raw=hashlib.md5(json.dumps(ALL_NEWS).encode()).hexdigest()
    if md5_str!='' and md5_str.lower()!=md5_raw.lower():
        return {"data":ALL_NEWS.copy()}
    else:
        return {"data":[]}
